from __future__ import annotations

from dataclasses import dataclass

import logging

logger = logging.getLogger(__name__)


@dataclass
class DBConfig:
    type: str = None
    connector: str = None  # unused
    host: str = None
    port: int = None
    login: str = None
    password: str = None
    name: str = None

    @property
    def uri(self):
        if self.type in ('mysql', 'postgresql'):
            url = (
                f'{self.type}://{self.login}:{self.password}'
                f'@{self.host}:{self.port}/{self.name}'
            )
        else:
            raise ValueError("DB_TYPE not mysql or postgres")
        logger.debug(url)
        return url
