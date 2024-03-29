import sqlite3

from app.misc import config as global_config


def upgrade():
    with sqlite3.connect(global_config.db_config.db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
            ALTER TABLE work_threads
            ADD COLUMN log_chat_for_admins_without_usernames_message_id INT 
        """)


if __name__ == '__main__':
    upgrade()
