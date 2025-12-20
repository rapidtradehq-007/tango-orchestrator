import time
import logging
from selenium.webdriver.common.by import By
from app.config.settings import CONFIG
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
)

def safe_click(driver, element):
    """
    JS-based click with retry.
    """
    try:
        time.sleep(CONFIG["SAFE_CLICK"])
        driver.execute_script("arguments[0].click();", element)
    except ElementClickInterceptedException:
        logging.warning("Click intercepted, retrying...")
        time.sleep(CONFIG["CLICK_RETRY_DELAY"])
        driver.execute_script("arguments[0].click();", element)


def scroll_page(driver, css_selector):
    """
    Scrolls to the last visible element.
    """
    for _ in range(3):
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, css_selector)
            if not elements:
                logging.warning("No elements found to scroll.")
                return
            last_el = elements[-1]
            driver.execute_script("arguments[0].scrollIntoView();", last_el)
            return
        except Exception as e:
            logging.warning(
                f"Scroll attempt failed due to {type(e).__name__}, retrying..."
            )
            time.sleep(CONFIG["FAILED_SCROLL_RETRY_DELAY"])

    logging.error("Failed to scroll after multiple retries — skipping.")


def load_all_cards(driver, css_selector):
    """
    Keeps scrolling until card count stabilizes.
    """
    last_count = 0
    idle_count = 0
    max_idle = CONFIG["MAX_IDLE_SCROLLS"]

    while idle_count < max_idle:
        scroll_page(driver, css_selector)
        time.sleep(CONFIG["SCROLL_DELAY"])

        current_count = len(driver.find_elements(By.CSS_SELECTOR, css_selector))
        if current_count == last_count:
            idle_count += 1
        else:
            idle_count = 0
            last_count = current_count


def handle_notification_modal(driver, wait):
    """
    Declines browser notification modal if present.
    """
    try:
        modal_decline = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[data-testid="permissionRequest-modal-declineButton"]')
            )
        )
        safe_click(driver, modal_decline)
        logging.info("Notification modal declined.")
    except TimeoutException:
        logging.debug("No notification modal appeared.")


def close_modal(driver, wait):
    """
    Closes profile modal.
    """
    close_btn = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'button[data-testid="close-icon"]')
        )
    )
    driver.execute_script("arguments[0].click();", close_btn)
    wait.until(
        EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, 'button[data-testid="close-icon"]')
        )
    )
