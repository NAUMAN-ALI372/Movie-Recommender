import pickle

import pandas as pd
import requests
import streamlit as st
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def _build_session() -> requests.Session:
    session = requests.Session()
    retry_strategy = Retry(
        total=3,                              # retry up to 3 times
        backoff_factor=1,                     # wait 1s, 2s, 4s between retries
        status_forcelist=[429, 500, 502, 503, 504],  # retry on these HTTP error codes too
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


SESSION = _build_session()

TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
PLACEHOLDER_POSTER = "https://via.placeholder.com/500x750.png?text=Poster+Unavailable"


@st.cache_data(show_spinner=False, ttl=3600)  # cache each poster for 1 hour - avoids re-fetching on every rerun
def fetch_poster(movie_id) -> str:
    """
    Fetch a movie's poster URL from TMDb.

    On ANY failure (network reset, timeout, TMDb down, missing poster,
    invalid API key, etc.) this returns a placeholder image instead of
    raising - that is the key change that stops one bad request from
    crashing the whole Streamlit app.
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    try:
        response = SESSION.get(url, params={"api_key": TMDB_API_KEY}, timeout=10)
        response.raise_for_status()  # raises for 4xx/5xx responses (e.g. bad API key, rate limit)
    except requests.exceptions.RequestException as e:
        # Covers ConnectionError, Timeout, SSLError, HTTPError - everything
        # requests can throw for a failed call - and shows it as a small
        # warning in the UI instead of crashing the page.
        st.warning(f"Could not fetch poster for movie_id {movie_id}: {e}")
        return PLACEHOLDER_POSTER

    data = response.json()
    poster_path = data.get("poster_path")
    if not poster_path:

        return PLACEHOLDER_POSTER

    return "https://image.tmdb.org/t/p/w500" + poster_path


def recommend(movie: str):
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True,
    )[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]]["title"])
        recommended_movies_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_posters



movie_dict = pickle.load(open("movies_dict.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))
movies = pd.DataFrame(movie_dict)


st.title("Movie Recommender System")

selected_movie_name = st.selectbox(
    "Select a Movie Recommendation System",
    movies["title"].values,
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)


    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.header(names[0])
        st.image(posters[0])
    with col2:
        st.header(names[1])
        st.image(posters[1])
    with col3:
        st.header(names[2])
        st.image(posters[2])
    with col4:
        st.header(names[3])
        st.image(posters[3])
    with col5:
        st.header(names[4])
        st.image(posters[4])