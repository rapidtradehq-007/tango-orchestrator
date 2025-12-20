import time
import logging
import threading

from app.config.settings import CONFIG
from app.core.driver import init_driver
from app.core.login import login, login_profile_path
from app.core.profiles import clone_profile, cleanup_driver
from app.storage.local_storage import save_data
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, wait as future_wait, ALL_COMPLETED
from selenium.common.exceptions import WebDriverException
from app.utils.logger import setup_logger
from app.utils.interaction_utils import (
    safe_click,
    load_all_cards,
    handle_notification_modal,
    close_modal,
)

# =========================
# GLOBAL STATE
# =========================
broadcaster_table = []
broadcaster_keys = set()
broadcaster_table_lock = threading.Lock()

sender_table = []
sender_keys = set()
sender_table_lock = threading.Lock()

clone_profile_lock = threading.Lock()

# =========================
# CARD EXTRACTION
# =========================
def extract_cards(driver):
    cards = driver.find_elements(By.CSS_SELECTOR, "div.MN99i")
    data = []

    for el in cards:
        try:
            stream_url = el.find_element(By.CSS_SELECTOR, "a.vxciX").get_attribute("href")
        except:
            stream_url = None

        try:
            image = el.find_element(By.CSS_SELECTOR, "img.iMFfA").get_attribute("src")
        except:
            image = None

        try:
            name = el.find_element(By.CSS_SELECTOR, '[data-testid="name"] span').text.strip()
        except:
            name = None

        try:
            diamond_count = el.find_element(
                By.CSS_SELECTOR, '[data-testid="points"] span'
            ).text.strip()
        except:
            diamond_count = None

        try:
            viewer_count = el.find_element(By.CSS_SELECTOR, ".JgGPM span").text.strip()
        except:
            viewer_count = None

        data.append(
            {
                "stream_url": stream_url,
                "image_url": image,
                "name": name,
                "diamond_count": diamond_count,
                "viewer_count": viewer_count,
            }
        )

    return data


# =========================
# STREAM PAGE PROCESSING
# =========================
def process_stream_page(section_url):
    with clone_profile_lock:
        profile_path = clone_profile(login_profile_path, CONFIG["ROOT_PATH_OF_PROFILES"])

    driver, wait, _ = init_driver(profile_path, headless=True)

    try:
        driver.get(section_url)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.MN99i")))

        handle_notification_modal(driver, wait)
        logging.info(f"Scrolling broadcasters...")
        load_all_cards(driver, "div.MN99i")
        cards = extract_cards(driver)
        logging.info(f"Total broadcasters loaded: {len(cards)}")

    finally:
        cleanup_driver(driver, profile_path)

    unique_broadcasters = {bc["stream_url"]: bc for bc in cards if bc.get("stream_url")}
    broadcasters = list(unique_broadcasters.values())

    if not broadcasters:
        logging.info("No broadcasters found in this section.")
        return

    chunks = [
        broadcasters[i :: CONFIG["MAX_WORKERS"]]
        for i in range(CONFIG["MAX_WORKERS"])
    ]

    with ThreadPoolExecutor(max_workers=CONFIG["MAX_WORKERS"]) as executor:
        futures = {
            executor.submit(process_broadcaster_batch, chunk, i): i
            for i, chunk in enumerate(chunks)
        }
        future_wait(futures.keys(), return_when=ALL_COMPLETED)


# ============================
# BROADCASTER BATCH PROCESSING
# ============================
def process_broadcaster_batch(broadcasters, worker_id):
    with clone_profile_lock:
        profile_path = clone_profile(login_profile_path, CONFIG["ROOT_PATH_OF_PROFILES"])

    driver, wait, _ = init_driver(profile_path, headless=True)
    logging.info(f"[Worker {worker_id}] Started with {len(broadcasters)} broadcasters")

    try:
        for idx, bc in enumerate(broadcasters, start=1):
            logging.info( f"[Worker {worker_id}] [Processing {idx}/{len(broadcasters)} broadcaster]")

            retries = 0
            while retries < CONFIG["PROCESS_BROADCASTER_MAX_RETRIES"]:
                try:
                    process_single_broadcaster(driver, wait, bc)
                    if len(sender_table) >= CONFIG["MAX_SENDERS"]:
                        return

                    break

                except WebDriverException:
                    retries += 1
                    with clone_profile_lock:
                        clone_path = clone_profile(login_profile_path, CONFIG["ROOT_PATH_OF_PROFILES"])
                    cleanup_driver(driver, profile_path)
                    driver, wait, _ = init_driver(clone_path, headless=True)
                    profile_path = clone_path

                except Exception as e:
                    logging.error(f"[Worker {worker_id}] Unretryable error: {e}")
                    break

    finally:
        cleanup_driver(driver, profile_path)
        logging.info(f"[Worker {worker_id}] Finished.")

# =============================
# SINGLE BROADCASTER PROCESSING
# =============================
def process_single_broadcaster(driver, wait, bc):
    try:
        viewer_count = int("".join(filter(str.isdigit, bc.get("viewer_count", "0"))))
    except:
        viewer_count = 0

    if viewer_count < CONFIG["VIEWER_THRESHOLD"]:
        return

    driver.get(bc["stream_url"])
    time.sleep(CONFIG["BROADCASTER_URL_LOAD_WAIT"])

    try:
        unavailable_view = driver.find_element(
            By.CSS_SELECTOR, 'div[data-testid="stream-unavailable-view"]'
        )
        if unavailable_view:
            return
    except:
        pass

    save_broadcaster_profile(driver, wait, bc)
    extract_gifters(driver, wait, bc)


# ================
# SAVE BROADCASTER
# ================
def save_broadcaster_profile(driver, wait, bc):
    broadcaster_url = None
    crown_info = None

    try:
        broadcaster_info = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-testid="streamer-info"]'))
        )
        safe_click(driver, broadcaster_info)

        username_span = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span.mMHa5.Y3IN4.ruFUq'))
        )
        time.sleep(CONFIG["USERNAME_APPEARANCE_DELAY"])

        broadcaster_url = CONFIG["BASE_URL"] + username_span.text[1:]

        try:
            crown_span = driver.find_element(By.CSS_SELECTOR, 'div._fS99 span._H0HX')
            crown_info = crown_span.text.strip()
        except:
            pass

        close_modal(driver, wait)

    except Exception as e:
        logging.error(f"Failed to fetch profile for broadcaster '{bc.get('name')}' -> {e}")
        return

    bc["url"] = broadcaster_url
    bc["crown_info"] = crown_info

    with broadcaster_table_lock:
        if broadcaster_url not in broadcaster_keys:
            broadcaster_table.append(bc)
            broadcaster_keys.add(broadcaster_url)
            logging.info(f"Saved broadcaster #{len(broadcaster_table)}: {broadcaster_url} -> Viewer Count: {bc.get('viewer_count')}")

# ===============
# PROCESS GIFTERS
# ===============
def extract_gifters(driver, wait, bc):
    try:
        logging.info(f"Opening gifters tab for broadcaster: {bc.get('url')}")
        gifters_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-testid="top-gifters"]')))
        safe_click(driver, gifters_tab)

        logging.info(f"Scrolling gifters list for broadcaster: {bc.get('url')}")
        load_all_cards(driver, ".ZNbUV")
        gifters = driver.find_elements(By.CSS_SELECTOR, '[data-testid="top-gifters-list"] .ZNbUV')
        logging.info(f"Total gifters loaded: {len(gifters)} for broadcaster: {bc.get('url')}")

        for idx, el in enumerate(gifters, start=1):
            logging.debug(f"Processing gifter {idx}/{len(gifters)} for broadcaster: {bc.get('url')}")
            process_single_sender(driver, wait, el, bc.get("url"))

    except Exception as e:
        logging.warning(f"Gifters loading failed for broadcaster {bc.get('name')} -> {e}")

# ===========
# SAVE GIFTER
# ===========
def process_single_sender(driver, wait, el, broadcaster_url):
    sender = {
        "name": None,
        "image_url": None,
        "coins_gifted": 0,
        "url": None,
        "broadcaster_url": broadcaster_url,
        "crown_info": None,
    }

    try:
        sender["name"] = el.find_element(
            By.CSS_SELECTOR, '[data-testid="name"] span'
        ).text.strip()
    except:
        pass

    try:
        coins_text = el.find_element(
            By.CSS_SELECTOR, '[data-testid="gifted-coins-number"]'
        ).text
        sender["coins_gifted"] = int("".join(filter(str.isdigit, coins_text)))
    except:
        pass

    if sender["name"] and sender["coins_gifted"] >= CONFIG["COINS_THRESHOLD"]:
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", el)
            safe_click(driver, el)

            username_span = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'span.mMHa5.Y3IN4.ruFUq'))
            )
            time.sleep(CONFIG["USERNAME_APPEARANCE_DELAY"])
            sender["url"] = CONFIG["BASE_URL"] + username_span.text[1:]

            try:
                crown_span = driver.find_element(By.CSS_SELECTOR, 'div._fS99 span._H0HX')
                sender["crown_info"] = crown_span.text.strip()
            except:
                pass

            close_modal(driver, wait)

            with sender_table_lock:
                if sender["url"] not in sender_keys:
                    sender_table.append(sender)
                    sender_keys.add(sender["url"])
                    logging.info(f"Saved sender #{len(sender_table)}: {sender.get('url')} "
                                 f" -> Gifted {sender.get('coins_gifted')} coins")

        except Exception as e:
            logging.error(f"Failed data fetch for sender {sender.get('name')} -> {e}")

# ==========
# ENTRYPOINT
# ==========
def customer_collector():
    start_time = time.time()
    setup_logger()
    login()

    try:
        process_stream_page(CONFIG["SECTION_URL"])
    finally:
        save_data(CONFIG["CUSTOMER_TABLE_NAME"], [row for table in [broadcaster_table, sender_table] for row in table])
        total = int(time.time() - start_time)
        logging.info(f"Script Execution Time: {total//3600:02d}:{(total%3600)//60:02d}:{total%60:02d}")

customer_collector()
