CREATE TABLE balance_events(
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    delta NUMERIC(20, 10),
    currency VARCHAR,
    comment TEXT NULL
);
ALTER TABLE balance_events
    ADD CONSTRAINT balance_events_user_id_fk
        FOREIGN KEY (user_id)
            REFERENCES public.users (id);
