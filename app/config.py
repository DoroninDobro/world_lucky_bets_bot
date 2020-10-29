"""
constants, settings
"""
import json
import os
import secrets
from pathlib import Path
from dateutil import tz

from dotenv import load_dotenv


app_dir: Path = Path(__file__).parent.parent
jsons_dir = app_dir / 'jsons'

load_dotenv(str(app_dir / '.env'))

tz_view = tz.gettz('Europe/Moscow')

PRINT_LOG = "print.log"

BOMZHEG_ID = 46866565
TREE_HOUSE_TRIP_ID = 203288953
SUPERUSERS = {BOMZHEG_ID, TREE_HOUSE_TRIP_ID}

TECH_LOG_CHAT_ID = os.getenv("TECH_LOG_CHAT_ID", -1001171895296)
USER_LOG_CHAT_ID = os.getenv("USER_LOG_CHAT_ID", -1001350461791)
ADMIN_LOG_CHAT_ID = os.getenv("ADMIN_LOG_CHAT_ID", -1001426455516)
WORKERS_CHAT_ID = os.getenv("WORKERS_CHAT_ID", -1001363065436)

allow_list_path = jsons_dir / 'allow_list.json'
ENABLE_ALLOW_LIST = bool(int(os.getenv("ENABLE_ALLOW_LIST", default=0)))

admin_list_path = jsons_dir / 'admins_list.json'
with open(admin_list_path) as f:
    admins_list = set(json.load(f))

BOT_TOKEN = os.getenv("BOT_TOKEN")
secret_str = secrets.token_urlsafe(16)  # for webhook path

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PORT = os.getenv("WEBHOOK_PORT", default=443)
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", default='/bot/')
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_PATH}"

LISTEN_IP = os.getenv("LISTEN_IP", default='0.0.0.0')
LISTEN_PORT = int(os.getenv("LISTEN_PORT", default=3000))

DB_TYPE = os.getenv("DB_TYPE", default='sqlite')
LOGIN_DB = os.getenv("LOGIN_DB")
PASSWORD_DB = os.getenv("PASSWORD_DB")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_PATH = os.getenv("DB_PATH", default=app_dir / "db_data" / "bot.db")


PROG_NAME = "world lucky bets bot"
PROG_DESC = (
    "This program is a Python 3.9+ script. The script launches a bot in Telegram,"
    " allowing ..."
)
PROG_EP = "by bomzheg"
DESC_POLLING = "Run tg bot with polling. Default use WebHook"
