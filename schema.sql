create table main.t_file
(
    id              INTEGER
        primary key autoincrement,
    filename        TEXT not null,
    filesize        INTEGER,
    filetype        TEXT,
    filepath        TEXT,
    parent_id       INTEGER default NULL,
    is_dir          INTEGER default 0,
    create_datetime TEXT,
    update_datetime TEXT
);

create table main.t_share
(
    id               INTEGER
        primary key autoincrement,
    file_id          INTEGER not null,
    share_key        TEXT    not null
        unique,
    password         TEXT,
    expires_at       TEXT,
    allow_download   BOOLEAN default 1,
    allow_delete     BOOLEAN default 0,
    created_datetime TEXT    not null,
    update_datetime  TEXT    not null
);

create table main.t_user
(
    id              INTEGER
        primary key autoincrement,
    username        TEXT,
    password        TEXT,
    salt            TEXT,
    nickname        TEXT,
    email           TEXT,
    phone           TEXT,
    create_datetime TEXT,
    update_datetime TEXT
);


