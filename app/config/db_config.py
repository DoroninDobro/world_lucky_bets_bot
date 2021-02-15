import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DBConfig:
    db_type: str = None
    login: str = None
    password: str = None
    db_name: str = None
    db_host: str = None
    db_port: str = None
    db_path: str = None

    def init_from_environment(self, app_dir: Path, current_bot: str):
        self.db_type = os.getenv("DB_TYPE", default='sqlite')
        self.login = os.getenv("LOGIN_DB")
        self.password = os.getenv("PASSWORD_DB")
        self.db_name = os.getenv("DB_NAME", default=current_bot)
        self.db_host = os.getenv("DB_HOST")
        self.db_port = os.getenv("DB_PORT")
        self.db_path = os.getenv("DB_PATH", default=app_dir / "db_data" / current_bot / "bot.db")

    def create_url_config(self):
        if self.db_type == 'mysql':
            db_url = (
                f'{self.db_type}://{self.login}:{self.password}'
                f'@{self.db_host}:{self.db_port}/{self.db_name}'
            )
        elif self.db_type == 'postgres':
            db_url = (
                f'{self.db_type}://{self.login}:{self.password}'
                f'@{self.db_host}:{self.db_port}/{self.db_name}'
            )
        elif self.db_type == 'sqlite':
            db_url = (
                f'{self.db_type}://{self.db_path}'
            )
        else:
            raise ValueError("DB_TYPE not mysql, sqlite or postgres")
        return db_url
