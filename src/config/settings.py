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
    "ROOT_PATH_OF_PROFILES": os.path.join(BASE_DIR, "data", "runtime", "profiles"),
    "LOGIN_PROFILE_PATH": os.path.join(BASE_DIR, "data", "runtime", "profiles", "log_in"),
    "OUTPUT_PATH": os.path.join(BASE_DIR, "data", "local_storage"),
    "IMAGE_PATH": os.path.join(BASE_DIR, "src", "resources", "RateCard.png"),
    "CUSTOMER_TABLE_NAME": "customers",
    "SKIP_PROFILE_URLS": [
        "https://tango.me/divs001"
    ],
    "MESSAGE_TEXT":
"""
₹489 - 1000 Coins ⚡
₹979 - 2000 Coins ⚡
₹1469 - 3000 Coins ⚡
₹2449 - 5000 Coins ⚡
₹4899 - 10000 Coins ⚡
₹9799 - 20000 Coins ⚡
₹12249 - 25000 Coins ⚡
₹14699 - 30000 Coins ⚡

Hey buddy 

I’m a Tango Official Coin Reseller, offering the lowest coin prices in the market.
My rates are transparent, competitive, and designed for regular senders as well as bulk buyers.

-  Market-Lowest Rates
-  No Hidden Charges
-  Instant Transfer

Payment options:
Indian customers: UPI / QR scanner or Bank Transfer
International customers: Crypto or Remitly

For bulk purchases or other currencies, DM me directly for better personalized rates.

Compare prices once — you’ll know why I’m the cheapest.
"""
}
