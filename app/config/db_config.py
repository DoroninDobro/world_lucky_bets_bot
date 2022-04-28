from typing import Any

from app.models.config.db import DBConfig


def load_db_config(dct: dict[str, Any]) -> DBConfig:
    result = DBConfig()
    result.type = dct["type"]
    result.login = dct["login"]
    result.password = dct["password"]
    result.name = dct["name"]
    result.host = dct["host"]
    port = dct.get("port", None)
    if port is None:
        if result.type == 'mysql':
            result.port = 3306
        elif result.type == 'postgres':
            result.port = 5432
    else:
        result.port = int(port)
    return result
