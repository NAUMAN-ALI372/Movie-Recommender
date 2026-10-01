import pickle
import streamlit as st
import pandas as pd
import requests

def fetch_poster(movie):
    pass

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    recommended_movies = []

    for i in movies_list:
        movie_id=i[0]
        #fetch poster from API
        recommended_movies.append(movies.iloc[i[0]]['title'])
    return recommended_movies


movie_dict = pickle.load(open('movies_dict.pkl', 'rb'))
similarity = pickle.load(open('similarity_float32.pkl','rb'))

movies = pd.DataFrame(movie_dict)

st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    'Select a Movie Recommendation System',
    movies['title'].values
)

if st.button('Recommend'):
    recommendations = recommend(selected_movie_name)

    for i in recommendations:
        st.write(i)