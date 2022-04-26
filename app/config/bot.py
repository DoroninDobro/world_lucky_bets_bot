from app.models.config.main import BotConfig


def load_bot_config(dct: dict) -> BotConfig:
    return BotConfig(
        token=dct["token"],
        log_chat=dct["log_chat"],
        superusers=dct["superusers"],
    )
