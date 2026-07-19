from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import os
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MOVIES_PATH = os.path.join(
    BASE_DIR,
    "..",
    "model",
    "movies.pkl"
)

# Load only movies.pkl
with open(MOVIES_PATH, "rb") as file:
    movies = pickle.load(file)

# Reset index to avoid wrong vector index
movies = movies.reset_index(drop=True)

# Handle missing tags
movies["tags"] = movies["tags"].fillna("")

# Convert movie tags into vectors
vectorizer = CountVectorizer(
    max_features=5000,
    stop_words="english"
)

vectors = vectorizer.fit_transform(movies["tags"])

print("Columns:", movies.columns.tolist())
print("Movie Recommendation Model Loaded")


def safe_text(value, default="Unknown"):
    if pd.isna(value):
        return default
    return str(value)


def safe_float(value):
    if pd.isna(value):
        return 0.0
    return float(value)


def safe_int(value):
    if pd.isna(value):
        return 0
    return int(value)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "message": "Movie Recommendation API Running"
    })


@app.route("/recommend", methods=["POST"])
def recommend_movies():
    try:
        data = request.get_json()

        if not data or not data.get("title"):
            return jsonify({
                "success": False,
                "message": "Movie title is required"
            }), 400

        searched_title = data.get("title").strip()

        matched_movies = movies[
            movies["title"].str.lower() == searched_title.lower()
        ]

        if matched_movies.empty:
            return jsonify({
                "success": False,
                "message": "Movie not found"
            }), 404

        movie_index = matched_movies.index[0]

        # Calculate similarity only for searched movie
        similarity_scores = cosine_similarity(
            vectors[movie_index],
            vectors
        ).flatten()

        sorted_movie_indexes = similarity_scores.argsort()[::-1][1:6]

        recommendations = []

        for index in sorted_movie_indexes:
            movie = movies.iloc[index]
            score = similarity_scores[index]

            recommendations.append({
                "movie_id": safe_int(movie["movie_id"]),
                "title": safe_text(movie["title"]),
                "tags": safe_text(movie.get("tags", ""), ""),
                "release_date": safe_text(
                    movie.get("release_date"),
                    "Unknown"
                ),
                "rating": safe_float(
                    movie.get("vote_average", 0)
                ),
                "runtime": safe_int(
                    movie.get("runtime", 0)
                ),
                "language": safe_text(
                    movie.get("original_language"),
                    "Unknown"
                ).upper(),
                "overview": safe_text(
                    movie.get("overview"),
                    "Overview not available"
                ),
                "similarity_score": round(
                    float(score) * 100,
                    2
                )
            })

        return jsonify({
            "success": True,
            "searched_movie": safe_text(
                movies.iloc[movie_index]["title"]
            ),
            "recommendations": recommendations
        })

    except Exception as error:
        print("Recommendation error:", error)

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)