import pathlib

from loguru import logger

from app.config import PRINT_LOG, app_dir, CURRENT_BOT

log_path = pathlib.Path(app_dir / 'log' / CURRENT_BOT)
log_path.mkdir(parents=True, exist_ok=True)


def setup():
    logger.add(
        sink=log_path / PRINT_LOG,
        format='{time} - {name} - {level} - {message}',
        level="INFO",
        encoding='utf-8',
    )
    logger.info("Program started")
