ALTER TABLE bets_log ALTER COLUMN bet type NUMERIC(20, 10) USING bet::NUMERIC;
ALTER TABLE bets_log ALTER COLUMN result type NUMERIC(20, 10) USING result::NUMERIC;
ALTER TABLE historical_rates ALTER COLUMN to_eur type NUMERIC(20, 10) USING to_eur::NUMERIC;
ALTER TABLE historical_rates ALTER COLUMN to_usd type NUMERIC(20, 10) USING to_usd::NUMERIC;

ALTER TABLE work_threads ALTER COLUMN stopped DROP DEFAULT;
ALTER TABLE work_threads ALTER COLUMN stopped TYPE boolean using stopped::boolean;
ALTER TABLE work_threads ALTER COLUMN stopped SET DEFAULT false;
ALTER TABLE additional_texts ALTER COLUMN is_draft DROP DEFAULT;
ALTER TABLE additional_texts ALTER COLUMN is_draft TYPE boolean using is_draft::boolean;
ALTER TABLE additional_texts ALTER COLUMN is_draft SET DEFAULT false;
ALTER TABLE additional_texts ALTER COLUMN is_disinformation DROP DEFAULT;
ALTER TABLE additional_texts ALTER COLUMN is_disinformation TYPE boolean using is_disinformation::boolean;
ALTER TABLE additional_texts ALTER COLUMN is_disinformation SET DEFAULT false;
ALTER TABLE send_to_workers ALTER COLUMN send DROP DEFAULT;
ALTER TABLE send_to_workers ALTER COLUMN send TYPE boolean using send::boolean;
ALTER TABLE send_to_workers ALTER COLUMN send SET DEFAULT true;

ALTER TABLE bookmakers ALTER COLUMN created TYPE timestamp with time zone;
ALTER TABLE bets_log ALTER COLUMN created TYPE timestamp with time zone;
ALTER TABLE work_threads ALTER COLUMN start TYPE timestamp with time zone;
