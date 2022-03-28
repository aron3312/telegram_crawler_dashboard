CREATE TABLE message (
    id TEXT NOT NULL PRIMARY KEY,
    channel_name TEXT NOT NULL,
    date TEXT NOT NULL,
    message TEXT NOT NULL,
    views INT NOT NULL
);