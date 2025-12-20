import os

BASE_DIR = os.getcwd()

CONFIG = {
    "PIPELINE_DELAY_BETWEEN_STEPS_SECONDS": 120,
    "EMAIL": os.getenv("EMAIL"),
    "PASSWORD": os.getenv("PASSWORD"),
    "BASE_URL": "https://tango.me/",
    "IMAP_SERVER": "imap.gmail.com",
    "FROM_EMAIL": "info@transactional.tango.me",
    "LOGIN_URL": "https://tango.me/welcome",
    "SECTION_URL": "https://tango.me/live/nearby",
    "LOGIN_PAGE_LOAD_DELAY": 3,
    "OTP_EMAIL_WAIT_DELAY": 10,
    "PIN_DIGIT_ENTER_DELAY": 0.2,
    "DRIVER_WAIT_DELAY": 15,
    "SCROLL_DELAY": 1,
    "FAILED_SCROLL_RETRY_DELAY": 0.5,
    "MAX_IDLE_SCROLLS": 5,
    "SAFE_CLICK": 0.2,
    "CLICK_RETRY_DELAY": 1,
    "TYPING_TIME": 0.1,
    "BROADCASTER_URL_LOAD_WAIT": 3,
    "USERNAME_APPEARANCE_DELAY": 1,
    "COINS_THRESHOLD": 99,
    "VIEWER_THRESHOLD": 3,
    "MAX_SENDERS": 99999,
    "MAX_WORKERS": 5,
    "PROCESS_BROADCASTER_MAX_RETRIES": 3,
    "PROCESS_URL_MAX_RETRIES": 3,
    "CHAT_WAIT_TIME": 3,
    "ACTION_DELAY": 2,
    "DELETE_DELAY": 2,
    "POLL_TIME": 0.2,
    "MESSAGE_THRESHOLD_TO_SKIP_CHAT": 2,
    "PROFILE_LOAD_DELAY": 3,
    "ROOT_PATH_OF_PROFILES": os.path.join(BASE_DIR, "app/data/runtime/profiles"),
    "LOGIN_PROFILE_PATH": os.path.join(BASE_DIR, "app/data/runtime/profiles/log_in"),
    "OUTPUT_PATH": os.path.join(BASE_DIR, "app/data/local_storage"),
    "IMAGE_PATH": os.path.join(BASE_DIR, "app/resources/RateCard.png"),
    "CUSTOMER_TABLE_NAME": "customers",
    "MESSAGE_TEXT":
"""
₹500 - 1000 Coins ⚡
₹1000 - 2000 Coins ⚡
₹2000 - 4000 Coins ⚡
₹5000 - 10000 Coins ⚡
₹10000 - 20000 Coins ⚡
₹20000 - 40000 Coins ⚡
₹50000 - 100000 Coins ⚡
₹100000 - 200000 Coins ⚡

Hey buddy,
I am a Tango Official Coin Reseller and I sell Tango coins at ₹0.5 per coin. 
For prices in other currencies, please DM me directly. 
Indian customers can pay easily via UPI or scanners, while non-Indians can make payments through Crypto or the Remitly app. 
If you’re planning to purchase in bulk, feel free to contact me directly for better rates.
"""
}
