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
        /* ... (existing CSS remains unchanged) ... */
    </style>
""", unsafe_allow_html=True)

# Add animated background
st.markdown('<div class="animated-bg"></div>', unsafe_allow_html=True)

# Add particle background
st.markdown("""
    <div class="particles" id="particles"></div>
    <script>
        /* ... (existing JavaScript remains unchanged) ... */
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
def fetch_movie_details(movie_id, api_key="623d4838545cb2f9581d85baa9c89ed8"):
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

# UPDATED: Fetch MORE Bollywood movies
@st.cache_data(ttl=3600*24)  # Cache for 24 hours
def fetch_popular_movies_by_year(years, api_key="623d4838545cb2f9581d85baa9c89ed8", movies_per_year=50):
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
                'is_bollywood': False
            } for m in movies])
            
            # NEW: Fetch MORE Bollywood movies - increased to 40 per year
            bollywood_params = {
                'api_key': api_key,
                'primary_release_year': year,
                'sort_by': 'popularity.desc',
                'page': 1,
                'with_original_language': 'hi'  # Hindi language
            }
            bollywood_response = requests.get(url, params=bollywood_params).json()
            # Get up to 40 Bollywood movies per year
            bollywood_movies = bollywood_response.get('results', [])[:40]
            all_movies.extend([{
                'id': m['id'],
                'title': m.get('title', 'Unknown Title'),
                'release_date': m.get('release_date', f'{year}-01-01'),
                'poster_path': m.get('poster_path', None),
                'is_bollywood': True
            } for m in bollywood_movies])
            
        except Exception as e:
            st.error(f"Error fetching movies for {year}: {str(e)}")
    
    return all_movies

# NEW: Fetch movies by popular Bollywood actors
@st.cache_data(ttl=3600*24)  # Cache for 24 hours
def fetch_movies_by_actor(actor_name, api_key="623d4838545cb2f9581d85baa9c89ed8", max_movies=50):
    """Fetch movies by a specific actor"""
    try:
        # First, search for the actor
        search_url = f"https://api.themoviedb.org/3/search/person?api_key={api_key}&query={actor_name}"
        search_response = requests.get(search_url).json()
        
        if not search_response.get('results'):
            return []
        
        actor_id = search_response['results'][0]['id']
        
        # Get actor's movie credits
        credits_url = f"https://api.themoviedb.org/3/person/{actor_id}/movie_credits?api_key={api_key}"
        credits_response = requests.get(credits_url).json()
        
        movies = []
        for movie in credits_response.get('cast', [])[:max_movies]:
            movies.append({
                'id': movie['id'],
                'title': movie.get('title', 'Unknown Title'),
                'release_date': movie.get('release_date', ''),
                'poster_path': movie.get('poster_path', None),
                'is_bollywood': True
            })
        
        return movies
        
    except Exception as e:
        st.error(f"Error fetching movies for actor {actor_name}: {str(e)}")
        return []

@st.cache_data
def load_data():
    # Show loading progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.text("Loading movie data... 0%")
    
    # Fetch popular movies by year (2000-2025) - now includes Bollywood
    years = list(range(2000, 2026))
    movies_list = fetch_popular_movies_by_year(years, movies_per_year=50)
    
    # NEW: Add movies from popular Bollywood actors
    popular_actors = [
        "Shah Rukh Khan", "Aamir Khan", "Salman Khan", "Akshay Kumar", "Hrithik Roshan",
        "Ranbir Kapoor", "Ranveer Singh", "Deepika Padukone", "Priyanka Chopra", "Alia Bhatt",
        "Katrina Kaif", "Kareena Kapoor", "Ajay Devgn", "Varun Dhawan", "Ayushmann Khurrana"
    ]
    
    status_text.text("Adding popular Bollywood actors...")
    for actor in popular_actors:
        actor_movies = fetch_movies_by_actor(actor)
        movies_list.extend(actor_movies)
        # Update progress
        progress = (popular_actors.index(actor) + 1) / len(popular_actors)
        progress_bar.progress(progress)
        status_text.text(f"Loading {actor} movies... {int(progress*100)}%")
    
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
    ratings_df = pd.read_csv('/Users/welcomemac/Downloads/ratings.csv')
    
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
    # ... (existing implementation remains unchanged) ...

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
    # ... (existing implementation remains unchanged) ...

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
            bollywood_movies = movies_df[movies_df['is_bollywood'] == True].sort_values('weighted_score', ascending=False).head(15)
            
            if not bollywood_movies.empty:
                cols = st.columns(5)
                for idx, (_, row) in enumerate(bollywood_movies.iterrows()):
                    if idx < 15:  # Limit to 15 movies
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

        # ... (other tabs remain unchanged) ...

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
