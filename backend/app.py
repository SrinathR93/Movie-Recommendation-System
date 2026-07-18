from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import os

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MOVIES_PATH = os.path.join(
    BASE_DIR,
    "..",
    "model",
    "movies.pkl"
)

SIMILARITY_PATH = os.path.join(
    BASE_DIR,
    "..",
    "model",
    "similarity.pkl"
)

with open(MOVIES_PATH, "rb") as file:
    movies = pickle.load(file)

with open(SIMILARITY_PATH, "rb") as file:
    similarity = pickle.load(file)

print("Columns:", movies.columns.tolist())


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

        similarity_scores = list(
            enumerate(similarity[movie_index])
        )

        sorted_movies = sorted(
            similarity_scores,
            key=lambda item: item[1],
            reverse=True
        )[1:6]

        recommendations = []

        for index, score in sorted_movies:
            movie = movies.iloc[index]

            recommendations.append({
                "movie_id": int(movie["movie_id"]),
                "title": str(movie["title"]),
                "tags": str(movie.get("tags", "")),
                "release_date": str(
                    movie.get("release_date", "Unknown")
                ),
                "rating": float(
                    movie.get("vote_average", 0)
                ),
                "runtime": int(
                    movie.get("runtime", 0)
                ),
                "language": str(
                    movie.get(
                        "original_language",
                        "Unknown"
                    )
                ).upper(),
                "overview": str(
                    movie.get(
                        "overview",
                        "Overview not available"
                    )
                ),
                "similarity_score": round(
                    float(score) * 100,
                    2
                )
            })

        return jsonify({
            "success": True,
            "searched_movie": str(
                movies.iloc[movie_index]["title"]
            ),
            "recommendations": recommendations
        })

    except Exception as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)