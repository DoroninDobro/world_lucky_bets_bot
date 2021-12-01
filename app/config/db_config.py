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
    db_port: int = None
    db_path: str = None

    def init_from_environment(self, app_dir: Path):
        self.db_type = os.getenv("DB_TYPE", default='sqlite')
        self.login = os.getenv("DB_LOGIN")
        self.password = os.getenv("DB_PASSWORD")
        self.db_name = os.getenv("DB_NAME", default="bot")
        self.db_host = os.getenv("DB_HOST", default='localhost')
        port = os.getenv("DB_PORT")
        if port is None:
            if self.db_type == 'mysql':
                self.db_port = 5432
            elif self.db_type == 'postgres':
                self.db_port = 3306
        else:
            self.db_port = int(port)
        self.db_path = os.getenv("DB_PATH", default=app_dir / "db_data" / "bot" / "bot.db")

    def create_url_config(self):
        db_url = ""
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
        return db_url
