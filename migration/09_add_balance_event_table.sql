CREATE TABLE balance_events(
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    delta NUMERIC(20, 10),
    currency VARCHAR,
    type TEXT NOT NULL,
    bet_item_id INTEGER NULL,
    comment TEXT NULL
);
ALTER TABLE balance_events
    ADD CONSTRAINT balance_events_user_id_fk
        FOREIGN KEY (user_id)
            REFERENCES public.users (id);
ALTER TABLE balance_events
    ADD CONSTRAINT balance_events_author_id_fk
        FOREIGN KEY (author_id)
            REFERENCES public.users (id);
ALTER TABLE balance_events
    ADD CONSTRAINT balance_events_bet_item_id_fk
        FOREIGN KEY (bet_item_id)
            REFERENCES public.bets_log (id);
