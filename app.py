import streamlit as st
import requests
import pandas as pd
import pickle
import urllib.parse
from streamlit_searchbox import st_searchbox

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)

# -----------------------------
# Load Data
# -----------------------------
API_KEY = st.secrets["OMDB_API_KEY"]

movies = pd.read_csv("movies.csv")
similarity = pickle.load(open("similarity.pkl", "rb"))

# -----------------------------
# OMDb Functions
# -----------------------------
def search_movies(search_term):
    if not search_term:
        return []

    url = f"https://www.omdbapi.com/?s={search_term}&apikey={API_KEY}"

    response = requests.get(url)
    data = response.json()

    if data.get("Response") == "True":
        return [movie["Title"] for movie in data["Search"]]

    return []


def get_movie(title):
    url = f"https://www.omdbapi.com/?t={title}&apikey={API_KEY}"

    response = requests.get(url)

    return response.json()


# -----------------------------
# Recommendation Function
# -----------------------------
def recommend(movie_name):

    if movie_name not in movies["title"].values:
        return []

    index = movies[movies["title"] == movie_name].index[0]

    distances = list(enumerate(similarity[index]))

    distances = sorted(
        distances,
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    recommended = []

    for i in distances:
        recommended.append(movies.iloc[i[0]].title)

    return recommended


def get_streaming_platforms(movie_name):

    url = "https://streaming-availability.p.rapidapi.com/shows/search/title"

    querystring = {
        "title": movie_name,
        "country": "in",
        "show_type": "movie"
    }

    headers = {
        "x-rapidapi-key": st.secrets["RAPID_API_KEY"],
        "x-rapidapi-host": st.secrets["RAPID_API_HOST"]
    }

    response = requests.get(
        url,
        headers=headers,
        params=querystring
    )

    if response.status_code == 200:
        return response.json()

    return None


# -----------------------------
# Title
# -----------------------------
st.title("🎬 Movie Recommendation System")

st.markdown(
    "Search any movie, view details, watch the trailer, and discover similar movies."
)

# -----------------------------
# Search Box
# -----------------------------
selected_movie = st_searchbox(
    search_movies,
    placeholder="🔍 Search any movie...",
    key="movie_search"
)

# -----------------------------
# Display Movie
# -----------------------------
if selected_movie:

    movie = get_movie(selected_movie)

    if movie.get("Response") == "True":

        col1, col2 = st.columns([1, 2])

        with col1:

            if movie.get("Poster") != "N/A":
                st.image(movie["Poster"], use_container_width=True)

        with col2:

            st.header(movie["Title"])

            st.write(f"⭐ **IMDb Rating:** {movie.get('imdbRating','N/A')}")
            st.write(f"📅 **Year:** {movie.get('Year','N/A')}")
            st.write(f"🎭 **Genre:** {movie.get('Genre','N/A')}")
            st.write(f"🎬 **Director:** {movie.get('Director','N/A')}")
            st.write(f"👨‍🎤 **Actors:** {movie.get('Actors','N/A')}")
            st.write(f"🌍 **Language:** {movie.get('Language','N/A')}")
            st.write(f"⏱️ **Runtime:** {movie.get('Runtime','N/A')}")

        st.subheader("📝 Plot")

        st.info(movie.get("Plot", "No Plot Available"))

        # -----------------------------
        # Buttons
        # -----------------------------

        youtube_url = (
            "https://www.youtube.com/results?search_query="
            + urllib.parse.quote(movie["Title"] + " Official Trailer")
        )

        watch_url = (
            "https://www.google.com/search?q="
            + urllib.parse.quote(movie["Title"] + " watch online")
        )

        imdb_url = (
            f"https://www.imdb.com/title/{movie['imdbID']}/"
        )

        wiki_url = (
            "https://en.wikipedia.org/wiki/"
            + urllib.parse.quote(movie["Title"])
        )

        st.divider()


        st.subheader("🎥 Watch & Explore")
        
        b1, b2, b3, b4 = st.columns(4)
        
        with b1:
            st.link_button("🎬 Trailer", youtube_url)
        
        with b2:
            st.link_button("🍿 Where to Watch", watch_url)
        
        with b3:
            st.link_button("⭐ IMDb", imdb_url)
        
        with b4:
            st.link_button("📖 Wikipedia", wiki_url)
        
        st.divider()
        
        # -----------------------------
        # Recommendations
        # -----------------------------

        if st.button("🎯 Recommend Similar Movies"):

            recommendations = recommend(movie["Title"])

            if len(recommendations) == 0:

                st.warning(
                    "This movie is not available in the recommendation dataset."
                )

            else:

                st.subheader("🎬 Recommended Movies")

                cols = st.columns(5)

                for i, rec in enumerate(recommendations):

                    rec_movie = get_movie(rec)

                    with cols[i]:

                        if (
                            rec_movie.get("Poster")
                            and rec_movie["Poster"] != "N/A"
                        ):
                            st.image(
                                rec_movie["Poster"],
                                use_container_width=True
                            )

                        st.markdown(
                            f"**{rec_movie.get('Title', rec)}**"
                        )

                        st.caption(
                            f"⭐ {rec_movie.get('imdbRating','N/A')}"
                        )

                        if st.button(
                            "Details",
                            key=f"details_{i}"
                        ):
                            st.info(rec_movie.get("Plot", "No Plot Available"))

    else:

        st.error("Movie not found.")