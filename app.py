
from flask import Flask, render_template, request, redirect, url_for, g, jsonify
import sqlite3, os, requests
from datetime import datetime

app = Flask(__name__)
DATABASE = os.path.join("instance","stars.db")
TMDB_API_KEY = "8759c347308b901c2477899708088368"

def get_db():
    db = getattr(g,"_database",None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g,"_database",None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with open("schema.sql") as f:
        db.executescript(f.read())
    db.commit()

@app.route("/init")
def initialize():
    init_db()
    return "Database initialized"

@app.route("/")
def home():
    db = get_db()
    movies = db.execute(
        """
        SELECT movies.*, COUNT(comments.id) as review_count
        FROM movies
        LEFT JOIN comments ON movies.id = comments.movie_id
        GROUP BY movies.id
        ORDER BY review_count DESC
        """
    ).fetchall()
    return render_template("home.html", movies=movies)

@app.route("/search_movie")
def search_movie():
    query = request.args.get("q")
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
    data = requests.get(url).json()

    results=[]
    for m in data.get("results",[])[:5]:
        poster = ""
        if m.get("poster_path"):
            poster = "https://image.tmdb.org/t/p/w500"+m["poster_path"]
        results.append({"title":m["title"],"poster":poster})

    return jsonify(results)

@app.route("/add_movie", methods=["GET","POST"])
def add_movie():
    db = get_db()
    if request.method == "POST":
        title = request.form["title"]
        poster = request.form["poster"]
        review = request.form["review"]

        db.execute(
            "INSERT INTO movies(title,poster,review,created_at) VALUES(?,?,?,?)",
            (title,poster,review,datetime.now())
        )
        db.commit()
        return redirect(url_for("home"))

    return render_template("add_movie.html")

@app.route("/movie/<int:movie_id>", methods=["GET","POST"])
def movie(movie_id):
    db = get_db()

    if request.method == "POST":
        rating = int(request.form["rating"])
        comment = request.form["comment"]

        db.execute(
            "INSERT INTO comments(movie_id,rating,comment,likes,created_at) VALUES(?,?,?,?,?)",
            (movie_id,rating,comment,0,datetime.now())
        )
        db.commit()
        return redirect(url_for("movie",movie_id=movie_id))

    movie = db.execute("SELECT * FROM movies WHERE id=?", (movie_id,)).fetchone()

    comments = db.execute(
        "SELECT * FROM comments WHERE movie_id=? ORDER BY id DESC",(movie_id,)
    ).fetchall()

    ratings = [c["rating"] for c in comments]
    avg = round(sum(ratings)/len(ratings),2) if ratings else 0

    return render_template("movie.html",movie=movie,comments=comments,avg=avg)

@app.route("/like/<int:comment_id>")
def like(comment_id):
    db = get_db()
    db.execute("UPDATE comments SET likes = likes + 1 WHERE id=?",(comment_id,))
    db.commit()
    return redirect(request.referrer)

if __name__ == "__main__":
    if not os.path.exists("instance"):
        os.makedirs("instance")
    app.run(debug=True)
