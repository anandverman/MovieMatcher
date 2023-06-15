import streamlit as st
import pickle
import pandas as pd
import requests

API_KEY = "8ad5d364814ed91827a798b45a8f6e84"


def fetch_poster(movie_id):
    try:
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        return "./noimg.png"
    except Exception as err:
        st.error(f"Error occured: {err}")
    else:
        data = response.json()
        poster_path = data["poster_path"]
        if poster_path is None:
            return "./noimg.png"
        return "https://image.tmdb.org/t/p/original/" + poster_path


def recommender(movie):
    try:
        movie_index = movies[movies["title"] == movie].index[0]
    except IndexError:
        st.error(f"No movie with title '{movie}' found in the database.")
        return [], []

    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[
        1:16
    ]
    recommended_movies = []
    recommended_movies_poster = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        poster = fetch_poster(movie_id)
        if poster:
            recommended_movies_poster.append(poster)

    if not recommended_movies:
        st.warning("Sorry, no recommendations found for this movie.")

    return recommended_movies, recommended_movies_poster


movies_list = pickle.load(open("movie.pkl", "rb"))
movies = pd.DataFrame(movies_list)

similarity = pickle.load(open("similarity.pkl", "rb"))

# Page Layout
st.set_page_config(layout="wide")


# Setting title
st.title("Movie Matcher")
st.markdown("---")

# Multiselect to enter movie names
get_movie_names = st.multiselect(
    "Enter the movie names you want to find matches for.", movies["title"].values
)

if st.button("Match"):
    for movie_name in get_movie_names:
        st.subheader("Because you watched: " + movie_name)
        recommended_movies, recommended_movies_posters = recommender(movie_name)
        if recommended_movies:
            num_rows = 3
            cols_per_row = 5
            cols = st.columns(cols_per_row)
            index = 0
            for i in range(num_rows):
                for j in range(cols_per_row):
                    with cols[j]:
                        if index < len(recommended_movies):
                            st.text(recommended_movies[index])
                            st.image(recommended_movies_posters[index])
                            index += 1
                        else:
                            break
