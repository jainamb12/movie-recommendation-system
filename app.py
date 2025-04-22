import pickle
import pandas as pd
import streamlit as st
import requests

def fetch_poster(movie_id):
    try:
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US",
            timeout=5  # Set timeout to prevent hanging requests
        )
        response.raise_for_status()  # Raises an error for bad responses (4xx, 5xx)
        data = response.json()

        # Check if 'poster_path' exists and is not None
        if data.get('poster_path'):
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        else:
            print(f"No poster found for movie ID {movie_id}")
            return ""  # Return empty string instead of None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return ""  # Return empty string if an error occurs

def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommended_movies = []
        recommended_movies_posters = []

        for i in movies_list:
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movies.append(movies.iloc[i[0]].title)
            poster_url = fetch_poster(movie_id)
            recommended_movies_posters.append(poster_url if poster_url else "Server is busy")  # Handle missing images

        return recommended_movies, recommended_movies_posters

    except Exception as e:
        print(f"Error in recommend function: {e}")
        return ["No recommendation available"], ["Server is busy"]

# Streamlit UI
st.title('Movie Recommender System')

movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

selected_movie_name = st.selectbox(
    'Select a movie to get recommendations:',
    movies['title'].values
)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(5)  # Creates 5 equal columns

    for i in range(5):
        with cols[i]:
            st.text(names[i])  # Display movie name
            if posters[i] and posters[i] != "Server is busy":
                st.image(posters[i])  # Display poster if available
            else:
                st.markdown("<h4 style='color: red;'>Server is busy</h4>", unsafe_allow_html=True)  # Show message in red