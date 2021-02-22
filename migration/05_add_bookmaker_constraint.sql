ALTER TABLE bets_log
   ADD COLUMN bookmaker_id BIGINT,
   ADD CONSTRAINT bets_log_bookmaker_id_fkey
   FOREIGN KEY (bookmaker_id)
   REFERENCES bookmakers(id)
   ON DELETE CASCADE;
