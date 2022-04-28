"""
constants, settings
"""
import os
import secrets
import yaml

from app.models.config import Config
from app.models.config.main import Paths
from .app_config import load_app_config
from .bot import load_bot_config
from .currency import load_currency, load_currencies
from .db_config import load_db_config


def load_config(paths: Paths) -> Config:
    with (paths.config_path / "config.yml").open() as f:
        dct_config = yaml.safe_load(f)
    return Config(
        paths=paths,
        db=load_db_config(dct_config["db"]),
        currencies=load_currencies(dct_config["currencies"]),
        bot=load_bot_config(dct_config["bot"]),
        app=load_app_config(dct_config["app"]),
    )


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
