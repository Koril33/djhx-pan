CREATE TABLE IF NOT EXISTS t_user
(
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT,
    password        TEXT,
    salt            TEXT,
    nickname        TEXT,
    email           TEXT,
    phone           TEXT,
    create_datetime TEXT,
    update_datetime TEXT
);