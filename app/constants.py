import os
import secrets

secret_str = secrets.token_urlsafe(16)  # for webhook path

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PORT = os.getenv("WEBHOOK_PORT", default=443)
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", default='/')
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_PATH}"

LISTEN_IP = os.getenv("LISTEN_IP", default='0.0.0.0')
LISTEN_PORT = int(os.getenv("LISTEN_PORT", default=3000))

PROG_NAME = "world lucky bets bot"
PROG_DESC = "This program is a Python 3.9+ script. The script launches a bot in Telegram"
PROG_EP = "by bomzheg"
DESC_POLLING = "Run tg bot with polling. Default use WebHook"
BASE_CURRENCY = "EUR"
