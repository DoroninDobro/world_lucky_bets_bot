import sqlite3

from app import config


def upgrade():
    with sqlite3.connect(config.DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            ALTER TABLE bets_log
            ADD COLUMN bookmaker_id INT NULL;
            """)
        cur.execute("""
            ALTER TABLE bets_log
            ADD CONSTRAINT fk_bets_log_bookmaker
            FOREIGN KEY (bookmaker_id)
            REFERENCES bookmakers(id);
        """)
        conn.commit()


if __name__ == '__main__':
    upgrade()
