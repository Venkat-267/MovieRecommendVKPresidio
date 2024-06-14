import pickle
import streamlit as st
import requests
import sqlite3
import os
import hashlib

st.set_page_config(page_title="MovieFlix", page_icon="🎥")
movies = pickle.load(open('models/movie_list.pkl','rb'))
similarity = pickle.load(open('models/similarity.pkl','rb'))


conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT
    )
"""
)
conn.commit()

def create_user(username, password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash),
    )
    conn.commit()

def verify_login(username, password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password_hash=?",
        (username, password_hash),
    )
    return cursor.fetchone() is not None

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        # fetch the movie poster
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names,recommended_movie_posters

class MovieRecommender:
    def __init__(self):
        st.header('MovieFlix Recommender')
        movies = pickle.load(open('models/movie_list.pkl','rb'))
        similarity = pickle.load(open('models/similarity.pkl','rb'))

        movie_list = movies['title'].values
        selected_movie = st.selectbox(
            "Type or select a movie from the dropdown",
            movie_list
        )

        if st.button('Show Recommendation'):
            recommended_movie_names,recommended_movie_posters = recommend(selected_movie)
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.text(recommended_movie_names[0])
                st.image(recommended_movie_posters[0])
            with col2:
                st.text(recommended_movie_names[1])
                st.image(recommended_movie_posters[1])

            with col3:
                st.text(recommended_movie_names[2])
                st.image(recommended_movie_posters[2])
            with col4:
                st.text(recommended_movie_names[3])
                st.image(recommended_movie_posters[3])
            with col5:
                st.text(recommended_movie_names[4])
                st.image(recommended_movie_posters[4])


def main():
    if not st.session_state.get("logged_in"):
        page = st.sidebar.radio("Select an option:", ["Login", "Signup"])

        if page == "Login":
            st.title("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                if verify_login(username, password):
                    st.session_state.logged_in = True
                    st.success("Login successful!")
                else:
                    st.error("Invalid username or password.")
        elif page == "Signup":
            st.title("Signup")
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            if st.button("Signup"):
                create_user(new_username, new_password)
                st.success("Signup successful! You can now login.")

    if st.session_state.get("logged_in"):
        MovieRecommender()
    else:
        st.warning("Please login or signup to access the application.")


if __name__ == "__main__":
    main()

