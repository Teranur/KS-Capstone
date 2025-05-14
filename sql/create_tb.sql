DROP TABLE IF EXISTS c12de.kr_so_capstone;

CREATE TABLE c12de.kr_so_capstone (
    appid             INTEGER       PRIMARY KEY,
    name              TEXT          NOT NULL,
    release_date      DATE,
    price             NUMERIC(10,2),
    dlc_count         INTEGER,
    header_image      TEXT,
    about_the_game    TEXT,
    windows           BOOLEAN,
    mac               BOOLEAN,
    linux             BOOLEAN,
    metacritic_score  INTEGER,
    recommendations   INTEGER,
    developers        TEXT,
    categories        TEXT,
    genres            TEXT,
    positive          INTEGER,
    negative          INTEGER,
    estimated_owners  INTEGER,
    current_players   INTEGER,
    release_year      INTEGER,
    estimated_revenue NUMERIC(14,1),
    price_tier        VARCHAR(20),
    positive_ratio    NUMERIC(5,1)
);