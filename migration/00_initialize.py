from app.misc import config as global_config
from app.models.db.db import generate_schemas


def main():
    generate_schemas(db_config=global_config.db_config)


if __name__ == "__main__":
    main()
