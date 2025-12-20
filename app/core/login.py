import uuid
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from app.core.driver import init_driver, safe_click
from app.core.otp import get_latest_otp
from app.config.settings import CONFIG

login_profile_path = CONFIG["LOGIN_PROFILE_PATH"] + f"_{uuid.uuid4().hex}"

def login():
    driver, wait, _ = init_driver(login_profile_path, headless=False)
    driver.get(CONFIG["LOGIN_URL"])
    time.sleep(CONFIG["LOGIN_PAGE_LOAD_DELAY"])

    email_btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//button[.//span[text()="Continue with Email"]]')))
    safe_click(driver, email_btn)

    email_input = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, 'input[data-testid="login-with-email-input-email"]')))
    email_input.send_keys(CONFIG["EMAIL"])

    submit = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, 'button[data-testid="login-with-email-continue-button"]')))
    safe_click(driver, submit)

    time.sleep(CONFIG["OTP_EMAIL_WAIT_DELAY"])
    otp = get_latest_otp()

    if otp:
        for i, d in enumerate(otp):
            field = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, f'input[data-testid="digit-input-{i}"]')))
            field.send_keys(d)
            time.sleep(CONFIG["PIN_DIGIT_ENTER_DELAY"])

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="avatar"]')))
    driver.quit()
