import base64
import os
import streamlit as st
import pickle
import pandas as pd
import requests

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="HeyFlix - Movie Recommender System",
    page_icon="🎬",
    layout="wide"
)

# ===================== BACKGROUND SETUP =====================
def add_bg_from_local(image_file):
    with open(image_file, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background: url("data:image/jpg;base64,{encoded_string}") no-repeat center center fixed;
            background-size: cover;
        }}
        [data-testid="stHeader"], [data-testid="stToolbar"] {{
            background: rgba(0,0,0,0);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ✅ Use your uploaded image as full-screen background
add_bg_from_local("yes.jpg")

# ===================== CUSTOM STYLING =====================
page_style = """
<style>
@keyframes glow {
  0% { text-shadow: 0 0 5px #ff4b2b, 0 0 10px #ff416c; }
  50% { text-shadow: 0 0 20px #ff416c, 0 0 30px #ff4b2b; }
  100% { text-shadow: 0 0 5px #ff4b2b, 0 0 10px #ff416c; }
}

@keyframes fadeIn {
  from {opacity: 0; transform: translateY(-20px);}
  to {opacity: 1; transform: translateY(0);}
}

h1 {
    font-family: 'Trebuchet MS', sans-serif;
    text-align: center;
    color: #ffffff;
    animation: glow 2s ease-in-out infinite alternate, fadeIn 2s ease-in-out;
    font-size: 3.8rem !important;
    letter-spacing: 3px;
    margin-bottom: 25px;
    text-shadow: 2px 2px 8px black;
}

/* Frosted-glass container */
.block-container {
    background: rgba(0, 0, 0, 0.55);
    border-radius: 20px;
    padding: 30px 40px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
}

/* Dropdown */
div[data-baseweb="select"] > div {
    background-color: rgba(255, 255, 255, 0.1) !important;
    color: white !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.3);
}

/* Button */
div.stButton > button:first-child {
    background: linear-gradient(135deg, #ff416c, #ff4b2b);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.8em 2.2em;
    font-size: 1.2em;
    font-weight: bold;
    box-shadow: 0px 4px 20px rgba(255, 65, 108, 0.5);
    transition: all 0.3s ease-in-out;
}

div.stButton > button:first-child:hover {
    transform: scale(1.07);
    background: linear-gradient(135deg, #ff4b2b, #ff416c);
    box-shadow: 0px 6px 25px rgba(255, 65, 108, 0.7);
}

/* Movie posters */
div[data-testid="column"] {
    text-align: center;
}

img {
    border-radius: 18px;
    box-shadow: 0 6px 25px rgba(0,0,0,0.7);
    transition: transform 0.4s ease;
}

img:hover {
    transform: scale(1.08);
}

/* Movie names under posters */
.caption {
    font-weight: bold;
    font-size: 1rem;
    color: #f0f0f0;
    margin-top: 8px;
    text-shadow: 2px 2px 4px black;
}
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

# ===================== BACKEND LOGIC =====================
API_KEY = os.getenv("TMDB_API_KEY", "277d14c25d24db963450644664845953")

def fetch_poster(movie_id):
    """Fetch poster URL from TMDB by movie_id. Returns None if not available."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
        else:
            return None
    except Exception:
        return None

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters

# ===================== LOAD DATA =====================
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# ===================== UI ELEMENTS =====================
st.markdown("<h1>🎬 HeyFlix - Movie Recommender System</h1>", unsafe_allow_html=True)

selected_movie_name = st.selectbox(
    '🎥 Select a movie you like 👇',
    movies['title'].values
)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            if posters[idx]:
                st.image(posters[idx], use_container_width=True)
            else:
                st.write("Poster not available")
            st.markdown(f"<div class='caption'>{names[idx]}</div>", unsafe_allow_html=True)
