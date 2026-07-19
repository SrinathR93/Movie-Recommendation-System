import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [title, setTitle] = useState("");
  const [searchedMovie, setSearchedMovie] = useState("");
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const languages = {
    EN: "English",
    HI: "Hindi",
    ZH: "Chinese",
    FR: "French",
    ES: "Spanish",
    TA: "Tamil",
    TE: "Telugu",
    ML: "Malayalam",
    KN: "Kannada",
    JA: "Japanese",
    KO: "Korean",
    DE: "German",
    IT: "Italian",
    RU: "Russian",
    PT: "Portuguese",
    AR: "Arabic",
  };

  const getRatingColor = (rating) => {
    if (rating >= 7) {
      return "#4ade80";
    }

    if (rating >= 5) {
      return "#facc15";
    }

    return "#f87171";
  };

  const formatReleaseDate = (releaseDate) => {
    if (!releaseDate || releaseDate === "Unknown") {
      return "Unknown";
    }

    const date = new Date(releaseDate);

    if (Number.isNaN(date.getTime())) {
      return releaseDate;
    }

    return date.toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  };

  const getRecommendations = async (event) => {
    event.preventDefault();

    if (!title.trim()) {
      setError("Please enter a movie title");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setRecommendations([]);

      const response = await axios.post(
        "https://movie-recommendation-system-cloq.onrender.com/recommend",
        {
          title: title.trim(),
        }
      );

      setSearchedMovie(response.data.searched_movie);

      setRecommendations(
        response.data.recommendations || []
      );
    } catch (error) {
      setError(
        error.response?.data?.message ||
          "Unable to get recommendations"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <nav className="navbar">
        <div className="logo">MovieMatch AI</div>

        <span>
          Content-Based Recommendation System
        </span>
      </nav>

      <main className="container">
        <section className="hero">
          <p className="hero-label">
            DISCOVER YOUR NEXT MOVIE
          </p>

          <h1>
            Find Movies Similar To Your Favourites
          </h1>

          <p className="hero-description">
            Search for a movie and receive five recommendations
            based on genre, cast, keywords and description.
          </p>

          <form
            className="search-container"
            onSubmit={getRecommendations}
          >
            <input
              type="text"
              placeholder="Search Avatar, Batman, Titanic..."
              value={title}
              onChange={(event) =>
                setTitle(event.target.value)
              }
            />

            <button
              type="submit"
              disabled={loading}
            >
              {loading
                ? "Searching..."
                : "Recommend"}
            </button>
          </form>

          {error && (
            <p className="error-message">
              {error}
            </p>
          )}
        </section>

        {recommendations.length > 0 && (
          <section className="results">
            <div className="results-heading">
              <div>
                <p>RECOMMENDATIONS</p>

                <h2>
                  Movies similar to {searchedMovie}
                </h2>
              </div>

              <span>
                {recommendations.length} movies found
              </span>
            </div>

            <div className="movie-grid">
              {recommendations.map(
                (movie, index) => (
                  <article
                    className="movie-card"
                    key={`${movie.movie_id}-${index}`}
                  >
                    <div className="card-top">
                      <span className="rank">
                        #{index + 1}
                      </span>

                      <span className="score">
                        {movie.similarity_score}% Match
                      </span>
                    </div>

                    <div className="movie-content">
                      <h3>{movie.title}</h3>

                      <div className="movie-meta">
                        <span
                          style={{
                            color: getRatingColor(
                              movie.rating || 0
                            ),
                          }}
                        >
                          ⭐{" "}
                          {typeof movie.rating ===
                          "number"
                            ? movie.rating.toFixed(1)
                            : "0.0"}
                          /10
                        </span>

                        <span>
                          🌐{" "}
                          {languages[
                            movie.language
                          ] ||
                            movie.language ||
                            "Unknown"}
                        </span>
                      </div>

                      <p className="release-date">
                        📅 Release Date:{" "}
                        {formatReleaseDate(
                          movie.release_date
                        )}
                      </p>

                      <p className="overview">
                        {movie.overview &&
                        movie.overview !==
                          "Overview not available"
                          ? movie.overview.length >
                            150
                            ? `${movie.overview.substring(
                                0,
                                150
                              )}...`
                            : movie.overview
                          : "Overview not available"}
                      </p>
                    </div>
                  </article>
                )
              )}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;