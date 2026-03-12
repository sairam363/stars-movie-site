
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
DB_PATH = os.path.join(INSTANCE_DIR, "stars.db")

os.makedirs(INSTANCE_DIR, exist_ok=True)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS movies(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        poster TEXT,
        created_at TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS comments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id INTEGER,
        rating INTEGER,
        comment TEXT,
        likes INTEGER DEFAULT 0,
        created_at TEXT,
        FOREIGN KEY(movie_id) REFERENCES movies(id)
    )
    """)

    conn.commit()
    conn.close()


init_db()


@app.route("/")
def home():
    db = get_db()

    movies = db.execute("""
        SELECT m.*, 
        IFNULL(AVG(c.rating),0) as avg_rating,
        COUNT(c.id) as review_count
        FROM movies m
        LEFT JOIN comments c ON m.id = c.movie_id
        GROUP BY m.id
        ORDER BY m.created_at DESC
    """).fetchall()

    db.close()

    return render_template("home.html", movies=movies)


@app.route("/movie/<int:movie_id>")
def movie(movie_id):
    db = get_db()

    movie = db.execute(
        "SELECT * FROM movies WHERE id=?", (movie_id,)
    ).fetchone()

    comments = db.execute(
        "SELECT * FROM comments WHERE movie_id=? ORDER BY created_at DESC",
        (movie_id,)
    ).fetchall()

    db.close()

    return render_template("movie.html", movie=movie, comments=comments)


@app.route("/add_movie", methods=["POST"])
def add_movie():
    title = request.form["title"]
    poster = request.form["poster"]

    db = get_db()

    db.execute(
        "INSERT INTO movies(title, poster, created_at) VALUES(?,?,?)",
        (title, poster, datetime.now())
    )

    db.commit()
    db.close()

    return redirect(url_for("home"))


@app.route("/add_review/<int:movie_id>", methods=["POST"])
def add_review(movie_id):
    rating = request.form["rating"]
    comment = request.form["comment"]

    db = get_db()

    db.execute(
        "INSERT INTO comments(movie_id,rating,comment,likes,created_at) VALUES(?,?,?,?,?)",
        (movie_id, rating, comment, 0, datetime.now())
    )

    db.commit()
    db.close()

    return redirect(url_for("movie", movie_id=movie_id))


@app.route("/like/<int:comment_id>")
def like(comment_id):
    db = get_db()

    db.execute(
        "UPDATE comments SET likes = likes + 1 WHERE id=?",
        (comment_id,)
    )

    db.commit()
    db.close()

    return redirect(request.referrer)


if __name__ == "__main__":
    app.run(debug=True)