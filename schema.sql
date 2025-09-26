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

CREATE TABLE IF NOT EXISTS t_file
(
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    filename        TEXT NOT NULL,
    filesize        INTEGER,
    filetype        TEXT,
    filepath        TEXT,                   -- 存储相对路径，比如 /upload/family/xxx.jpg
    parent_id       INTEGER DEFAULT NULL,   -- 层级结构：父目录ID
    is_dir          INTEGER DEFAULT 0,      -- 是否是目录 (0=文件, 1=目录)
    create_datetime TEXT,
    update_datetime TEXT
);