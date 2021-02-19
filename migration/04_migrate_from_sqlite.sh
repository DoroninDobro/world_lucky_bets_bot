sqlite_db_name=test_bot.db
postgres_db=test_bot
pgloader sqlite:///$sqlite_db_name postgresql:///$postgres_db --after 04_migrate_from_sqlite.sql
dump_dir=test_bot_dump
pg_dump -f $dump_dir -F d --no-owner --no-privileges $postgres_db
pg_restore -F d --no-owner --no-privileges -U postgres -d $postgres_db $dump_dir

