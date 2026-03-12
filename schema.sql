
CREATE TABLE movies(
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT,
poster TEXT,
review TEXT,
created_at TEXT
);

CREATE TABLE comments(
id INTEGER PRIMARY KEY AUTOINCREMENT,
movie_id INTEGER,
rating INTEGER,
comment TEXT,
likes INTEGER,
created_at TEXT
);
