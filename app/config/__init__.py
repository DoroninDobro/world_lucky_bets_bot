"""
constants, settings
"""
import json
import os
import secrets
from pathlib import Path

from dateutil import tz
from dotenv import load_dotenv
import yaml
from yaml import SafeLoader

from .currency import load_currency
from .db_config import DBConfig

app_dir: Path = Path(__file__).parent.parent.parent
config_path = app_dir / 'config'
jsons_dir = config_path / 'jsons'
CURRENT_BOT = os.getenv("BOT_NAME", default="")

load_dotenv(str(config_path / f"{CURRENT_BOT}.env"))

tz_view = tz.gettz('Europe/Moscow')

PRINT_LOG = f"{CURRENT_BOT}.print.log"

ENABLE_LOGGING_MIDDLEWARE = bool(int(os.getenv("ENABLE_LOGGING_MIDDLEWARE", default=1)))

BOMZHEG_ID = 46866565
TREE_HOUSE_TRIP_ID = 203288953
SUPERUSERS = {BOMZHEG_ID, TREE_HOUSE_TRIP_ID}

TECH_LOG_CHAT_ID = int(os.getenv("TECH_LOG_CHAT_ID", -1001171895296))
USER_LOG_CHAT_ID = int(os.getenv("USER_LOG_CHAT_ID", -1001350461791))
ADMIN_LOG_CHAT_ID = int(os.getenv("ADMIN_LOG_CHAT_ID", -1001426455516))
WORKERS_CHAT_ID = int(os.getenv("WORKERS_CHAT_ID", -1001243606983))
ADMINS_WITHOUT_USERNAMES_LOG_CHAT_ID = int(os.getenv("ADMINS_WITHOUT_USERNAMES_LOG_CHAT_ID", -1001227120186))

allow_list_path = jsons_dir / CURRENT_BOT / 'allow_list.json'
ENABLE_ALLOW_LIST = bool(int(os.getenv("ENABLE_ALLOW_LIST", default=0)))

admin_list_path = jsons_dir / CURRENT_BOT / 'admins_list.json'
with open(admin_list_path) as f:
    admins_list = set(json.load(f))

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise EnvironmentError("You have to specify BOT_TOKEN environment")
OER_TOKEN = os.getenv("OER_TOKEN")

with (config_path / "currency.yml").open("r", encoding="utf-8") as f:
    currencies = load_currency(yaml.load(f, SafeLoader))


secret_str = secrets.token_urlsafe(16)  # for webhook path

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PORT = os.getenv("WEBHOOK_PORT", default=443)
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", default=f'/{CURRENT_BOT}/')
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_PATH}"

LISTEN_IP = os.getenv("LISTEN_IP", default='0.0.0.0')
LISTEN_PORT = int(os.getenv("LISTEN_PORT", default=3000))

db_config = DBConfig().init_from_environment()


PROG_NAME = "world lucky bets bot"
PROG_DESC = "This program is a Python 3.9+ script. The script launches a bot in Telegram"
PROG_EP = "by bomzheg"
DESC_POLLING = "Run tg bot with polling. Default use WebHook"
BASE_CURRENCY = "EUR"
