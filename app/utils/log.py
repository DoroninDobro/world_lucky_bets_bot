from loguru import logger

from app.models.config import Config


def setup(config: Config):
    log_path = config.log_path / "app.log"
    log_path.mkdir(parents=True, exist_ok=True)
    logger.add(
        sink=log_path,
        format='{time} - {name} - {level} - {message}',
        level="INFO",
        encoding='utf-8',
    )
    logger.info("Program started")
