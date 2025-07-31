# 🔧 Disable Streamlit file watcher
import os
os.environ["STREAMLIT_DISABLE_WATCHDOG_WARNINGS"] = "1"
os.environ["STREAMLIT_WATCH_FILES"] = "false"
os.environ["PYTHONWARNINGS"] = "ignore"

# ✅ Torch patch
import torch
try:
    torch.classes.__path__ = []
except Exception:
    pass

# ✅ Imports
import warnings
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
import requests
import faiss
import ast
from datetime import datetime
from wordcloud import WordCloud
import networkx as nx
from collections import defaultdict, Counter
import time
import uuid
import re
import torch.nn as nn
import torch.optim as optim
#from fuzzywuzzy import process

# Suppress warnings
warnings.filterwarnings('ignore')

# Streamlit config and styles
st.set_page_config(page_title="🎬 Movie Recommender Pro", layout="wide", page_icon="🎥", initial_sidebar_state="expanded")

# Custom CSS with stunning UI enhancements
st.markdown("""
    <style>
        :root {
            --primary: #1e88e5;
            --secondary: #ff4081;
            --accent: #7c4dff;
            --background: #0f0c29;
            --card: rgba(30, 30, 46, 0.8);
            --text: #ffffff;
            --text-secondary: #b0b0b0;
        }
        
        body, .main { 
            background-color: var(--background);
            color: var(--text);
            font-family: 'Poppins', sans-serif;
            overflow-x: hidden;
        }
        
        /* Glassmorphism effect for cards */
        .glass-card {
            background: var(--card);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.36);
            padding: 20px;
            margin: 15px 0;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        .glass-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(124, 77, 255, 0.4);
        }
        
        /* Feature cards */
        .feature-card {
            background: linear-gradient(135deg, rgba(124, 77, 255, 0.15), rgba(30, 136, 229, 0.15));
            border-radius: 16px;
            padding: 25px;
            margin: 15px 0;
            border: 1px solid rgba(124, 77, 255, 0.3);
            transition: all 0.3s ease;
        }
        
        .feature-card:hover {
            transform: scale(1.02);
            box-shadow: 0 10px 35px rgba(124, 77, 255, 0.25);
        }
        
        /* Gradient buttons */
        .gradient-btn {
            background: linear-gradient(45deg, var(--primary), var(--accent));
            color: white !important;
            border: none;
            border-radius: 50px;
            padding: 10px 25px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        
        .gradient-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
            background: linear-gradient(45deg, var(--accent), var(--primary));
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            padding: 15px 25px;
            margin: 0 5px;
            border-radius: 12px;
            font-weight: 600;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(30, 30, 30, 0.5);
            transform: translateY(-3px);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(45deg, var(--primary), var(--accent));
            color: white;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
            border: none;
        }
        
        /* Input fields */
        .stTextInput>div>div>input, 
        .stSelectbox>div>div>select,
        .stTextArea>div>div>textarea {
            background: rgba(30, 30, 46, 0.6) !important;
            color: var(--text) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            padding: 12px 15px !important;
        }
        
        /* Slider styling */
        .stSlider>div>div>div>div {
            background: linear-gradient(90deg, var(--primary), var(--accent)) !important;
        }
        
        /* Progress bar */
        .stProgress>div>div>div>div {
            background: linear-gradient(90deg, var(--primary), var(--accent)) !important;
        }
        
        /* Custom movie card */
        .movie-card {
            background: var(--card);
            border-radius: 16px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            border-left: 4px solid var(--accent);
            position: relative;
            overflow: hidden;
        }
        
        .movie-card:before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary), var(--accent));
        }
        
        .movie-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
        }
        
        .tag {
            display: inline-block;
            background: rgba(124, 77, 255, 0.2);
            border-radius: 20px;
            padding: 6px 15px;
            margin-right: 8px;
            margin-bottom: 8px;
            font-size: 0.85rem;
            color: var(--text);
            border: 1px solid rgba(124, 77, 255, 0.3);
        }
        
        .similarity-bar {
            height: 8px;
            background: linear-gradient(90deg, var(--secondary), var(--accent));
            border-radius: 4px;
            margin: 12px 0;
        }
        
        /* Neon title */
        .neon-title {
            text-shadow: 0 0 10px var(--primary), 
                         0 0 20px var(--primary), 
                         0 0 30px var(--accent);
            animation: flicker 1.5s infinite alternate;
        }
        
        @keyframes flicker {
            0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% {
                text-shadow: 0 0 10px var(--primary),
                             0 0 20px var(--primary),
                             0 0 30px var(--accent),
                             0 0 40px var(--accent),
                             0 0 70px var(--accent),
                             0 0 80px var(--accent),
                             0 0 100px var(--accent),
                             0 0 150px var(--accent);
            }
            20%, 24%, 55% {
                text-shadow: none;
            }
        }
        
        /* Animated background */
        .animated-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1e1e1e);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
        }
        
        @keyframes gradientBG {
            0% { background-position: 0% 50% }
            50% { background-position: 100% 50% }
            100% { background-position: 0% 50% }
        }
        
        /* Particle background */
        .particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            pointer-events: none;
        }
        
        .particle {
            position: absolute;
            border-radius: 50%;
            background: rgba(124, 77, 255, 0.3);
            animation: float 15s infinite linear;
        }
        
        @keyframes float {
            0% {
                transform: translateY(0) translateX(0) rotate(0deg);
                opacity: 1;
            }
            100% {
                transform: translateY(-1000px) translateX(1000px) rotate(720deg);
                opacity: 0;
            }
        }
        
        /* 3D Poster Effects */
        .poster-container {
            transition: transform 0.5s ease;
            transform-style: preserve-3d;
            perspective: 1000px;
            margin-bottom: 15px;
        }
        
        .poster-container:hover {
            transform: perspective(1000px) rotateY(10deg) rotateX(5deg) translateZ(30px);
        }
        
        .poster-img {
            width: 100%;
            border-radius: 10px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        }
        
        /* Mood filter colors */
        .mood-happy { background: linear-gradient(135deg, #43cea2, #185a9d); }
        .mood-exciting { background: linear-gradient(135deg, #ff5e62, #ff9966); }
        .mood-romantic { background: linear-gradient(135deg, #ff6b6b, #ff8e8e); }
        .mood-thrilling { background: linear-gradient(135deg, #8e2de2, #4a00e0); }
        .mood-thoughtful { background: linear-gradient(135deg, #56ab2f, #a8e063); }
        .mood-calm { background: linear-gradient(135deg, #00c9ff, #92fe9d); }
        
        /* Responsive adjustments */
        @media only screen and (max-width: 768px) {
            .stTabs [data-baseweb="tab"] {
                padding: 12px 15px;
                margin: 5px;
                font-size: 12px;
            }
            
            .movie-card {
                padding: 15px;
            }
        }
    </style>
""", unsafe_allow_html=True)

# Add animated background
st.markdown('<div class="animated-bg"></div>', unsafe_allow_html=True)

# Add particle background
st.markdown("""
    <div class="particles" id="particles"></div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const container = document.getElementById('particles');
            const particleCount = 30;
            
            for (let i = 0; i < particleCount; i++) {
                const particle = document.createElement('div');
                particle.classList.add('particle');
                
                // Random size
                const size = Math.random() * 10 + 2;
                particle.style.width = `${size}px`;
                particle.style.height = `${size}px`;
                
                // Random position
                particle.style.left = `${Math.random() * 100}%`;
                particle.style.top = `${Math.random() * 100}%`;
                
                // Random animation duration
                const duration = Math.random() * 20 + 10;
                particle.style.animationDuration = `${duration}s`;
                
                // Random animation delay
                const delay = Math.random() * 5;
                particle.style.animationDelay = `${delay}s`;
                
                container.appendChild(particle);
            }
        });
    </script>
""", unsafe_allow_html=True)

# --- User Authentication ---
USERS_FILE = "users.csv"
LOGIN_ACTIVITY_FILE = "login_activity.csv"
USER_PROFILES_DIR = "user_profiles"

# Create directories if not exists
os.makedirs(USER_PROFILES_DIR, exist_ok=True)

# --- Initialize session state ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_vector" not in st.session_state:
    st.session_state.user_vector = None
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None
if "hybrid_recs" not in st.session_state:
    st.session_state.hybrid_recs = None
if "content_recs" not in st.session_state:
    st.session_state.content_recs = None
if "cached_data" not in st.session_state:
    st.session_state.cached_data = None

# Define default user preferences structure
DEFAULT_USER_PREFERENCES = {
    'liked_movies': [],
    'disliked_movies': [],
    'preferred_genres': [],
    'watchlist': [],
    'mood_preferences': []
}

if "user_preferences" not in st.session_state:
    st.session_state.user_preferences = DEFAULT_USER_PREFERENCES.copy()

# ----------------- SAVE USER PROFILE -----------------
def save_user_profile(username):
    profile_path = os.path.join(USER_PROFILES_DIR, f"{username}_profile.pkl")
    profile_data = {
        'user_vector': st.session_state.user_vector,
        'user_preferences': st.session_state.user_preferences
    }
    with open(profile_path, 'wb') as f:
        pickle.dump(profile_data, f)

# ----------------- LOAD USER PROFILE -----------------
def load_user_profile(username):
    profile_path = os.path.join(USER_PROFILES_DIR, f"{username}_profile.pkl")
    if os.path.exists(profile_path):
        with open(profile_path, 'rb') as f:
            profile_data = pickle.load(f)
        
        # Ensure all preference keys exist
        loaded_prefs = profile_data.get('user_preferences', {})
        for key in DEFAULT_USER_PREFERENCES:
            if key not in loaded_prefs:
                loaded_prefs[key] = DEFAULT_USER_PREFERENCES[key]
                
        st.session_state.user_vector = profile_data['user_vector']
        st.session_state.user_preferences = loaded_prefs
        return True
    return False

# ----------------- SAVE LOGIN ACTIVITY -----------------
def save_login_activity(username):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if os.path.exists(LOGIN_ACTIVITY_FILE):
        logs = pd.read_csv(LOGIN_ACTIVITY_FILE)
    else:
        logs = pd.DataFrame(columns=["Username", "Timestamp"])

    new_entry = pd.DataFrame({"Username": [username], "Timestamp": [now]})
    logs = pd.concat([logs, new_entry], ignore_index=True)
    logs.to_csv(LOGIN_ACTIVITY_FILE, index=False)

# ----------------- USER VALIDATION -----------------
def validate_user(username, password):
    if not os.path.exists(USERS_FILE):
        return False
    df = pd.read_csv(USERS_FILE)
    return ((df['username'] == username) & (df['password'] == password)).any()

# ----------------- USER REGISTRATION -----------------
def register_user(username, password):
    if os.path.exists(USERS_FILE):
        df = pd.read_csv(USERS_FILE)
        if username in df['username'].values:
            return False
    else:
        df = pd.DataFrame(columns=["username", "password"])

    new_user = pd.DataFrame({"username": [username], "password": [password]})
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USERS_FILE, index=False)
    return True

# --- Load Model/Data with Performance Optimization ---
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')
_model = load_model()

@st.cache_data(ttl=3600*24)  # Cache for 24 hours
def fetch_movie_details(movie_id, api_key = st.secrets["TMDB_API_KEY"]):
    """Fetch detailed movie info including credits"""
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&append_to_response=credits"
        data = requests.get(url).json()
        
        # Extract director
        director = "Unknown"
        if 'credits' in data and 'crew' in data['credits']:
            for person in data['credits']['crew']:
                if person['job'] == 'Director':
                    director = person['name']
                    break
        
        # Extract top 3 actors
        actors = []
        if 'credits' in data and 'cast' in data['credits']:
            cast = data['credits']['cast']
            actors = [person['name'] for person in cast[:3]]
        
        # Extract genres
        genres = []
        if 'genres' in data:
            genres = [g['name'] for g in data['genres']]
        
        # ADD POSTER PATH
        poster_path = data.get('poster_path', None)
        
        return {
            'id': movie_id,
            'title': data.get('title', 'Unknown Title'),
            'release_date': data.get('release_date', ''),
            'overview': data.get('overview', 'No overview available.'),
            'vote_average': data.get('vote_average', 0),
            'vote_count': data.get('vote_count', 0),
            'popularity': data.get('popularity', 0),
            'budget': data.get('budget', 0),
            'genres': ', '.join(genres),
            'director': director,
            'actors': actors,
            'poster_path': poster_path,  # ADD THIS
            'original_language': data.get('original_language', 'en')  # NEW: Track language
        }
    except Exception as e:
        st.error(f"Error fetching details for movie {movie_id}: {str(e)}")
        return None

# UPDATED: Fetch both Hollywood and Bollywood movies
@st.cache_data(ttl=3600*24)  # Cache for 24 hours
def fetch_popular_movies_by_year(years, api_key = st.secrets["TMDB_API_KEY"], movies_per_year=50):
    """Fetch popular movies for multiple years with minimal data"""
    all_movies = []
    for year in years:
        try:
            # Fetch Hollywood movies
            url = f"https://api.themoviedb.org/3/discover/movie"
            params = {
                'api_key': api_key,
                'primary_release_year': year,
                'sort_by': 'popularity.desc',
                'page': 1
            }
            response = requests.get(url, params=params).json()
            movies = response.get('results', [])[:movies_per_year]
            all_movies.extend([{
                'id': m['id'],
                'title': m.get('title', 'Unknown Title'),
                'release_date': m.get('release_date', f'{year}-01-01'),
                'poster_path': m.get('poster_path', None),
                'is_bollywood': False  # NEW: Flag for Hollywood movies
            } for m in movies])
            
            # NEW: Fetch Bollywood movies
            bollywood_params = {
                'api_key': api_key,
                'primary_release_year': year,
                'sort_by': 'popularity.desc',
                'page': 1,
                'with_original_language': 'hi'  # Hindi language
            }
            bollywood_response = requests.get(url, params=bollywood_params).json()
            bollywood_movies = bollywood_response.get('results', [])[:min(20, movies_per_year//2)]
            all_movies.extend([{
                'id': m['id'],
                'title': m.get('title', 'Unknown Title'),
                'release_date': m.get('release_date', f'{year}-01-01'),
                'poster_path': m.get('poster_path', None),
                'is_bollywood': True  # NEW: Flag for Bollywood movies
            } for m in bollywood_movies])
            
        except Exception as e:
            st.error(f"Error fetching movies for {year}: {str(e)}")
    
    return all_movies

@st.cache_data
def load_data():
    # Show loading progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.text("Loading movie data... 0%")
    
    # Fetch popular movies by year (2000-2025) - now includes Bollywood
    years = list(range(2000, 2026))
    movies_list = fetch_popular_movies_by_year(years, movies_per_year=50)
    total_movies = len(movies_list)
    
    # Fetch details for each movie with progress
    detailed_movies = []
    for i, movie in enumerate(movies_list):
        details = fetch_movie_details(movie['id'])
        if details:
            # Add Bollywood flag to details
            details['is_bollywood'] = movie.get('is_bollywood', False)
            detailed_movies.append(details)
        
        # Update progress every 5 movies
        if i % 5 == 0:
            progress = (i + 1) / total_movies
            progress_bar.progress(progress)
            status_text.text(f"Loading movie data... {int(progress*100)}%")
    
    # Create DataFrame
    movies_df = pd.DataFrame(detailed_movies)
    
    # Load ratings data
    ratings_df = pd.read_csv('ratings.csv')
    
    # Precompute TF-IDF and similarity
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(movies_df['overview'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    indices = pd.Series(movies_df.index, index=movies_df['title']).drop_duplicates()
    
    # Generate embeddings
    embeddings = _model.encode(movies_df['genres'].tolist(), show_progress_bar=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    
    # Add weighted score
    v = movies_df['vote_count'].fillna(0)
    R = movies_df['vote_average'].fillna(0)
    C = movies_df['vote_average'].mean()
    m = movies_df['vote_count'].quantile(0.60)
    movies_df['weighted_score'] = ((v / (v + m)) * R) + ((m / (v + m)) * C)
    
    # Create genre set
    genre_set = set()
    for genres in movies_df['genres']:
        if isinstance(genres, str):
            for genre in genres.split(', '):
                genre_set.add(genre.strip())
    
    # Add Bollywood as a genre
    genre_set.add("Bollywood")
    
    # Complete progress
    progress_bar.progress(1.0)
    status_text.text("Data loaded successfully!")
    time.sleep(1)
    progress_bar.empty()
    status_text.empty()
    
    return movies_df, ratings_df, {
        'tfidf_matrix': tfidf_matrix,
        'cosine_sim': cosine_sim,
        'indices': indices,
        'embeddings': embeddings,
        'faiss_index': index,
        'genre_set': sorted(genre_set)
    }

# Use the loader
if st.session_state.cached_data is None:
    with st.spinner("Loading movie data. This may take a few minutes..."):
        movies_df, ratings_df, precomputed = load_data()
        st.session_state.cached_data = (movies_df, ratings_df, precomputed)
else:
    movies_df, ratings_df, precomputed = st.session_state.cached_data

# ----------------- MOVIE POSTER DISPLAY -----------------
def display_poster(poster_path, class_name="poster-container", width=200):
    """Display movie poster with 3D effect using HTML/CSS"""
    if poster_path:
        try:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            st.markdown(
                f"""
                <div class="{class_name}" style="width:{width}px">
                    <img src="{poster_url}" class="poster-img" alt="Movie Poster">
                </div>
                """,
                unsafe_allow_html=True
            )
            return True
        except Exception as e:
            st.error(f"Error displaying poster: {str(e)}")
    # Show placeholder if no poster found
    st.markdown(
        f"""
        <div class="{class_name}" style="width:{width}px">
            <div style="background:#333; border-radius:10px; width:100%; height:300px; display:flex; align-items:center; justify-content:center;">
                <span style="color:#aaa; text-align:center;">No Poster<br>Available</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    return False

# Format currency
def format_currency(amount):
    if pd.isna(amount) or amount <= 0:
        return "N/A"
    return f"${amount:,.0f}"

# ----------------- USER PROFILE MANAGEMENT -----------------
def initialize_user_profile(username):
    if not load_user_profile(username):
        # Create new profile
        st.session_state.user_vector = np.zeros(384)
        st.session_state.user_preferences = DEFAULT_USER_PREFERENCES.copy()
        save_user_profile(username)

# ----------------- UPDATE USER PREFERENCES -----------------
def update_user_preference(movie_id, action):
    movie_title = movies_df[movies_df['id'] == movie_id]['title'].values[0]
    
    if action == 'like':
        if movie_title in st.session_state.user_preferences['disliked_movies']:
            st.session_state.user_preferences['disliked_movies'].remove(movie_title)
        if movie_title not in st.session_state.user_preferences['liked_movies']:
            st.session_state.user_preferences['liked_movies'].append(movie_title)
            
    elif action == 'dislike':
        if movie_title in st.session_state.user_preferences['liked_movies']:
            st.session_state.user_preferences['liked_movies'].remove(movie_title)
        if movie_title not in st.session_state.user_preferences['disliked_movies']:
            st.session_state.user_preferences['disliked_movies'].append(movie_title)
    
    # Update user vector
    match = movies_df[movies_df['id'] == movie_id]
    if not match.empty:
        movie_idx = match.index[0]
        movie_embedding = precomputed['embeddings'][movie_idx]
        
        if action == 'like':
            if st.session_state.user_vector is None:
                st.session_state.user_vector = movie_embedding
            else:
                st.session_state.user_vector = st.session_state.user_vector * 0.7 + movie_embedding * 0.3
        elif action == 'dislike':
            if st.session_state.user_vector is not None:
                st.session_state.user_vector = st.session_state.user_vector * 0.9 - movie_embedding * 0.1
    
    # Save updated profile
    save_user_profile(st.session_state.username)

# ----------------- UPDATE WATCHLIST -----------------
def update_watchlist(movie_id, action):
    movie_title = movies_df[movies_df['id'] == movie_id]['title'].values[0]
    
    if action == 'add':
        if movie_title not in st.session_state.user_preferences['watchlist']:
            st.session_state.user_preferences['watchlist'].append(movie_title)
            st.success(f"✅ Added {movie_title} to your watchlist!")
    elif action == 'remove':
        if movie_title in st.session_state.user_preferences['watchlist']:
            st.session_state.user_preferences['watchlist'].remove(movie_title)
            st.success(f"✅ Removed {movie_title} from your watchlist!")
    
    # Save updated profile
    save_user_profile(st.session_state.username)

# ----------------- DEEP LEARNING MODEL -----------------
@st.cache_resource
def train_dl_model():
    from surprise import Dataset, Reader, SVD
    from surprise.model_selection import train_test_split

    reader = Reader(rating_scale=(0.5, 5))
    data = Dataset.load_from_df(ratings_df[['userId', 'movieId', 'rating']], reader)
    trainset, _ = train_test_split(data, test_size=0.2, random_state=42)

    model = SVD(n_factors=50, n_epochs=10, lr_all=0.01, reg_all=0.02)
    model.fit(trainset)
    return model

# Load DL model
dl_model = train_dl_model()

# ----------------- HYBRID RECOMMENDER -----------------
def advanced_hybrid_recommendation(title=None, user_id=None, top_n=10, selected_genres=None, 
                                  sort_by="latest", actor_director=None, mood=None):
    # If no title provided, use user preferences or default to popular movies
    if title is None:
        # If user has preferences, find similar to user vector
        if st.session_state.user_vector is not None and not np.all(st.session_state.user_vector == 0):
            # Search for similar movies to user vector
            query_vector = st.session_state.user_vector.reshape(1, -1)
            _, indices = precomputed['faiss_index'].search(query_vector, top_n*3)
            
            # Get movie details
            results = movies_df.iloc[indices[0]]
            
            # Apply genre filter
            if selected_genres:
                results = results[results['genres'].apply(lambda g: any(genre in g for genre in selected_genres))]
            
            # Sort by release date
            if sort_by == "latest":
                results = results.sort_values("release_date", ascending=False)
            elif sort_by == "oldest":
                results = results.sort_values("release_date", ascending=True)
                
            return results.head(top_n)
        else:
            # Default to popular movies if no preferences
            results = movies_df.sort_values('weighted_score', ascending=False)
            
            # Apply genre filter
            if selected_genres:
                results = results[results['genres'].apply(lambda g: any(genre in g for genre in selected_genres))]
            
            # Sort by release date
            if sort_by == "latest":
                results = results.sort_values("release_date", ascending=False)
            elif sort_by == "oldest":
                results = results.sort_values("release_date", ascending=True)
                
            return results.head(top_n)
    
    # Validate movie title exists
    if title not in precomputed['indices']:
        return pd.DataFrame()
    
    idx = precomputed['indices'][title]
    sim_scores = list(enumerate(precomputed['cosine_sim'][idx]))
    
    # Collaborative filtering predictions
    if user_id:
        predictions = []
        for i, row in movies_df.iterrows():
            pred = dl_model.predict(user_id, row['id'])
            predictions.append((i, pred.est))
    else:
        predictions = [(i, 0) for i in range(len(movies_df))]
    
    # Combine scores
    combined = []
    max_content = max(score for _, score in sim_scores)
    max_collab = max(score for _, score in predictions) if user_id else 1
    
    for (i, content_score), (_, collab_score) in zip(sim_scores, predictions):
        if user_id:
            combined_score = (0.6 * (content_score / max_content)) + (0.4 * (collab_score / max_collab))
        else:
            combined_score = content_score / max_content
        combined.append((i, combined_score))
    
    # Sort and get top recommendations
    combined.sort(key=lambda x: x[1], reverse=True)
    top_indices = [i[0] for i in combined[1:top_n*2]]  # Get extra for filtering
    results = movies_df.iloc[top_indices]
    
    # Apply genre filter
    if selected_genres:
        results = results[results['genres'].apply(lambda g: any(genre in g for genre in selected_genres))]
    
    # Apply actor/director filter
    if actor_director:
        # Search for actor or director name
        results = results[
            (results['director'].str.contains(actor_director, case=False)) |
            (results['actors'].apply(lambda x: any(actor_director.lower() in actor.lower() for actor in x) if isinstance(x, list) else False))
        ]
    
    # Apply mood filter
    if mood:
        mood_mapping = {
            'happy': ['Comedy', 'Animation', 'Family', 'Music'],
            'exciting': ['Action', 'Adventure', 'Thriller', 'Science Fiction'],
            'romantic': ['Romance', 'Drama'],
            'thrilling': ['Horror', 'Mystery', 'Thriller'],
            'thoughtful': ['Drama', 'History', 'Documentary'],
            'calm': ['Drama', 'Romance', 'Family']
        }
        mood_genres = mood_mapping.get(mood, [])
        if mood_genres:
            results = results[results['genres'].apply(lambda g: any(genre in g for genre in mood_genres))]
    
    # Sort by release date
    if sort_by == "latest":
        results = results.sort_values("release_date", ascending=False)
    elif sort_by == "oldest":
        results = results.sort_values("release_date", ascending=True)
        
    return results.head(top_n)

# ----------------- LOG EVENTS -----------------
def log_event(user, movie, action):
    os.makedirs('user_data', exist_ok=True)
    log_file = f'user_data/{user}_log.csv'
    
    if not os.path.exists(log_file):
        with open(log_file, 'w') as f:
            f.write("Timestamp,Movie,Action\n")
    
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now()},{movie},{action}\n")

# ----------------- MOVIE CARD COMPONENT -----------------
def movie_card(movie, show_feedback=True, context="default", index=0, similarity=None):
    with st.container():
        # Add Bollywood tag if applicable
        bollywood_tag = ""
        if movie.get('is_bollywood', False):
            bollywood_tag = "<span class='tag' style='background:rgba(255, 215, 0, 0.2);border:1px solid gold;'>Bollywood</span>"
        
        st.markdown(f"<div class='movie-card'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            # Use poster_path directly from movie data
            display_poster(movie.get('poster_path'), class_name="poster-container")
        
        with col2:
            st.subheader(movie['title'])
            st.markdown(bollywood_tag, unsafe_allow_html=True)
            
            # Use director from movie data
            director = movie.get('director', 'Unknown')
            st.markdown(f"🎬 **Director:** {director}")
            
            # Safely handle actors field
            actors = movie.get('actors', [])
            if isinstance(actors, list) and len(actors) > 0:
                st.markdown(f"👥 **Cast:** {', '.join(actors)}")
                
            st.caption(f"⭐ {movie['vote_average']} | 🗳️ {movie['vote_count']} votes | 📅 {movie['release_date']}")
            
            # Display genres as tags
            genres = movie['genres'].split(', ') if isinstance(movie['genres'], str) else []
            genre_tags = " ".join([f"<span class='tag'>{genre}</span>" for genre in genres])
            st.markdown(f"<div style='margin: 10px 0;'>{genre_tags}</div>", unsafe_allow_html=True)
            
            # Display similarity bar if available
            if similarity is not None:
                st.markdown(f"<div class='similarity-bar' style='width: {similarity*100}%'></div>", unsafe_allow_html=True)
                st.caption(f"Match: {similarity*100:.1f}%")
            
            # Use budget from movie data
            budget = movie.get('budget', 0)
            st.write(f"💰 Budget: {format_currency(budget)}")
            
            # Use overview from movie data
            overview = movie.get('overview', 'No overview available.')
            st.write(overview[:200] + "...")
            
            if show_feedback and st.session_state.logged_in:
                c1, c2, c3 = st.columns(3)
                unique_key_like = f"{context}_like_{movie['id']}_{index}_{uuid.uuid4().hex[:6]}"
                unique_key_dislike = f"{context}_dislike_{movie['id']}_{index}_{uuid.uuid4().hex[:6]}"
                unique_key_watchlist = f"{context}_watchlist_{movie['id']}_{index}_{uuid.uuid4().hex[:6]}"
                
                with c1:
                    if st.button("👍 Like", key=unique_key_like, use_container_width=True):
                        log_event(st.session_state.username, movie['title'], "liked")
                        update_user_preference(movie['id'], 'like')
                        st.rerun()
                with c2:
                    if st.button("👎 Dislike", key=unique_key_dislike, use_container_width=True):
                        log_event(st.session_state.username, movie['title'], "disliked")
                        update_user_preference(movie['id'], 'dislike')
                        st.rerun()
                with c3:
                    # Safely access watchlist with default
                    watchlist = st.session_state.user_preferences.get('watchlist', [])
                    if movie['title'] in watchlist:
                        if st.button("❌ Remove Watchlist", key=unique_key_watchlist, use_container_width=True):
                            update_watchlist(movie['id'], 'remove')
                            st.rerun()
                    else:
                        if st.button("➕ Add to Watchlist", key=unique_key_watchlist, use_container_width=True):
                            update_watchlist(movie['id'], 'add')
                            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# ----------------- FIND MOVIE BY TITLE -----------------
def find_movie_by_title(title, movies_df):
    # Exact match
    if title in movies_df['title'].values:
        return title
    
    # Fuzzy match
    matches = movies_df[movies_df['title'].str.contains(title, case=False)]
    if not matches.empty:
        return matches.iloc[0]['title']
    
    # Try fuzzy matching
    all_titles = movies_df['title'].tolist()
    match = process.extractOne(title, all_titles)
    if match and match[1] > 80:  # confidence threshold
        return match[0]
    
    return None

# ----------------- TRENDING MOVIES -----------------
@st.cache_data(ttl=3600)  # cache for 1 hour
def get_trending_movies():
    return movies_df.sort_values('weighted_score', ascending=False).head(10)

# ----------------- GET USER PREFERRED GENRES -----------------
def get_user_preferred_genres():
    liked_movies = st.session_state.user_preferences.get('liked_movies', [])
    all_genres = []
    
    for movie_title in liked_movies:
        movie_row = movies_df[movies_df['title'] == movie_title]
        if not movie_row.empty:
            genres = movie_row['genres'].iloc[0].split(', ') if isinstance(movie_row['genres'].iloc[0], str) else []
            all_genres.extend(genres)
    
    # Count genres and get top 3
    if all_genres:
        counter = Counter(all_genres)
        return [genre for genre, _ in counter.most_common(3)]
    return []

# ----------------- GET MOVIES BY ACTOR/DIRECTOR -----------------
@st.cache_data(ttl=24*3600, show_spinner=False)  # Cache for 24 hours
def get_movies_by_actor_director(name):
    # Search for actor in cast or director
    movies = movies_df[
        (movies_df['director'].str.contains(name, case=False)) |
        (movies_df['actors'].apply(lambda x: any(name.lower() in actor.lower() for actor in x) if isinstance(x, list) else False))
    ]
    return movies

# ----------------- MAIN APP -----------------
def main():
    if not st.session_state.logged_in:
        login_or_signup()
    else:
        st.markdown(f'<h1 class="neon-title">🎬 Movie Recommender Pro</h1>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: center; margin-bottom: 30px;">Welcome back, <strong>{st.session_state.username}</strong>!</div>', unsafe_allow_html=True)
        
        tabs = st.tabs([
            "🏠 Home",
            "🔍 Search",
            "📊 Popular",
            "🎯 Genre Filter",
            "🎬 Latest Releases",
            "📈 Analytics",
            "🎭 Actor/Director",
            "💡 Hybrid",
            "🤖 Deep Learning",
            "👤 Profile"
        ])

        # Tab 0 - Home - COMPLETELY REDESIGNED
        with tabs[0]:
            # Project description expander - UPDATED WITH NEW FEATURES
            with st.expander("🌟 About Movie Recommender Pro", expanded=True):
                st.markdown("""
                <div style="padding: 20px; border-radius: 15px; background: linear-gradient(135deg, rgba(30, 136, 229, 0.2), rgba(124, 77, 255, 0.2));">
                    <h3 style="color: #7c4dff; text-align: center;">Discover Your Next Favorite Movie!</h3>
                    <p style="font-size: 1.1rem; text-align: center;">Movie Recommender Pro uses advanced AI algorithms to find perfect movie matches based on your unique preferences. Our hybrid recommendation system combines multiple techniques to deliver personalized suggestions for both Hollywood and Bollywood movies.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Feature showcase - UPDATED WITH NEW FEATURES
                st.subheader("✨ Key Features")
                
                # Feature cards in columns - ADDED BOLLYWOOD AND OTHER FEATURES
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    <div class="feature-card">
                        <h4>🔍 Smart Search</h4>
                        <p>Find movies by title, genre, or keywords with fuzzy matching</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="feature-card">
                        <h4>🤖 AI Recommendations</h4>
                        <p>Deep learning models personalize suggestions based on your taste</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="feature-card">
                        <h4>💡 Hybrid System</h4>
                        <p>Combines content-based and collaborative filtering for better results</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="feature-card">
                        <h4>🎭 Bollywood & Hollywood</h4>
                        <p>Extensive collection from both industries</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="feature-card">
                        <h4>🎬 Actor/Director Search</h4>
                        <p>Find movies by your favorite actors or directors</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with col2:
                    st.markdown("""
                    <div class="feature-card">
                        <h4>😊 Mood-Based Filtering</h4>
                        <p>Get recommendations based on your current mood</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="feature-card">
                        <h4>🆕 Latest Releases</h4>
                        <p>Stay updated with the newest movie releases</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="feature-card">
                        <h4>📊 Visual Analytics</h4>
                        <p>Explore movie trends, ratings, and genre distributions</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="feature-card">
                        <h4>👤 Personal Profile</h4>
                        <p>Track your liked/disliked movies and preferences</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="feature-card">
                        <h4>🎯 Genre Filtering</h4>
                        <p>Discover movies by specific genres or combinations</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Bollywood section - FIXED TO ACTUALLY SHOW BOLLYWOOD MOVIES
            st.markdown("### 🎬 Bollywood Spotlight")
            bollywood_movies = movies_df[movies_df['is_bollywood'] == True].sort_values('weighted_score', ascending=False).head(10)
            
            if not bollywood_movies.empty:
                cols = st.columns(5)
                for idx, (_, row) in enumerate(bollywood_movies.iterrows()):
                    with cols[idx % 5]:
                        display_poster(row.get('poster_path'), class_name="poster-container", width=150)
                        st.caption(f"**{row['title']}**")
                        st.progress(row['weighted_score'] / 10, text=f"⭐ {row['vote_average']}")
            else:
                st.info("No Bollywood movies available at the moment")
            
            # Trending movies section
            st.markdown("### 🔥 Trending This Week")
            trending = get_trending_movies()
            cols = st.columns(5)
            for idx, (_, row) in enumerate(trending.iterrows()):
                with cols[idx % 5]:
                    display_poster(row.get('poster_path'), class_name="poster-container", width=150)
                    
                    st.caption(f"**{row['title']}**")
                    st.progress(row['weighted_score'] / 10, text=f"⭐ {row['vote_average']}")
            
            # Latest releases section
            st.markdown("### 🆕 Latest Releases")
            latest = movies_df.sort_values("release_date", ascending=False).head(5)
            cols = st.columns(5)
            for idx, (_, row) in enumerate(latest.iterrows()):
                with cols[idx % 5]:
                    display_poster(row.get('poster_path'), class_name="poster-container", width=150)
                    
                    st.caption(f"**{row['title']}**")
                    st.caption(f"📅 {row['release_date']}")
            
            # Personalized recommendations section
            st.markdown("### ✨ Recommended For You")
            if st.session_state.user_preferences.get('liked_movies', []):
                try:
                    # Create user ID from username
                    username = st.session_state.username
                    user_id = abs(hash(username)) % 10000
                    
                    # Get personalized recommendations
                    recs_df = movies_df.copy()
                    
                    # Show recommendations
                    cols = st.columns(5)
                    for idx, row in recs_df.sample(5).iterrows():
                        with cols[idx % 5]:
                            display_poster(row.get('poster_path'), class_name="poster-container", width=150)
                            st.caption(f"**{row['title']}**")
                            st.caption(f"⭐ {row['vote_average']}")
                except:
                    st.info("Personalizing recommendations...")
            else:
                st.info("Like some movies to get personalized recommendations")
            
            # Admin Panel
            if st.session_state.username == "Vic":
                with st.expander("🛡️ Admin Panel - User Login Activity", expanded=False):
                    st.markdown("### 👨‍💼 User Login Logs")
                    if os.path.exists(LOGIN_ACTIVITY_FILE):
                        logs = pd.read_csv(LOGIN_ACTIVITY_FILE)
                        st.dataframe(logs.sort_values("Timestamp", ascending=False).head(10))
                    else:
                        st.info("No login activity recorded yet.")
                    if st.button("🔄 Refresh Logs"):
                        st.rerun()

        # Tab 1 - Search
        with tabs[1]:
            st.subheader("🔍 Search Movies")
            search_term = st.text_input("Search by title, genre, or keyword")
            
            if search_term:
                # Search by title
                title_results = movies_df[movies_df['title'].str.contains(search_term, case=False)]
                
                # Search by genre
                genre_results = movies_df[movies_df['genres'].str.contains(search_term, case=False)]
                
                # Search by keyword in overview
                keyword_results = movies_df[movies_df['overview'].str.contains(search_term, case=False)]
                
                # Combine results
                results = pd.concat([title_results, genre_results, keyword_results]).drop_duplicates(subset=["id"])

                
                if not results.empty:
                    st.write(f"🔍 Found {len(results)} matches")
                    for _, row in results.head(20).iterrows():
                        movie_card(row, show_feedback=True, context="search")
                else:
                    st.warning("No movies found matching your search")

        # Tab 2 - Popular
        with tabs[2]:
            st.subheader("📂 Browse Movie Database")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                sort_options = [
                    "Title", "Rating", "Popularity", "Release Date (Newest)", 
                    "Release Date (Oldest)", "Budget (High to Low)", "Budget (Low to High)"
                ]
                sort_by = st.selectbox("Sort by", sort_options, key="popular_sort")
            with col2:
                num_movies = st.slider("Number to display", 10, 100, 20, key="num_movies_slider")
            
            sorted_df = movies_df.copy()
            if sort_by == "Rating":
                sorted_df = sorted_df.sort_values("vote_average", ascending=False)
            elif sort_by == "Popularity":
                sorted_df = sorted_df.sort_values("popularity", ascending=False)
            elif sort_by == "Release Date (Newest)":
                sorted_df = sorted_df.sort_values("release_date", ascending=False)
            elif sort_by == "Release Date (Oldest)":
                sorted_df = sorted_df.sort_values("release_date", ascending=True)
            elif sort_by == "Budget (High to Low)":
                sorted_df = sorted_df.sort_values("budget", ascending=False)
            elif sort_by == "Budget (Low to High)":
                sorted_df = sorted_df.sort_values("budget", ascending=True)
            else:
                sorted_df = sorted_df.sort_values("title")
            
            for _, row in sorted_df.head(num_movies).iterrows():
                movie_card(row, context="browse")

        # Tab 3 - Genre Filter
        with tabs[3]:
            st.subheader("🎯 Discover by Genre")
            selected_genres = st.multiselect("Select genres", precomputed['genre_set'], default=["Action", "Drama", "Bollywood"], key="genre_filter")
            
            if selected_genres:
                filtered = movies_df[movies_df['genres'].apply(lambda g: any(genre in g for genre in selected_genres))]
                st.write(f"🎬 Found {len(filtered)} movies")
                
                view_mode = st.radio("View mode", ["Cards", "Gallery"], horizontal=True, key="genre_view_mode")
                
                if view_mode == "Cards":
                    num_to_show = st.slider("Number to show", 10, len(filtered), min(30, len(filtered)), key="genre_num_slider")
                    for _, row in filtered.head(num_to_show).iterrows():
                        movie_card(row, context="genre")
                else:
                    num_to_show = st.slider("Number to show", 10, 50, 15, key="gallery_slider")
                    cols = st.columns(5)
                    for idx, (_, row) in enumerate(filtered.head(num_to_show).iterrows()):
                        with cols[idx % 5]:
                            display_poster(row['poster_path'], class_name="poster-container", width=150)
                            st.caption(f"**{row['title']}**")
                            st.caption(f"⭐ {row['vote_average']}")
            else:
                st.warning("Please select at least one genre")
        
        # Tab 4 - Latest Releases (Real-time Data Integration)
        with tabs[4]:
            st.subheader("🎬 Latest Movie Releases")
            
            # Genre filter
            selected_genres = st.multiselect("Filter by genres", precomputed['genre_set'], key="latest_genre_filter")
            
            # Year selector
            selected_year = st.selectbox("Select Year", list(range(2018, 2026)), index=2024-2018)
            
            # Filter movies by selected year
            current_year_movies = movies_df[
                (movies_df['release_date'].str.startswith(str(selected_year))) | 
                (movies_df['release_date'].str.contains(f"^{selected_year}-", na=False))
            ]
            
            # Apply genre filter
            if selected_genres:
                # Create a filter function that checks if any selected genre is in the movie's genres
                def genre_filter(genres):
                    if not isinstance(genres, str):
                        return False
                    return any(genre.strip() in selected_genres for genre in genres.split(','))
                
                current_year_movies = current_year_movies[current_year_movies['genres'].apply(genre_filter)]
            
            if not current_year_movies.empty:
                st.markdown(f"### 🎉 Movies of {selected_year} ({len(current_year_movies)} found)")
                
                # Sort by release date (newest first)
                current_year_movies = current_year_movies.sort_values("release_date", ascending=False)
                
                # Show movie cards with budgets
                for _, row in current_year_movies.iterrows():
                    movie_card(row, context="latest", show_feedback=True)
            else:
                st.warning(f"No movies found for {selected_year} with selected genres. Try different filters.")
        
        # Tab 5 - Analytics      
        with tabs[5]:
            st.subheader("📊 Movie Analytics Dashboard")
            
            tab1, tab2, tab3 = st.tabs(["Genre Analysis", "Rating Insights", "Word Cloud"])
            
            with tab1:
                st.subheader("🎭 Genre Distribution")
                genre_count = defaultdict(int)
                # Create a set to store all unique genres
                all_genres = set()
                
                for g_list in movies_df['genres']:
                    if isinstance(g_list, str):
                        for genre in g_list.split(', '):
                            clean_genre = genre.strip()
                            if clean_genre:
                                genre_count[clean_genre] += 1
                                all_genres.add(clean_genre)
                
                # Create DataFrame from genre_count
                genre_df = pd.DataFrame(list(genre_count.items()), columns=['Genre', 'Count'])
                genre_df = genre_df.sort_values('Count', ascending=False)
                
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.barplot(x='Count', y='Genre', data=genre_df.head(15), palette="viridis", ax=ax)
                ax.set_title("Top 15 Movie Genres")
                st.pyplot(fig)

            
            with tab2:
                st.subheader("⭐ Rating Insights")
                fig, ax = plt.subplots(1, 2, figsize=(14, 5))
                
                # Rating histogram
                sns.histplot(movies_df['vote_average'].dropna(), bins=20, kde=True, ax=ax[0], color='skyblue')
                ax[0].set_title("Vote Average Distribution")
                ax[0].set_xlabel("Rating")
                ax[0].set_ylabel("Frequency")
                
                # Rating vs. Budget
                budget_movies = movies_df[movies_df['budget'] > 0]
                sample_size = min(500, len(budget_movies))
                budget_sample = budget_movies.sample(sample_size)
                sns.scatterplot(x='vote_average', y='budget', data=budget_sample, ax=ax[1], alpha=0.6)
                ax[1].set_title("Rating vs. Budget")
                ax[1].set_xlabel("Rating")
                ax[1].set_ylabel("Budget (Millions)")
                ax[1].set_yscale('log')
                
                st.pyplot(fig)
            
            with tab3:
                st.subheader("☁️ Overview Word Cloud")
                text = " ".join(movies_df['overview'].dropna().astype(str))
                
                if text:
                    wordcloud = WordCloud(width=800, height=400, background_color='black').generate(text)
                    fig, ax = plt.subplots(figsize=(12, 8))
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis('off')
                    st.pyplot(fig)
                else:
                    st.warning("No overview text available")
        
        # Tab 6 - Actor/Director Recommendations
        with tabs[6]:
            st.subheader("🎭 Find Movies by Actor or Director")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                search_name = st.text_input("Enter actor or director name", key="actor_director_search")
            with col2:
                num_results = st.slider("Number of results", 5, 50, 10, key="actor_num_slider")
            
            if search_name:
                with st.spinner(f"Searching for movies with {search_name}..."):
                    results = get_movies_by_actor_director(search_name)
                
                if not results.empty:
                    st.success(f"🎬 Found {len(results)} movies featuring {search_name}")
                    
                    # Sort by popularity
                    results = results.sort_values('popularity', ascending=False)
                    
                    # Display results
                    for _, row in results.head(num_results).iterrows():
                        movie_card(row, context="actor", show_feedback=True)
                else:
                    st.warning(f"No movies found with {search_name}")
        
        # Tab 7 - Hybrid Recommendations
        with tabs[7]:
            st.subheader("💡 Hybrid Recommendations")
            st.info("Combines content-based filtering with collaborative filtering for personalized results")
            
            # Movie type selection
            selected_types = st.multiselect("Filter by movie types", precomputed['genre_set'], default=["Action", "Bollywood"], key="hybrid_type_filter")
            
            # Optional movie search
            movie_search = st.text_input("🎬 Enter a movie name (optional)", key="hybrid_movie_search", placeholder="Type a movie name...")
            
            # Actor/Director filter
            actor_director = st.text_input("👤 Filter by actor or director (optional)", key="hybrid_actor_director")
            
            # Mood filter
            mood_options = ["Happy 😊", "Exciting 🚀", "Romantic 💕", "Thrilling 😱", "Thoughtful 🤔", "Calm 😌"]
            mood = st.selectbox("😊 Filter by mood (optional)", ["None"] + mood_options, key="hybrid_mood")
            mood_mapping = {
                "Happy 😊": "happy",
                "Exciting 🚀": "exciting",
                "Romantic 💕": "romantic",
                "Thrilling 😱": "thrilling",
                "Thoughtful 🤔": "thoughtful",
                "Calm 😌": "calm"
            }
            mood_value = mood_mapping.get(mood, None)
            
            # Sorting options
            col1, col2 = st.columns(2)
            with col1:
                sort_by = st.radio("Prioritize", ["Latest", "Oldest"], horizontal=True, key="hybrid_sort")
            with col2:
                top_n = st.slider("🔢 Number of recommendations", 5, 20, 10, key="hybrid_num_slider")

            if st.button("Generate Recommendations", key="hybrid_btn", use_container_width=True):
                with st.spinner("Analyzing patterns..."):
                    time.sleep(0.5)
                    
                    # Improved user ID generation
                    user_id = abs(hash(st.session_state.username)) % 10000
                    
                    # Determine what to recommend
                    recommendation_basis = ""
                    if movie_search:
                        # User entered a movie
                        movie_title = find_movie_by_title(movie_search, movies_df)
                        if not movie_title:
                            st.error("Movie not found. Please try another title.")
                        else:
                            results = advanced_hybrid_recommendation(
                                movie_title,
                                user_id,
                                top_n,
                                selected_types,
                                "latest" if sort_by == "Latest" else "oldest",
                                actor_director,
                                mood_value
                            )
                            
                            recommendation_basis = f"Because you liked **{movie_title}**"
                    else:
                        # No movie entered - use user preferences or popular movies
                        results = advanced_hybrid_recommendation(
                            None,
                            user_id,
                            top_n,
                            selected_types,
                            "latest" if sort_by == "Latest" else "oldest",
                            actor_director,
                            mood_value
                        )
                            
                        if st.session_state.user_preferences.get('liked_movies', []):
                            # Get top 3 preferred genres
                            top_genres = get_user_preferred_genres()
                            if top_genres:
                                genres_str = ", ".join(top_genres)
                                recommendation_basis = f"Based on your preferences for **{genres_str}** genres"
                            else:
                                recommendation_basis = "Based on your movie preferences"
                        else:
                            recommendation_basis = "Popular movies you might enjoy"
                    
                    st.session_state.hybrid_recs = results

                    if not results.empty:
                        # Show recommendation context
                        st.subheader(f"🌟 Recommendations {recommendation_basis}")
                        
                        # Get unique genres from recommendations
                        all_genres = []
                        for _, row in results.iterrows():
                            genres = row['genres'].split(', ') if isinstance(row['genres'], str) else []
                            all_genres.extend(genres)
                        
                        top_genres = [genre for genre, _ in Counter(all_genres).most_common(3)]
                        if top_genres:
                            st.write(f"📊 **Top genres in recommendations:** {', '.join(top_genres)}")
                        
                        # Show recommendations
                        for _, row in results.iterrows():
                            movie_card(row, context="hybrid")
                    else:
                        st.warning("⚠️ No recommendations found matching your criteria")

        # Tab 8 - Deep Learning
        with tabs[8]:
            st.subheader("🤖 Deep Learning Recommendations")
            st.info("Personalized recommendations based on your taste profile")
            
            # Show user preferences context
            if st.session_state.user_preferences.get('liked_movies', []):
                top_genres = get_user_preferred_genres()
                if top_genres:
                    st.write(f"🎯 Based on your preferences for: **{', '.join(top_genres)}**")
            
            # Train DL model on button click
            if st.button("Generate Personalized Recommendations", key="dl_btn", use_container_width=True):
                try:
                    # Create user ID from username
                    username = st.session_state.username
                    user_id = abs(hash(username)) % 10000
                    
                    # Show progress
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    status_text.text("Generating recommendations...")
                    
                    # Get all movie IDs
                    all_movie_ids = movies_df['id'].tolist()
                    total_movies = len(all_movie_ids)
                    
                    # Predict ratings
                    predictions = []
                    for idx, movie_id in enumerate(all_movie_ids):
                        pred = dl_model.predict(user_id, movie_id)
                        predictions.append((movie_id, pred.est))
                        
                        # Update progress
                        if idx % 100 == 0:
                            progress_bar.progress(idx / total_movies)
                    
                    # Sort predictions
                    predictions.sort(key=lambda x: x[1], reverse=True)
                    top_movie_ids = [mid for mid, _ in predictions[:10]]
                    recs_df = movies_df[movies_df['id'].isin(top_movie_ids)]
                    
                    # Complete progress
                    progress_bar.progress(1.0)
                    status_text.empty()
                    progress_bar.empty()
                    
                    st.session_state.dl_recs = recs_df

                    st.subheader("🌟 Personalized For You")
                    if not recs_df.empty:
                        # Show recommendation context
                        liked_movies = st.session_state.user_preferences.get('liked_movies', [])
                        if liked_movies:
                            st.write(f"✨ Based on your likes: **{', '.join(liked_movies[:3])}**")
                        
                        # Show recommendations
                        for i, row in recs_df.iterrows():
                            unique_index = f"{i}_{uuid.uuid4().hex[:6]}"
                            movie_card(row, context="dl", index=unique_index)
                            if "username" in st.session_state:
                                log_event(username, row['title'], "recommended")
                    else:
                        st.warning("No recommendations found. Try rating more movies.")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    
        # Tab 9 - Profile
        with tabs[9]:
            st.subheader(f"👤 {st.session_state.username}'s Profile")

            # User preferences section
            st.markdown("### 🎭 Your Preferences")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 👍 Liked Movies")
                liked_movies = st.session_state.user_preferences.get('liked_movies', [])
                if liked_movies:
                    for movie in liked_movies:
                        st.write(f"- {movie}")
                else:
                    st.info("No liked movies yet")
                    
                # Show top genres based on liked movies
                top_genres = get_user_preferred_genres()
                if top_genres:
                    st.markdown("#### ⭐ Preferred Genres")
                    st.write(", ".join([f"**{genre}**" for genre in top_genres]))
                    
                # Show mood preferences
                mood_prefs = st.session_state.user_preferences.get('mood_preferences', [])
                if mood_prefs:
                    st.markdown("#### 😊 Preferred Moods")
                    st.write(", ".join([f"**{mood}**" for mood in mood_prefs]))

            with col2:
                st.markdown("#### 👎 Disliked Movies")
                disliked_movies = st.session_state.user_preferences.get('disliked_movies', [])
                if disliked_movies:
                    for movie in disliked_movies:
                        st.write(f"- {movie}")
                else:
                    st.info("No disliked movies yet")
                    
                st.markdown("#### 📝 Watchlist")
                watchlist = st.session_state.user_preferences.get('watchlist', [])
                if watchlist:
                    for movie in watchlist:
                        st.write(f"- {movie}")
                else:
                    st.info("Your watchlist is empty")

            # Activity log section
            st.markdown("### 📝 Your Activity")
            log_file = f'user_data/{st.session_state.username}_log.csv'
            if os.path.exists(log_file):
                logs = pd.read_csv(log_file)
                st.dataframe(logs.sort_values("Timestamp", ascending=False).head(10))
            else:
                st.info("No activity recorded yet")

            # Recommendation history
            st.markdown("### 🎬 Recently Recommended")
            if hasattr(st.session_state, 'dl_recs') and not st.session_state.dl_recs.empty:
                cols = st.columns(3)
                for idx, (_, row) in enumerate(st.session_state.dl_recs.head(3).iterrows()):
                    with cols[idx]:
                        display_poster(row['poster_path'], class_name="poster-container", width=150)
                        st.write(f"**{row['title']}**")
                        st.write(f"⭐ {row['vote_average']}")
            else:
                st.info("No recommendations generated yet")
                
            # Logout button
            st.markdown("---")
            if st.button("🔒 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.success("You have been logged out. Please login again.")
                time.sleep(2)
                st.rerun()


# ----------------- LOGIN + SIGNUP FUNCTION -----------------
def login_or_signup():
    st.markdown('<h1 class="neon-title" style="text-align: center;">🎬 Movie Recommender Pro</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### 🔐 Login to Your Account")
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login", key="login_btn", use_container_width=True):
            if login_username == "Vic" and login_password == "Vik":
                st.success("✅ Admin Logged In")
                st.session_state.logged_in = True
                st.session_state.username = login_username
                save_login_activity(login_username)
                initialize_user_profile(login_username)
            elif validate_user(login_username, login_password):
                st.success(f"✅ Welcome {login_username}")
                st.session_state.logged_in = True
                st.session_state.username = login_username
                save_login_activity(login_username)
                initialize_user_profile(login_username)
            else:
                st.error("❌ Invalid Credentials")
    
    with col2:
        st.markdown("### 🎉 Create New Account")
        reg_username = st.text_input("Username", key="reg_user")
        reg_password = st.text_input("Password", type="password", key="reg_pass")
        reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
        
        if st.button("Register", key="reg_btn", use_container_width=True):
            if reg_password != reg_confirm:
                st.error("Passwords do not match")
            elif register_user(reg_username, reg_password):
                st.success("🎉 Signup successful. You are now logged in.")
                st.session_state.logged_in = True
                st.session_state.username = reg_username
                save_login_activity(reg_username)
                initialize_user_profile(reg_username)
            else:
                st.warning("⚠️ Username already exists. Try logging in.")


# ----------------- Run App -----------------
if __name__ == "__main__":
    main()
