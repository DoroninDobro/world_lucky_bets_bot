"""
constants, settings
"""
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

