CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    poster TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_id INTEGER,
    rating INTEGER,
    comment TEXT,
    likes INTEGER DEFAULT 0,
    created_at TEXT,
    FOREIGN KEY(movie_id) REFERENCES movies(id)
);