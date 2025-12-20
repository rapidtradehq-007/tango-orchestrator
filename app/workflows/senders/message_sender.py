import time
import logging
import threading
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor, wait as future_wait, ALL_COMPLETED
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from app.config.settings import CONFIG
from app.core.driver import init_driver
from app.core.login import login, login_profile_path
from app.core.profiles import clone_profile, cleanup_driver
from app.storage.local_storage import get_column, get_data
from app.utils.interaction_utils import safe_click
from app.utils.logger import setup_logger
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
)

# =========================
# GLOBAL STATE
# =========================
sent_messages_urls = set()
sent_messages_urls_lock = threading.Lock()
clone_profile_lock = threading.Lock()

def follow_if_present(driver, profile_url):
    follow_buttons = driver.find_elements(
        By.XPATH, "//button[@data-testid='follow']"
    )

    if follow_buttons:
        try:
            safe_click(driver, follow_buttons[0])
            time.sleep(CONFIG["ACTION_DELAY"])
            logging.info(f"Followed {profile_url}")
        except WebDriverException as e:
            logging.warning(f"Follow button present but click failed: {e}")
    else:
        logging.info("Follow button not present — continuing")

def try_navigate_to_chat_from_stream(driver, wait, url, profile_url):
    try:
        logging.info(f"Redirected to stream url ({url}) for profile url ({profile_url}) – clicking avatar now..." )
        avatar_div = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-testid='avatar']"))
        )
        safe_click(driver, avatar_div)
        time.sleep(CONFIG["ACTION_DELAY"])
        follow_if_present(driver, profile_url)

        return True
    except TimeoutException:
        logging.warning(
            f"Couldn’t find expected elements on stream url: {url}."
        )
    except Exception as e:
        logging.error(f"Error navigating from stream url: {url}")

    return False


def is_stream_unavailable(driver, url):
    try:
        unavailable_view = driver.find_element(
            By.CSS_SELECTOR, "div[data-testid='stream-unavailable-view']"
        )
        if unavailable_view:
            logging.warning(f"Skipping '{url}' because stream is unavailable.")
            return True
    except:
        pass
    return False


def open_profile(driver, wait, url):
    logging.info(f"Opening profile URL: {url}")
    driver.get(url)
    time.sleep(CONFIG["PROFILE_LOAD_DELAY"])

    current_url = driver.current_url
    if current_url.startswith("https://tango.me/stream"):
        if is_stream_unavailable(driver, current_url) or not try_navigate_to_chat_from_stream(
                driver, wait, current_url, url
        ):
            return False

    return True


# =============
# CHAT HANDLING
# =============
def handle_existing_messages(driver, wait, actions, url):
    end_time = time.time() + CONFIG["CHAT_WAIT_TIME"]
    messages = []

    while time.time() < end_time:
        try:
            messages = driver.find_elements(By.CSS_SELECTOR, "div.QiDQA")
            if messages:
                break
        except Exception:
            pass
        time.sleep(CONFIG["POLL_TIME"])

    if len(messages) > CONFIG["MESSAGE_THRESHOLD_TO_SKIP_CHAT"]:
        logging.info(f"Skipping {url} due to existing messages, count={len(messages)}")
        return False

    ignored_messages = set()

    while True:
        try:
            messages = [
                m
                for m in driver.find_elements(By.CSS_SELECTOR, "div.QiDQA")
                if m not in ignored_messages
            ]
            if not messages:
                break

            msg = messages[-1]
            driver.execute_script("arguments[0].scrollIntoView(true);", msg)
            actions.context_click(msg).perform()

            delete_option = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "div[data-testid='chat-message-menu-option-delete']")
                )
            )
            safe_click(driver, delete_option)

            modal_root = wait.until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "div[data-testid='chat-delete-message-confirm-for-all-moodal']",
                    )
                )
            )

            try:
                delete_checkbox = modal_root.find_element(
                    By.CSS_SELECTOR,
                    "input[data-testid='chat-delete-message-confirm-for-all']",
                )
                safe_click(driver, delete_checkbox)
            except Exception:
                cancel_btn = modal_root.find_element(
                    By.CSS_SELECTOR,
                    "button[data-testid='chat-delete-message-confirm-modal-cancel']",
                )
                safe_click(driver, cancel_btn)
                ignored_messages.add(msg)
                continue

            delete_btn = modal_root.find_element(
                By.CSS_SELECTOR,
                "button[data-testid='chat-delete-message-confirm-modal-delete']",
            )
            safe_click(driver, delete_btn)
            time.sleep(CONFIG["DELETE_DELAY"])

        except Exception:
            break

    return True


# ===============
# MESSAGE SENDING
# ===============
def send_image(driver, wait, url):
    try:
        file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
        file_input.send_keys(CONFIG["IMAGE_PATH"])

        send_image_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='send']")))
        safe_click(driver, send_image_btn)

    except Exception as e:
        logging.error(f"Error uploading image for {url}: {e}")
        raise
    finally:
        time.sleep(CONFIG["ACTION_DELAY"])


def send_message(driver, wait, url):
    try:
        textarea = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "textarea[data-testid='textarea']")
            )
        )
        textarea.clear()

        lines = CONFIG["MESSAGE_TEXT"].splitlines()
        for i, line in enumerate(lines):
            textarea.send_keys(line)
            if i != len(lines) - 1:
                textarea.send_keys(Keys.SHIFT, Keys.ENTER)
                time.sleep(CONFIG["TYPING_TIME"])

        send_btn = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-testid='chat-send-message-button']")
            )
        )
        safe_click(driver, send_btn)

    except Exception as e:
        logging.error(f"Error sending message to {url}: {e}")
        raise
    finally:
        time.sleep(CONFIG["ACTION_DELAY"])


# ======
# WORKER
# ======
def process_urls_worker(urls_chunk, worker_id):
    with clone_profile_lock:
        profile_path = clone_profile(login_profile_path, CONFIG["ROOT_PATH_OF_PROFILES"])

    driver, wait, actions = init_driver(profile_path, headless=True)
    logging.info(f"[Worker {worker_id}] Started with {len(urls_chunk)} URLs")

    try:
        for idx, url in enumerate(urls_chunk, start=1):
            logging.info( f"[Worker {worker_id}] [Processing {idx}/{len(urls_chunk)}: {url}]")

            if not open_profile(driver, wait, url):
                continue

            retries = 0
            while retries < CONFIG["PROCESS_URL_MAX_RETRIES"]:
                try:
                    msg_btn = wait.until(
                        EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, "a[data-testid='chat']")
                        )
                    )
                    safe_click(driver, msg_btn)

                    if not handle_existing_messages(driver, wait, actions, url):
                        break

                    send_image(driver, wait, url)
                    send_message(driver, wait, url)

                    with sent_messages_urls_lock:
                        sent_messages_urls.add(url)
                        logging.info(f"Message sent successfully to sender: {url}")

                    break

                except WebDriverException:
                    retries += 1
                    with clone_profile_lock:
                        clone_path = clone_profile(login_profile_path, CONFIG["ROOT_PATH_OF_PROFILES"])
                    cleanup_driver(driver, profile_path)
                    driver, wait, actions = init_driver(clone_path, headless=True)
                    profile_path = clone_path

                except Exception as e:
                    logging.error( f"Error processing {url}: {e}")
                    break

    finally:
        cleanup_driver(driver, profile_path)
        logging.info(f"[Worker {worker_id}] Finished.")

# ==========
# ENTRYPOINT
# ==========
def message_sender():
    start_time = time.time()
    setup_logger()
    login()

    input_urls = list(get_column(get_data(CONFIG["CUSTOMER_TABLE_NAME"]), "url"))
    chunks = [
        input_urls[i :: CONFIG["MAX_WORKERS"]]
        for i in range(CONFIG["MAX_WORKERS"])
    ]

    try:
        with ThreadPoolExecutor(
                max_workers=CONFIG["MAX_WORKERS"]
        ) as executor:
            futures = {
                executor.submit(process_urls_worker, chunks[i], i): i
                for i in range(CONFIG["MAX_WORKERS"])
            }
            future_wait(futures, return_when=ALL_COMPLETED)

    finally:
        with sent_messages_urls_lock:
            sent_count = len(sent_messages_urls)

        total = int(time.time() - start_time)
        logging.info(f"Messages sent successfully: {sent_count}")
        logging.info(f"Script Execution Time: {total//3600:02d}:{(total%3600)//60:02d}:{total%60:02d}")


message_sender()
