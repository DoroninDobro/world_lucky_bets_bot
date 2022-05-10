ALTER TABLE users
    ADD COLUMN worker_status TEXT NULL;
ALTER TABLE users
    ADD COLUMN piecework_pay numeric(20, 10) NULL;
ALTER TABLE users
    ADD COLUMN salary TEXT NULL;
