import imaplib
import email
import re
from src.config.settings import CONFIG

def get_latest_otp():
    mail = imaplib.IMAP4_SSL(CONFIG["IMAP_SERVER"])
    mail.login(CONFIG["EMAIL"], CONFIG["PASSWORD"])
    mail.select("inbox")
    _, data = mail.search(None, f'FROM "{CONFIG["FROM_EMAIL"]}"')
    if not data[0]:
        return None
    msg_id = data[0].split()[-1]
    _, msg_data = mail.fetch(msg_id, "(RFC822)")
    msg = email.message_from_bytes(msg_data[0][1])
    return re.findall(r"\b\d{4}\b", msg["Subject"])[0]
