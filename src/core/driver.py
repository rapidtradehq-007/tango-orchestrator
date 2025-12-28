import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import ElementClickInterceptedException
from src.config.settings import CONFIG

def init_driver(profile_path, headless):
    options = Options()
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-software-rasterizer")

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1200,800")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
    else:
        options.add_argument("--start-maximized")

    # Uncomment Service(ChromeDriverManager().install())  and comment Service("/usr/bin/chromedriver")  when running orchestrator in mac machine
    # service = Service(ChromeDriverManager().install())
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, CONFIG["DRIVER_WAIT_DELAY"])
    actions = ActionChains(driver)
    return driver, wait, actions

def safe_click(driver, element):
    try:
        time.sleep(CONFIG["SAFE_CLICK"])
        driver.execute_script("arguments[0].click();", element)
    except ElementClickInterceptedException:
        time.sleep(CONFIG["CLICK_RETRY_DELAY"])
        driver.execute_script("arguments[0].click();", element)
