import uuid
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from src.core.driver import init_driver, safe_click
from src.core.otp import get_latest_otp
from src.config.settings import CONFIG
from src.utils.logger import setup_logger

login_profile_path = CONFIG["LOGIN_PROFILE_PATH"] + f"_{uuid.uuid4().hex}"

def login():
    setup_logger()
    logging.info("Performing login")
    driver, wait, _ = init_driver(login_profile_path, headless=False)
    logging.info("Opening login page: %s", CONFIG["LOGIN_URL"])
    driver.get(CONFIG["LOGIN_URL"])
    time.sleep(CONFIG["LOGIN_PAGE_LOAD_DELAY"])

    logging.info("Clicking 'Continue with Email' button")
    email_btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//button[.//span[text()="Continue with Email"]]')))
    safe_click(driver, email_btn)

    logging.info("Entering email")
    email_input = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, 'input[data-testid="login-with-email-input-email"]')))
    email_input.send_keys(CONFIG["EMAIL"])

    logging.info("Submitting email")
    submit = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, 'button[data-testid="login-with-email-continue-button"]')))
    safe_click(driver, submit)

    logging.info("Waiting for OTP email")
    time.sleep(CONFIG["OTP_EMAIL_WAIT_DELAY"])
    otp = get_latest_otp()

    logging.info("Entering OTP")
    if otp:
        for i, d in enumerate(otp):
            field = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, f'input[data-testid="digit-input-{i}"]')))
            field.send_keys(d)
            time.sleep(CONFIG["PIN_DIGIT_ENTER_DELAY"])

    logging.info("Waiting for successful login (avatar presence)")
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="avatar"]')))
    logging.info("Login successful")
    driver.quit()
