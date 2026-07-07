-- Movie Ticket Booking System - initial schema (PostgreSQL)

CREATE TABLE app_user (
    id         BIGSERIAL PRIMARY KEY,
    email      VARCHAR(255) NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    full_name  VARCHAR(255) NOT NULL,
    role       VARCHAR(20)  NOT NULL,
    created_at TIMESTAMPTZ  NOT NULL
);

CREATE TABLE city (
    id    BIGSERIAL PRIMARY KEY,
    name  VARCHAR(255) NOT NULL UNIQUE,
    state VARCHAR(255) NOT NULL
);

CREATE TABLE theater (
    id      BIGSERIAL PRIMARY KEY,
    name    VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    city_id BIGINT NOT NULL REFERENCES city (id)
);

CREATE TABLE screen (
    id         BIGSERIAL PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    theater_id BIGINT NOT NULL REFERENCES theater (id)
);

CREATE TABLE seat (
    id          BIGSERIAL PRIMARY KEY,
    screen_id   BIGINT NOT NULL REFERENCES screen (id),
    row_label   VARCHAR(4) NOT NULL,
    seat_number INTEGER NOT NULL,
    seat_class  VARCHAR(20) NOT NULL,
    CONSTRAINT uq_seat_position UNIQUE (screen_id, row_label, seat_number)
);

CREATE TABLE movie (
    id               BIGSERIAL PRIMARY KEY,
    title            VARCHAR(255) NOT NULL,
    language         VARCHAR(255) NOT NULL,
    genre            VARCHAR(255) NOT NULL,
    duration_minutes INTEGER NOT NULL,
    certification    VARCHAR(10)
);

CREATE TABLE show_event (
    id         BIGSERIAL PRIMARY KEY,
    movie_id   BIGINT NOT NULL REFERENCES movie (id),
    screen_id  BIGINT NOT NULL REFERENCES screen (id),
    start_time TIMESTAMPTZ NOT NULL,
    end_time   TIMESTAMPTZ NOT NULL,
    base_price NUMERIC(10, 2) NOT NULL
);

CREATE TABLE pricing_tier (
    id         BIGSERIAL PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    seat_class VARCHAR(20) NOT NULL UNIQUE,
    multiplier NUMERIC(6, 3) NOT NULL
);

CREATE TABLE discount_code (
    id           BIGSERIAL PRIMARY KEY,
    code         VARCHAR(40) NOT NULL UNIQUE,
    type         VARCHAR(20) NOT NULL,
    value        NUMERIC(10, 2) NOT NULL,
    max_discount NUMERIC(10, 2),
    min_amount   NUMERIC(10, 2),
    valid_from   TIMESTAMPTZ,
    valid_to     TIMESTAMPTZ,
    active       BOOLEAN NOT NULL
);

CREATE TABLE refund_policy (
    id                          BIGSERIAL PRIMARY KEY,
    name                        VARCHAR(255) NOT NULL,
    full_refund_hours_before    INTEGER NOT NULL,
    partial_refund_hours_before INTEGER NOT NULL,
    partial_refund_percent      NUMERIC(5, 2) NOT NULL,
    active                      BOOLEAN NOT NULL
);

CREATE TABLE show_seat (
    id              BIGSERIAL PRIMARY KEY,
    show_id         BIGINT NOT NULL REFERENCES show_event (id),
    seat_id         BIGINT NOT NULL REFERENCES seat (id),
    status          VARCHAR(20) NOT NULL,
    price           NUMERIC(10, 2) NOT NULL,
    held_until      TIMESTAMPTZ,
    held_by_user_id BIGINT,
    version         BIGINT NOT NULL,
    CONSTRAINT uq_show_seat UNIQUE (show_id, seat_id)
);

CREATE INDEX idx_show_seat_show ON show_seat (show_id);

CREATE TABLE booking (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL REFERENCES app_user (id),
    show_id         BIGINT NOT NULL REFERENCES show_event (id),
    status          VARCHAR(20) NOT NULL,
    total_amount    NUMERIC(10, 2),
    discount_amount NUMERIC(10, 2),
    final_amount    NUMERIC(10, 2),
    refund_amount   NUMERIC(10, 2),
    discount_code   VARCHAR(40),
    hold_expires_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL,
    confirmed_at    TIMESTAMPTZ,
    cancelled_at    TIMESTAMPTZ,
    version         BIGINT NOT NULL
);

CREATE INDEX idx_booking_status_hold ON booking (status, hold_expires_at);
CREATE INDEX idx_booking_user ON booking (user_id);

CREATE TABLE booking_seat (
    id           BIGSERIAL PRIMARY KEY,
    booking_id   BIGINT NOT NULL REFERENCES booking (id),
    show_seat_id BIGINT NOT NULL REFERENCES show_seat (id),
    active       BOOLEAN NOT NULL DEFAULT TRUE
);

-- Physical backstop against double-allocation: at most one ACTIVE allocation per
-- show seat. Because a show_seat is unique per (show, seat), this is equivalent
-- to UNIQUE(show_id, seat_id) for active allocations. Correctness therefore does
-- not depend solely on application logic being bug-free.
CREATE UNIQUE INDEX uq_booking_seat_active ON booking_seat (show_seat_id) WHERE active = TRUE;

CREATE TABLE payment (
    id              BIGSERIAL PRIMARY KEY,
    booking_id      BIGINT NOT NULL UNIQUE REFERENCES booking (id),
    amount          NUMERIC(10, 2) NOT NULL,
    status          VARCHAR(20) NOT NULL,
    method          VARCHAR(20) NOT NULL,
    transaction_ref VARCHAR(64) NOT NULL,
    paid_at         TIMESTAMPTZ NOT NULL
);

CREATE TABLE audit_event (
    id          BIGSERIAL PRIMARY KEY,
    entity_type VARCHAR(40) NOT NULL,
    entity_id   BIGINT NOT NULL,
    action      VARCHAR(40) NOT NULL,
    details     VARCHAR(1000),
    user_id     BIGINT,
    created_at  TIMESTAMPTZ NOT NULL
);
