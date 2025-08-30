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

# =========================================
# MODULE 1: CONFIGURATION & INITIALIZATION
# =========================================
import warnings
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import requests
import faiss
import time
import uuid
import re
import logging
import json
from datetime import datetime
from wordcloud import WordCloud
from collections import defaultdict, Counter
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
import groq

# Configure logging
logging.basicConfig(filename='app_errors.log', level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress warnings
warnings.filterwarnings('ignore')

# Initialize session state
def initialize_session_state():
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
    if "high_contrast" not in st.session_state:
        st.session_state.high_contrast = False
    if "co2_savings" not in st.session_state:
        st.session_state.co2_savings = 0.0
    if "user_preferences_set" not in st.session_state:
        st.session_state.user_preferences_set = False
    if "show_debug" not in st.session_state:
        st.session_state.show_debug = False
    if "movie_details_cache" not in st.session_state:
        st.session_state.movie_details_cache = {}
    if "tmdb_ratings_cache" not in st.session_state:
        st.session_state.tmdb_ratings_cache = {}
    if "last_api_call" not in st.session_state:
        st.session_state.last_api_call = 0
    if "ai_assistant_messages" not in st.session_state:
        st.session_state.ai_assistant_messages = []
    if "similarity_movies" not in st.session_state:
        st.session_state.similarity_movies = []
    if "similarity_input" not in st.session_state:
        st.session_state.similarity_input = ""

    # Define default user preferences structure
    DEFAULT_USER_PREFERENCES = {
        'liked_movies': [],
        'disliked_movies': [],
        'preferred_genres': [],
        'watchlist': [],
        'mood_preferences': [],
        'preferred_era': "Any",
        'preferred_actors': [],
        'preferred_directors': []
    }

    if "user_preferences" not in st.session_state:
        st.session_state.user_preferences = DEFAULT_USER_PREFERENCES.copy()

# Configure Streamlit page
def configure_page():
    st.set_page_config(
        page_title="🎬 Movie Recommender Pro", 
        layout="wide", 
        page_icon="🎥", 
        initial_sidebar_state="expanded"
    )

# =========================================
# MODULE 2: UTILITIES & HELPER FUNCTIONS
# =========================================
def format_currency(amount):
    """Format currency amounts for display"""
    try:
        if pd.isna(amount) or amount <= 0:
            return "N/A"
        return f"${amount:,.0f}"
    except Exception as e:
        logging.error(f"Error formatting currency: {str(e)}")
        return "N/A"

def log_event(user, movie, action):
    """Log user events to CSV files"""
    try:
        os.makedirs('user_data', exist_ok=True)
        log_file = f'user_data/{user}_log.csv'
        
        if not os.path.exists(log_file):
            with open(log_file, 'w') as f:
                f.write("Timestamp,Movie,Action\n")
        
        with open(log_file, 'a') as f:
            f.write(f"{datetime.now()},{movie},{action}\n")
    except Exception as e:
        logging.error(f"Error logging event: {str(e)}")
        st.error(f"Error logging event: {str(e)}")

def display_poster(poster_path, class_name="poster-container", width=200, movie_id=None, title=None):
    """Display movie poster with lazy loading and error handling"""
    try:
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            
            # Create a unique key for the button
            button_key = f"poster_btn_{movie_id}_{uuid.uuid4().hex[:6]}" if movie_id else f"poster_{uuid.uuid4().hex[:6]}"
            
            # Make the entire poster clickable
            if movie_id and title:
                # Create a button that covers the entire poster
                st.markdown(
                    f"""
                    <div class="{class_name}" style="width:{width}px; position: relative;">
                        <img src="{poster_url}" class="poster-img" alt="Movie Poster" loading="lazy" 
                             onerror="this.onerror=null; this.src='https://via.placeholder.com/300x450?text=Poster+Not+Available';"
                             style="width: 100%; height: auto; border-radius: 10px; cursor: pointer;"
                             onclick="document.getElementById('{button_key}').click()">
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Add invisible button that will be clicked by the poster
                if st.button("", key=button_key, 
                            help=f"Click for details about {title}",
                            use_container_width=False,
                            on_click=show_movie_details, 
                            args=(movie_id, title),
                            type="secondary"):
                    pass
            else:
                # Just display the poster without click functionality
                st.markdown(
                    f"""
                    <div class="{class_name}" style="width:{width}px">
                        <img src="{poster_url}" class="poster-img" alt="Movie Poster" loading="lazy" 
                             onerror="this.onerror=null; this.src='https://via.placeholder.com/300x450?text=Poster+Not+Available';">
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            return True
    except Exception as e:
        logging.error(f"Error displaying poster: {str(e)}")
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

def show_movie_details(movie_id, title):
    """Set the selected movie in session state"""
    st.session_state.selected_movie = movie_id
    st.session_state.selected_movie_title = title

def render_movie_details(movie_id, title):
    """Render detailed movie information in a modal"""
    try:
        # Fetch movie details with caching
        movie_details = fetch_movie_details_with_cache(movie_id, st.secrets["TMDB_API_KEY"])
        
        if not movie_details:
            st.error("Could not fetch movie details. Please try again later.")
            return
        
        # Create modal-like UI
        st.markdown("""
        <style>
        .modal-content {
            background-color: var(--card);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            margin: 15px 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f'<div class="modal-content">', unsafe_allow_html=True)
        
        # Header with close button
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"### {title}")
        with col2:
            if st.button("✕", key=f"close_{movie_id}"):
                st.session_state.selected_movie = None
                st.rerun()
        
        # Movie details
        col1, col2 = st.columns([1, 2])
        
        with col1:
            display_poster(movie_details.get('poster_path'), 
                          class_name="poster-container", 
                          width=250,
                          movie_id=movie_id,
                          title=title)
            
            # Real-time rating
            rating = get_realtime_rating(movie_id, st.secrets["TMDB_API_KEY"])
            if rating:
                st.metric("TMDB Rating", f"{rating:.1f}/10")
        
        with col2:
            # Basic info
            st.write(f"**Release Date:** {movie_details.get('release_date', 'N/A')}")
            st.write(f"**Director:** {movie_details.get('director', 'N/A')}")
            
            # Genres
            genres = movie_details.get('genres', 'N/A')
            if isinstance(genres, str):
                genre_tags = " ".join([f"<span class='tag tag-genre'>{genre.strip()}</span>" for genre in genres.split(',')])
                st.markdown(f"**Genres:** <div style='margin: 10px 0;'>{genre_tags}</div>", unsafe_allow_html=True)
            
            # Cast
            actors = movie_details.get('actors', [])
            if actors and isinstance(actors, list):
                st.write(f"**Cast:** {', '.join(actors[:5])}")
            
            # Budget and revenue if available
            budget = movie_details.get('budget', 0)
            if budget and budget > 0:
                st.write(f"**Budget:** {format_currency(budget)}")
            
            # Overview
            st.write(f"**Overview:** {movie_details.get('overview', 'No overview available.')}")
            
            # User actions
            if st.session_state.logged_in:
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("👍 Like", key=f"like_detail_{movie_id}"):
                        update_preferences('like', movie_id, "detail")
                with col2:
                    if st.button("👎 Dislike", key=f"dislike_detail_{movie_id}"):
                        update_preferences('dislike', movie_id, "detail")
                with col3:
                    watchlist = st.session_state.user_preferences.get('watchlist', [])
                    if title in watchlist:
                        if st.button("❌ Remove Watchlist", key=f"remove_wl_detail_{movie_id}"):
                            update_preferences('remove_from_watchlist', movie_id, "detail")
                    else:
                        if st.button("➕ Add to Watchlist", key=f"add_wl_detail_{movie_id}"):
                            update_preferences('add_to_watchlist', movie_id, "detail")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    except Exception as e:
        logging.error(f"Error rendering movie details: {str(e)}")
        st.error(f"Error showing movie details: {str(e)}")

def find_movie_by_title(title, movies_df):
    """Find movie by title with fuzzy matching"""
    try:
        # Exact match
        if title in movies_df['title'].values:
            return title
        
        # Fuzzy match
        matches = movies_df[movies_df['title'].str.contains(title, case=False)]
        if not matches.empty:
            return matches.iloc[0]['title']
        
        # Try fuzzy matching
        all_titles = movies_df['title'].tolist()
        for t in all_titles:
            if title.lower() in t.lower():
                return t
        return None
    except Exception as e:
        logging.error(f"Error finding movie: {str(e)}")
        st.error(f"Error finding movie: {str(e)}")
        return None

def get_realtime_rating(movie_id, api_key):
    """Get real-time rating from TMDB API with caching and rate limiting"""
    try:
        # Check cache first
        if movie_id in st.session_state.tmdb_ratings_cache:
            cached_data = st.session_state.tmdb_ratings_cache[movie_id]
            # Check if cache is still valid (5 minutes)
            if time.time() - cached_data['timestamp'] < 300:
                return cached_data['rating']
        
        # Rate limiting - max 1 request per second
        current_time = time.time()
        if current_time - st.session_state.last_api_call < 1.0:
            time.sleep(1.0 - (current_time - st.session_state.last_api_call))
        
        # Fetch from API
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Update last API call time
        st.session_state.last_api_call = time.time()
        
        # Extract rating
        rating = data.get('vote_average', 0)
        
        # Cache the result
        st.session_state.tmdb_ratings_cache[movie_id] = {
            'rating': rating,
            'timestamp': time.time()
        }
        
        return rating
        
    except Exception as e:
        logging.error(f"Error fetching real-time rating for movie {movie_id}: {str(e)}")
        # Return cached value if available, even if expired
        if movie_id in st.session_state.tmdb_ratings_cache:
            return st.session_state.tmdb_ratings_cache[movie_id]['rating']
        return 0

def fetch_movie_details_with_cache(movie_id, api_key):
    """Fetch movie details with caching"""
    try:
        # Check cache first
        if movie_id in st.session_state.movie_details_cache:
            cached_data = st.session_state.movie_details_cache[movie_id]
            # Check if cache is still valid (24 hours)
            if time.time() - cached_data['timestamp'] < 86400:
                return cached_data['details']
        
        # Fetch from API
        details = fetch_movie_details(movie_id, api_key)
        
        # Cache the result
        if details:
            st.session_state.movie_details_cache[movie_id] = {
                'details': details,
                'timestamp': time.time()
            }
        
        return details
        
    except Exception as e:
        logging.error(f"Error fetching movie details with cache for movie {movie_id}: {str(e)}")
        # Return cached value if available, even if expired
        if movie_id in st.session_state.movie_details_cache:
            return st.session_state.movie_details_cache[movie_id]['details']
        return None

# =========================================
# MODULE 3: DATA LOADING & CACHING
# =========================================
@st.cache_resource
def load_model():
    """Load and cache the sentence transformer model"""
    try:
        return SentenceTransformer('all-MiniLM-L6-v2')
    except Exception as e:
        logging.error(f"Error loading model: {str(e)}")
        st.error(f"Error loading model: {str(e)}")
        return None

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_realtime_data(api_key):
    """Fetch real-time trending movies and new releases"""
    try:
        # Fetch trending movies
        trending_url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={api_key}"
        trending_response = requests.get(trending_url, timeout=10).json()
        trending_movies = trending_response.get('results', [])[:10]
        
        # Fetch new releases
        now = datetime.now()
        release_date = now.strftime("%Y-%m-%d")
        new_releases_url = f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}&primary_release_date.gte={release_date}&sort_by=release_date.asc"
        new_releases_response = requests.get(new_releases_url, timeout=10).json()
        new_releases = new_releases_response.get('results', [])[:10]
        
        # Fetch popular web series
        web_series_url = f"https://api.themoviedb.org/3/tv/popular?api_key={api_key}"
        web_series_response = requests.get(web_series_url, timeout=10).json()
        web_series = web_series_response.get('results', [])[:10]
        
        return {
            'trending': trending_movies,
            'new_releases': new_releases,
            'web_series': web_series
        }
    except Exception as e:
        logging.error(f"Error fetching real-time data: {str(e)}")
        st.error(f"Error fetching real-time data: {str(e)}")
        return {
            'trending': [],
            'new_releases': [],
            'web_series': []
        }

@st.cache_data(ttl=3600*24)  # Cache for 24 hours
def fetch_movie_details(movie_id, api_key):
    """Fetch detailed movie info including credits"""
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&append_to_response=credits"
        data = requests.get(url, timeout=10).json()
        
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
        
        # Get poster path
        poster_path = data.get('poster_path', None)
        
        # Handle missing overview
        overview = data.get('overview', 'No overview available.')
        if not overview or overview.strip() == "":
            overview = "No overview available."
        
        return {
            'id': movie_id,
            'title': data.get('title', 'Unknown Title'),
            'release_date': data.get('release_date', ''),
            'overview': overview,
            'vote_average': data.get('vote_average', 0),
            'vote_count': data.get('vote_count', 0),
            'popularity': data.get('popularity', 0),
            'budget': data.get('budget', 0),
            'genres': ', '.join(genres) if genres else "Unknown",
            'director': director,
            'actors': actors,
            'poster_path': poster_path,
            'original_language': data.get('original_language', 'en')
        }
    except Exception as e:
        logging.error(f"Error fetching details for movie {movie_id}: {str(e)}")
        st.error(f"Error fetching details for movie {movie_id}: {str(e)}")
        return None

@st.cache_data(ttl=3600*24)  # Cache for 24 hours
def fetch_popular_movies_by_year(years, api_key, movies_per_year=50):
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
            response = requests.get(url, params=params, timeout=10).json()
            movies = response.get('results', [])[:movies_per_year]
            all_movies.extend([{
                'id': m['id'],
                'title': m.get('title', 'Unknown Title'),
                'release_date': m.get('release_date', f'{year}-01-01'),
                'poster_path': m.get('poster_path', None),
                'is_bollywood': False
            } for m in movies])
            
            # Fetch Bollywood movies
            bollywood_params = {
                'api_key': api_key,
                'primary_release_year': year,
                'sort_by': 'popularity.desc',
                'page': 1,
                'with_original_language': 'hi'  # Hindi language
            }
            bollywood_response = requests.get(url, params=bollywood_params, timeout=10).json()
            bollywood_movies = bollywood_response.get('results', [])[:min(30, movies_per_year//2)]
            all_movies.extend([{
                'id': m['id'],
                'title': m.get('title', 'Unknown Title'),
                'release_date': m.get('release_date', f'{year}-01-01'),
                'poster_path': m.get('poster_path', None),
                'is_bollywood': True
            } for m in bollywood_movies])
            
        except Exception as e:
            logging.error(f"Error fetching movies for {year}: {str(e)}")
            st.error(f"Error fetching movies for {year}: {str(e)}")
    
    return all_movies

@st.cache_data(ttl=3600*24)  # Cache for 24 hours
def fetch_movies_by_actor(actor_name, api_key):
    """Fetch movies featuring a specific actor"""
    try:
        # Search for person
        search_url = f"https://api.themoviedb.org/3/search/person?api_key={api_key}&query={actor_name}"
        search_data = requests.get(search_url, timeout=10).json()
        
        if not search_data.get('results'):
            return []
        
        person_id = search_data['results'][0]['id']
        
        # Get person credits
        credits_url = f"https://api.themoviedb.org/3/person/{person_id}/movie_credits?api_key={api_key}"
        credits_data = requests.get(credits_url, timeout=10).json()
        
        # Get movies where person is actor
        movies = []
        for movie in credits_data.get('cast', []):
            movies.append({
                'id': movie['id'],
                'title': movie.get('title', 'Unknown'),
                'release_date': movie.get('release_date', ''),
                'poster_path': movie.get('poster_path', None),
                'is_bollywood': True if actor_name in [
                    "Shah Rukh Khan", "Salman Khan", "Aamir Khan", "Akshay Kumar", "Hrithik Roshan",
                    "Ranbir Kapoor", "Ranveer Singh", "Vicky Kaushal", "Shahid Kapoor", "Ayushmann Khurrana",
                    "Tiger Shroff", "Varun Dhawan", "Sidharth Malhotra", "Kartik Aaryan", "Rajkummar Rao",
                    "Pankaj Tripathi", "Nawazuddin Siddiqui", "Manoj Bajpayee", "Vikrant Massey", "Sunny Deol",
                    "Bobby Deol", "Arjun Kapoor", "Aditya Roy Kapur", "Emraan Hashmi", "Abhishek Bachchan",
                    "Farhan Akhtar", "John Abraham", "Sanjay Dutt", "Ajay Devgn", "Saif Ali Khan", "Prabhas",
                    "Deepika Padukone", "Alia Bhatt", "Katrina Kaif", "Kareena Kapoor Khan", "Priyanka Chopra Jonas",
                    "Kiara Advani", "Anushka Sharma", "Taapsee Pannu", "Janhvi Kapoor", "Sara Ali Khan",
                    "Kriti Sanon", "Bhumi Pednekar", "Shraddha Kapoor", "Parineeti Chopra", "Yami Gautam",
                    "Radhika Apte", "Mrunal Thakur", "Disha Patani", "Nushrratt Bharuccha", "Pooja Hegde",
                    "Sanya Malhotra", "Huma Qureshi", "Rani Mukerji", "Vidya Balan", "Sonam Kapoor",
                    "Nora Fatehi", "Tabu", "Kajol", "Aishwarya Rai Bachchan", "Triptii Dimri"
                ] else False
            })
        
        return movies
        
    except Exception as e:
        logging.error(f"Error fetching movies for {actor_name}: {str(e)}")
        st.error(f"Error fetching movies for {actor_name}: {str(e)}")
        return []

@st.cache_data(ttl=3600*24)  # Cache for 24 hours
def fetch_popular_web_series(api_key, num_series=30):
    """Fetch popular TV shows (web series)"""
    try:
        url = f"https://api.themoviedb.org/3/tv/popular?api_key={api_key}"
        response = requests.get(url, timeout=10).json()
        series_list = response.get('results', [])[:num_series]
        
        detailed_series = []
        for series in series_list:
            # Get TV show details
            tv_url = f"https://api.themoviedb.org/3/tv/{series['id']}?api_key={api_key}"
            tv_data = requests.get(tv_url, timeout=10).json()
            
            # Handle missing overview
            overview = tv_data.get('overview', 'No overview available.')
            if not overview or overview.strip() == "":
                overview = "No overview available."
            
            # Extract genres
            genres = []
            if 'genres' in tv_data:
                genres = [g['name'] for g in tv_data.get('genres', [])]
            
            detailed_series.append({
                'id': tv_data['id'],
                'title': tv_data.get('name', 'Unknown'),
                'release_date': tv_data.get('first_air_date', ''),
                'overview': overview,
                'vote_average': tv_data.get('vote_average', 0),
                'vote_count': tv_data.get('vote_count', 0),
                'popularity': tv_data.get('popularity', 0),
                'genres': ', '.join(genres),
                'poster_path': tv_data.get('poster_path', None),
                'type': 'Web Series',
                'seasons': tv_data.get('number_of_seasons', 1),
                'episodes': tv_data.get('number_of_episodes', 1),
                'original_language': tv_data.get('original_language', 'en')
            })
        
        return detailed_series
        
    except Exception as e:
        logging.error(f"Error fetching web series: {str(e)}")
        st.error(f"Error fetching web series: {str(e)}")
        return []

@st.cache_data
def load_data(api_key):
    """Load and cache movie data with progress tracking"""
    try:
        # Show loading progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("Loading movie data... 0%")
        
        # Fetch popular movies by year (2000-2025) - increased count
        years = list(range(2000, 2025))
        movies_list = fetch_popular_movies_by_year(years, api_key, movies_per_year=70)
        total_movies = len(movies_list)
        
        # Add movies for all requested actors/actresses
        actors_list = [
            "Shah Rukh Khan", "Salman Khan", "Aamir Khan", "Akshay Kumar", "Hrithik Roshan",
            "Ranbir Kapoor", "Ranveer Singh", "Vicky Kaushal", "Shahid Kapoor", "Ayushmann Khurrana",
            "Tiger Shroff", "Varun Dhawan", "Sidharth Malhotra", "Kartik Aaryan", "Rajkummar Rao",
            "Pankaj Tripathi", "Nawazuddin Siddiqui", "Manoj Bajpayee", "Vikrant Massey", "Sunny Deol",
            "Bobby Deol", "Arjun Kapoor", "Aditya Roy Kapur", "Emraan Hashmi", "Abhishek Bachchan",
            "Farhan Akhtar", "John Abraham", "Sanjay Dutt", "Ajay Devgn", "Saif Ali Khan", "Prabhas",
            "Deepika Padukone", "Alia Bhatt", "Katrina Kaif", "Kareena Kapoor Khan", "Priyanka Chopra Jonas",
            "Kiara Advani", "Anushka Sharma", "Taapsee Pannu", "Janhvi Kapoor", "Sara Ali Khan",
            "Kriti Sanon", "Bhumi Pednekar", "Shraddha Kapoor", "Parineeti Chopra", "Yami Gautam",
            "Radhika Apte", "Mrunal Thakur", "Disha Patani", "Nushrratt Bharuccha", "Pooja Hegde",
            "Sanya Malhotra", "Huma Qureshi", "Rani Mukerji", "Vidya Balan", "Sonam Kapoor",
            "Nora Fatehi", "Tabu", "Kajol", "Aishwarya Rai Bachchan", "Triptii Dimri"
        ]
        
        # Add actor movies
        for i, actor in enumerate(actors_list):
            actor_movies = fetch_movies_by_actor(actor, api_key)
            movies_list.extend(actor_movies)
            
            # Update progress
            progress = (i + 1) / len(actors_list) * 0.3
            progress_bar.progress(progress)
            status_text.text(f"Loading actor movies... {int(progress*100)}%")
        
        # Add web series
        web_series = fetch_popular_web_series(api_key, num_series=30)
        movies_list.extend([{
            'id': s['id'],
            'title': s['title'],
            'release_date': s['release_date'],
            'poster_path': s['poster_path'],
            'is_bollywood': False,
            'is_web_series': True,
            'details': s
        } for s in web_series])
        
        # Fetch details for each movie with progress
        detailed_movies = []
        for i, movie in enumerate(movies_list):
            # For web series, we already have details
            if movie.get('is_web_series', False):
                detailed_movies.append(movie['details'])
            else:
                details = fetch_movie_details(movie['id'], api_key)
                if details:
                    # Add Bollywood flag to details
                    details['is_bollywood'] = movie.get('is_bollywood', False)
                    details['is_web_series'] = False
                    detailed_movies.append(details)
            
            # Update progress every 5 movies
            if i % 5 == 0:
                progress = (i + 1) / len(movies_list) * 0.7 + 0.3
                progress_bar.progress(progress)
                status_text.text(f"Loading movie data... {int(progress*100)}%")
        
        # Create DataFrame
        movies_df = pd.DataFrame(detailed_movies)
        
        # Remove duplicates
        movies_df = movies_df.drop_duplicates(subset=['id'])
        
        # Load ratings data - with column validation
        ratings_df = pd.DataFrame(columns=['userId', 'movieId', 'rating'])
        if os.path.exists('ratings.csv'):
            ratings_df = pd.read_csv('ratings.csv')
            # Rename columns to match expected format
            column_map = {}
            if 'user_id' in ratings_df.columns:
                column_map['user_id'] = 'userId'
            if 'movie_id' in ratings_df.columns:
                column_map['movie_id'] = 'movieId'
            if 'ratings' in ratings_df.columns:
                column_map['ratings'] = 'rating'
            ratings_df = ratings_df.rename(columns=column_map)
            
            # Ensure required columns exist
            if not all(col in ratings_df.columns for col in ['userId', 'movieId', 'rating']):
                st.error("Ratings file has incorrect columns. Using empty DataFrame.")
                ratings_df = pd.DataFrame(columns=['userId', 'movieId', 'rating'])
        
        # Precompute TF-IDF and similarity - with overview validation
        tfidf = TfidfVectorizer(stop_words='english')
        overviews = movies_df['overview'].fillna('').astype(str)
        tfidf_matrix = tfidf.fit_transform(overviews)
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        indices = pd.Series(movies_df.index, index=movies_df['title']).drop_duplicates()
        
        # Generate embeddings
        model = load_model()
        if model:
            genres = movies_df['genres'].fillna('').astype(str)
            embeddings = model.encode(genres.tolist(), show_progress_bar=False)
            dim = embeddings.shape[1]
            index = faiss.IndexFlatL2(dim)
            index.add(np.array(embeddings))
        else:
            # Fallback: create empty index
            dim = 384  # Default dimension for all-MiniLM-L6-v2
            embeddings = np.zeros((len(movies_df), dim))
            index = faiss.IndexFlatL2(dim)
            index.add(embeddings)
        
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
        genre_set.add("Web Series")
        
        # Remove unwanted genres
        unwanted_genres = {
            'Action & Adventure', 'Bollywood', 'Drama', 'kids', 'Music', 'News', 'Reality', 
            'Western', 'Sci-Fi & Fantasy', 'TV Movie', 'Soap', 'Web Series', 'War', 'Talk'
        }
        genre_set = genre_set - unwanted_genres
        
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
            'genre_set': sorted(genre_set) if genre_set else []
        }
    except Exception as e:
        logging.error(f"Error loading data: {str(e)}")
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), {
            'tfidf_matrix': None,
            'cosine_sim': None,
            'indices': None,
            'embeddings': None,
            'faiss_index': None,
            'genre_set': []
        }

# =========================================
# MODULE 4: USER MANAGEMENT
# =========================================
USER_PROFILES_DIR = "user_profiles"
USERS_FILE = "users.csv"
LOGIN_ACTIVITY_FILE = "login_activity.csv"

def save_user_profile(username):
    """Save user profile to disk"""
    try:
        os.makedirs(USER_PROFILES_DIR, exist_ok=True)
        profile_path = os.path.join(USER_PROFILES_DIR, f"{username}_profile.pkl")
        profile_data = {
            'user_vector': st.session_state.user_vector,
            'user_preferences': st.session_state.user_preferences,
            'user_preferences_set': st.session_state.user_preferences_set,
            'co2_savings': st.session_state.co2_savings
        }
        with open(profile_path, 'wb') as f:
            pickle.dump(profile_data, f)
        return True
    except Exception as e:
        logging.error(f"Error saving user profile: {str(e)}")
        st.error(f"Error saving user profile: {str(e)}")
        return False

def load_user_profile(username):
    """Load user profile from disk"""
    try:
        profile_path = os.path.join(USER_PROFILES_DIR, f"{username}_profile.pkl")
        if os.path.exists(profile_path):
            with open(profile_path, 'rb') as f:
                profile_data = pickle.load(f)
            
            # Ensure all preference keys exist
            DEFAULT_USER_PREFERENCES = {
                'liked_movies': [],
                'disliked_movies': [],
                'preferred_genres': [],
                'watchlist': [],
                'mood_preferences': [],
                'preferred_era': "Any",
                'preferred_actors': [],
                'preferred_directors': []
            }
            
            loaded_prefs = profile_data.get('user_preferences', {})
            for key in DEFAULT_USER_PREFERENCES:
                if key not in loaded_prefs:
                    loaded_prefs[key] = DEFAULT_USER_PREFERENCES[key]
                    
            st.session_state.user_vector = profile_data.get('user_vector', None)
            st.session_state.user_preferences = loaded_prefs
            st.session_state.user_preferences_set = profile_data.get('user_preferences_set', False)
            st.session_state.co2_savings = profile_data.get('co2_savings', 0.0)
            return True
    except Exception as e:
        logging.error(f"Error loading user profile: {str(e)}")
        st.error(f"Error loading user profile: {str(e)}")
    return False

def save_login_activity(username):
    """Save login activity to log file"""
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if os.path.exists(LOGIN_ACTIVITY_FILE):
            logs = pd.read_csv(LOGIN_ACTIVITY_FILE)
        else:
            logs = pd.DataFrame(columns=["Username", "Timestamp"])

        new_entry = pd.DataFrame({"Username": [username], "Timestamp": [now]})
        logs = pd.concat([logs, new_entry], ignore_index=True)
        logs.to_csv(LOGIN_ACTIVITY_FILE, index=False)
    except Exception as e:
        logging.error(f"Error saving login activity: {str(e)}")
        st.error(f"Error saving login activity: {str(e)}")

def validate_user(username, password):
    """Validate user credentials"""
    try:
        if not os.path.exists(USERS_FILE):
            return False
        df = pd.read_csv(USERS_FILE)
        return ((df['username'] == username) & (df['password'] == password)).any()
    except Exception as e:
        logging.error(f"Error validating user: {str(e)}")
        st.error(f"Error validating user: {str(e)}")
        return False

def register_user(username, password):
    """Register a new user"""
    try:
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
    except Exception as e:
        logging.error(f"Error registering user: {str(e)}")
        st.error(f"Error registering user: {str(e)}")
        return False

def initialize_user_profile(username):
    """Initialize a new user profile"""
    try:
        if not load_user_profile(username):
            # Create new profile
            st.session_state.user_vector = np.zeros(384)
            st.session_state.user_preferences = {
                'liked_movies': [],
                'disliked_movies': [],
                'preferred_genres': [],
                'watchlist': [],
                'mood_preferences': [],
                'preferred_era': "Any",
                'preferred_actors': [],
                'preferred_directors': []
            }
            st.session_state.user_preferences_set = False
            st.session_state.co2_savings = 0.0
            save_user_profile(username)
    except Exception as e:
        logging.error(f"Error initializing user profile: {str(e)}")
        st.error(f"Error initializing user profile: {str(e)}")

# =========================================
# MODULE 5: RECOMMENDATION ENGINE
# =========================================
@st.cache_resource
def train_dl_model():
    """Train and cache the deep learning model"""
    try:
        from surprise import Dataset, Reader, SVD
        from surprise.model_selection import train_test_split

        ratings_df = st.session_state.cached_data[1] if st.session_state.cached_data else pd.DataFrame(columns=['userId', 'movieId', 'rating'])
        
        # Check if we have enough data
        if ratings_df.empty or len(ratings_df) < 100:
            st.warning("Insufficient ratings data. Using content-based recommendations only.")
            return None
        
        # Ensure we have the required columns
        required_columns = ['userId', 'movieId', 'rating']
        if not all(col in ratings_df.columns for col in required_columns):
            st.error("Ratings data is missing required columns. Using content-based recommendations only.")
            return None
        
        reader = Reader(rating_scale=(0.5, 5))
        data = Dataset.load_from_df(ratings_df[['userId', 'movieId', 'rating']], reader)
        trainset, _ = train_test_split(data, test_size=0.2, random_state=42)

        model = SVD(n_factors=50, n_epochs=10, lr_all=0.01, reg_all=0.02)
        model.fit(trainset)
        return model
    except Exception as e:
        logging.error(f"Error training DL model: {str(e)}")
        st.error(f"Error training DL model: {str(e)}")
        return None

def get_user_preferred_genres():
    """Get user's preferred genres based on liked movies"""
    try:
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
    except Exception as e:
        logging.error(f"Error getting preferred genres: {str(e)}")
        st.error(f"Error getting preferred genres: {str(e)}")
    return []

def advanced_hybrid_recommendation(title=None, user_id=None, top_n=10, selected_genres=None, 
                                  sort_by="latest", actor_director=None, mood=None):
    """Generate hybrid recommendations combining content and collaborative filtering"""
    try:
        movies_df, _, precomputed = st.session_state.cached_data
        
        # If no title provided, use user preferences or default to popular movies
        if title is None:
            # If user has preferences, find similar to user vector
            if st.session_state.user_vector is not None and not np.all(st.session_state.user_vector == 0):
                # Search for similar movies to user vector
                query_vector = st.session_state.user_vector.reshape(1, -1)
                distances, indices = precomputed['faiss_index'].search(query_vector, top_n*3)
                
                # Get movie details
                results = movies_df.iloc[indices[0]]
                
                # Calculate similarity scores (1 - normalized distance)
                max_distance = distances[0].max()
                results['similarity'] = 1 - (distances[0] / max_distance)
                
                # Apply genre filter
                if selected_genres:
                    results = results[results['genres'].apply(
                        lambda g: any(genre in g.split(', ') for genre in selected_genres) if isinstance(g, str) else False
                    )]
                
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
                    results = results[results['genres'].apply(
                        lambda g: any(genre in g.split(', ') for genre in selected_genres) if isinstance(g, str) else False
                    )]
                
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
        if user_id and dl_model is not None:
            predictions = []
            for i, row in movies_df.iterrows():
                pred = dl_model.predict(user_id, row['id'])
                predictions.append((i, pred.est))
        else:
            predictions = [(i, 0) for i in range(len(movies_df))]
        
        # Combine scores
        combined = []
        max_content = max(score for _, score in sim_scores)
        max_collab = max(score for _, score in predictions) if user_id and dl_model is not None else 1
        
        for (i, content_score), (_, collab_score) in zip(sim_scores, predictions):
            if user_id and dl_model is not None:
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
            results = results[results['genres'].apply(
                lambda g: any(genre in g.split(', ') for genre in selected_genres) if isinstance(g, str) else False
            )]
        
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
                results = results[results['genres'].apply(
                    lambda g: any(genre in g.split(', ') for genre in mood_genres) if isinstance(g, str) else False
                )]
        
        # Sort by release date
        if sort_by == "latest":
            results = results.sort_values("release_date", ascending=False)
        elif sort_by == "oldest":
            results = results.sort_values("release_date", ascending=True)
            
        return results.head(top_n)
    except Exception as e:
        logging.error(f"Error generating recommendations: {str(e)}")
        st.error(f"Error generating recommendations: {str(e)}")
        return pd.DataFrame()

def get_personalized_recommendations(top_n=5):
    """Get personalized recommendations based on user preferences"""
    try:
        movies_df, _, precomputed = st.session_state.cached_data
        
        # If user has liked movies, use them to generate recommendations
        if st.session_state.user_preferences.get('liked_movies', []):
            # Create a synthetic "favorite movie" based on user preferences
            user_vector = st.session_state.user_vector
            query_vector = user_vector.reshape(1, -1)
            distances, indices = precomputed['faiss_index'].search(query_vector, top_n*2)
            results = movies_df.iloc[indices[0]]
            
            # Calculate similarity scores (1 - normalized distance)
            max_distance = distances[0].max()
            results['similarity'] = 1 - (distances[0] / max_distance)
            results = results.sort_values('similarity', ascending=False)
        else:
            # Use preferred genres and other preferences
            preferred_genres = st.session_state.user_preferences.get('preferred_genres', [])
            preferred_era = st.session_state.user_preferences.get('preferred_era', "Any")
            preferred_actors = st.session_state.user_preferences.get('preferred_actors', [])
            preferred_directors = st.session_state.user_preferences.get('preferred_directors', [])
            
            # Start with all movies
            results = movies_df.copy()
            
            # Filter by preferred genres
            if preferred_genres:
                results = results[results['genres'].apply(
                    lambda g: any(genre in g.split(', ') for genre in preferred_genres) if isinstance(g, str) else False
                )]
            
            # Filter by preferred era
            if preferred_era != "Any":
                if preferred_era == "Recent (2010-Now)":
                    results = results[results['release_date'] >= "2010-01-01"]
                elif preferred_era == "Classic (Pre-2000)":
                    results = results[results['release_date'] < "2000-01-01"]
            
            # Filter by preferred actors
            if preferred_actors:
                actor_filter = False
                for actor in preferred_actors:
                    actor_filter = actor_filter | results['actors'].apply(
                        lambda x: actor.lower() in [a.lower() for a in x] if isinstance(x, list) else False
                    )
                results = results[actor_filter]
            
            # Filter by preferred directors
            if preferred_directors:
                director_filter = False
                for director in preferred_directors:
                    director_filter = director_filter | results['director'].str.contains(director, case=False)
                results = results[director_filter]
            
            # Sort by popularity
            results = results.sort_values('popularity', ascending=False)
        
        return results.head(top_n)
    except Exception as e:
        logging.error(f"Error getting personalized recommendations: {str(e)}")
        st.error(f"Error getting personalized recommendations: {str(e)}")
        return pd.DataFrame()

def get_similar_movies(movie_title, top_n=5):
    """Get movies similar to the given title"""
    try:
        movies_df, _, precomputed = st.session_state.cached_data
        
        if movie_title not in precomputed['indices']:
            return pd.DataFrame()
        
        idx = precomputed['indices'][movie_title]
        sim_scores = list(enumerate(precomputed['cosine_sim'][idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:top_n+1]  # Skip the first one (itself)
        movie_indices = [i[0] for i in sim_scores]
        
        results = movies_df.iloc[movie_indices]
        results['similarity'] = [i[1] for i in sim_scores]
        
        return results
    except Exception as e:
        logging.error(f"Error getting similar movies: {str(e)}")
        st.error(f"Error getting similar movies: {str(e)}")
        return pd.DataFrame()

def get_text_suggestions(text):
    """Get text-based movie suggestions"""
    try:
        movies_df, _, _ = st.session_state.cached_data
        
        # Simple text-based matching for suggestions
        text = text.lower()
        
        # Keyword to genre mapping
        keyword_mapping = {
            'super': ['Action', 'Adventure', 'Science Fiction', 'Superhero'],
            'hero': ['Action', 'Adventure', 'Science Fiction', 'Superhero'],
            'love': ['Romance', 'Drama', 'Comedy'],
            'romantic': ['Romance', 'Drama'],
            'funny': ['Comedy'],
            'comedy': ['Comedy'],
            'action': ['Action', 'Adventure'],
            'adventure': ['Adventure', 'Action'],
            'drama': ['Drama'],
            'horror': ['Horror', 'Thriller'],
            'scary': ['Horror', 'Thriller'],
            'thriller': ['Thriller', 'Mystery'],
            'mystery': ['Mystery', 'Thriller'],
            'sci-fi': ['Science Fiction'],
            'fantasy': ['Fantasy'],
            'animated': ['Animation', 'Family'],
            'family': ['Family', 'Animation'],
            'documentary': ['Documentary'],
            'history': ['History', 'War'],
            'war': ['War', 'History'],
            'crime': ['Crime', 'Thriller'],
            'musical': ['Music', 'Musical']
        }
        
        # Find matching keywords
        matching_genres = set()
        for keyword, genres in keyword_mapping.items():
            if keyword in text:
                matching_genres.update(genres)
        
        # If no specific keywords found, return popular movies
        if not matching_genres:
            return movies_df.sort_values('popularity', ascending=False).head(5)
        
        # Filter movies by matching genres
        results = movies_df[movies_df['genres'].apply(
            lambda g: any(genre in g for genre in matching_genres) if isinstance(g, str) else False
        )]
        
        # Sort by popularity and return top results
        return results.sort_values('popularity', ascending=False).head(5)
        
    except Exception as e:
        logging.error(f"Error getting text suggestions: {str(e)}")
        st.error(f"Error getting text suggestions: {str(e)}")
        return pd.DataFrame()

# =========================================
# MODULE 6: USER PREFERENCES MANAGEMENT
# =========================================
def update_preferences(action, movie_id, context="default"):
    """Centralized function to update user preferences"""
    try:
        movies_df, _, _ = st.session_state.cached_data
        movie_title = movies_df[movies_df['id'] == movie_id]['title'].values[0]
        
        # Create copies of lists to ensure state change detection
        prefs = st.session_state.user_preferences.copy()
        liked = list(prefs['liked_movies'])
        disliked = list(prefs['disliked_movies'])
        watchlist = list(prefs['watchlist'])
        
        if action == 'like':
            # Remove from disliked if present
            if movie_title in disliked:
                disliked = [m for m in disliked if m != movie_title]
                
            # Add to liked if not present
            if movie_title not in liked:
                liked = liked + [movie_title]
                st.toast(f"👍 Liked {movie_title}!", icon="👍")
                
            # Update user vector
            movie_idx = movies_df.index[movies_df['id'] == movie_id].tolist()[0]
            movie_embedding = st.session_state.cached_data[2]['embeddings'][movie_idx]
            
            if st.session_state.user_vector is None:
                st.session_state.user_vector = movie_embedding
            else:
                st.session_state.user_vector = st.session_state.user_vector * 0.5 + movie_embedding * 0.5
                
        elif action == 'dislike':
            # Remove from liked if present
            if movie_title in liked:
                liked = [m for m in liked if m != movie_title]
                
            # Add to disliked if not present
            if movie_title not in disliked:
                disliked = disliked + [movie_title]
                st.toast(f"👎 Disliked {movie_title}!", icon="👎")
            
            # Update user vector
            movie_idx = movies_df.index[movies_df['id'] == movie_id].tolist()[0]
            movie_embedding = st.session_state.cached_data[2]['embeddings'][movie_idx]
            
            if st.session_state.user_vector is not None:
                st.session_state.user_vector = st.session_state.user_vector * 0.9 - movie_embedding * 0.1
        
        elif action == 'add_to_watchlist':
            if movie_title not in watchlist:
                watchlist = watchlist + [movie_title]
                st.toast(f"✅ Added {movie_title} to your watchlist!", icon="✅")
                st.session_state.co2_savings += 2.5
        elif action == 'remove_from_watchlist':
            if movie_title in watchlist:
                watchlist = [m for m in watchlist if m != movie_title]
                st.toast(f"✅ Removed {movie_title} from your watchlist!", icon="✅")
        
        # Update preferences with new lists
        prefs['liked_movies'] = liked
        prefs['disliked_movies'] = disliked
        prefs['watchlist'] = watchlist
        st.session_state.user_preferences = prefs
        
        # Save updated profile
        save_user_profile(st.session_state.username)
        log_event(st.session_state.username, movie_title, action)
        
        # Force UI refresh to show updated recommendations
        st.rerun()
    except Exception as e:
        logging.error(f"Error updating preferences: {str(e)}")
        st.error(f"Error updating preferences: {str(e)}")

def save_user_taste_preferences():
    """Save user's taste preferences from the form"""
    try:
        st.session_state.user_preferences_set = True
        save_user_profile(st.session_state.username)
        st.toast("Preferences saved successfully! 🎉", icon="✅")
        st.session_state.preferences_expanded = False
        st.rerun()
    except Exception as e:
        logging.error(f"Error saving preferences: {str(e)}")
        st.error(f"Error saving preferences: {str(e)}")

# =========================================
# MODULE 7: UI COMPONENTS
# =========================================
def movie_card(movie, show_feedback=True, context="default", index=0):
    """Display movie information in a styled card"""
    try:
        with st.container():
            # Add type tags
            tags_html = ""
            if movie.get('is_bollywood', False):
                tags_html += "<span class='tag tag-bollywood'>Bollywood</span>"
            if movie.get('is_web_series', False):
                tags_html += "<span class='tag tag-webseries'>Web Series</span>"
                if 'seasons' in movie:
                    tags_html += f"<span class='tag tag-seasons'>{movie['seasons']} Seasons</span>"
            
            st.markdown(f"<div class='movie-card section-animation'>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 3])
            with col1:
                # Use poster_path directly from movie data with clickable functionality
                display_poster(movie.get('poster_path'), 
                              class_name="poster-container",
                              movie_id=movie['id'],
                              title=movie['title'])
            
            with col2:
                st.subheader(movie['title'])
                st.markdown(tags_html, unsafe_allow_html=True)
                
                # Use director from movie data
                director = movie.get('director', 'Unknown')
                st.markdown(f"🎬 **Director:** {director}")
                
                # Safely handle actors field
                actors = movie.get('actors', [])
                if isinstance(actors, list) and len(actors) > 0:
                    st.markdown(f"👥 **Cast:** {', '.join(actors)}")
                
                # Display real-time rating
                rating = get_realtime_rating(movie['id'], st.secrets["TMDB_API_KEY"])
                st.caption(f"⭐ {rating:.1f} | 🗳️ {movie['vote_count']} votes | 📅 {movie['release_date']}")
                
                # Display genres as tags
                genres = movie['genres'].split(', ') if isinstance(movie['genres'], str) else []
                genre_tags = " ".join([f"<span class='tag tag-genre'>{genre}</span>" for genre in genres])
                st.markdown(f"<div style='margin: 10px 0;'>{genre_tags}</div>", unsafe_allow_html=True)
                
                # For web series, show seasons/episodes
                if movie.get('is_web_series', False):
                    st.markdown(f"📺 **Seasons:** {movie.get('seasons', 'N/A')} | **Episodes:** {movie.get('episodes', 'N/A')}")
                
                # Display similarity bar if available
                if 'similarity' in movie:
                    similarity = movie['similarity']
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
                    unique_key = f"{context}_{movie['id']}_{index}_{uuid.uuid4().hex[:6]}"
                    
                    with c1:
                        if st.button("👍 Like", key=f"like_{unique_key}", use_container_width=True):
                            update_preferences('like', movie['id'], context)
                    with c2:
                        if st.button("👎 Dislike", key=f"dislike_{unique_key}", use_container_width=True):
                            update_preferences('dislike', movie['id'], context)
                    with c3:
                        # Safely access watchlist with default
                        watchlist = st.session_state.user_preferences.get('watchlist', [])
                        if movie['title'] in watchlist:
                            if st.button("❌ Remove Watchlist", key=f"remove_wl_{unique_key}", use_container_width=True):
                                update_preferences('remove_from_watchlist', movie['id'], context)
                        else:
                            if st.button("➕ Add to Watchlist", key=f"add_wl_{unique_key}", use_container_width=True):
                                update_preferences('add_to_watchlist', movie['id'], context)

            st.markdown("</div>", unsafe_allow_html=True)
    except Exception as e:
        logging.error(f"Error rendering movie card: {str(e)}")
        st.error(f"Error rendering movie card: {str(e)}")

def render_login_signup():
    """Render the login/signup interface"""
    st.markdown('<h1 class="neon-title" style="text-align: center;">🎬 Movie Recommender Pro</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### 🔐 Login to Your Account")
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login", key="login_btn", use_container_width=True):
            try:
                if login_username == "Vic" and login_password == "Vik":
                    st.success("✅ Admin Logged In")
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    save_login_activity(login_username)
                    initialize_user_profile(login_username)
                    st.rerun()
                elif validate_user(login_username, login_password):
                    st.success(f"✅ Welcome {login_username}")
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    save_login_activity(login_username)
                    initialize_user_profile(login_username)
                    st.rerun()
                else:
                    st.error("❌ Invalid Credentials")
            except Exception as e:
                logging.error(f"Login error: {str(e)}")
                st.error("Error during login. Please try again.")
    
    with col2:
        st.markdown("### 🎉 Create New Account")
        reg_username = st.text_input("Username", key="reg_user")
        reg_password = st.text_input("Password", type="password", key="reg_pass")
        reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
        
        if st.button("Register", key="reg_btn", use_container_width=True):
            try:
                if reg_password != reg_confirm:
                    st.error("Passwords do not match")
                elif register_user(reg_username, reg_password):
                    st.success("🎉 Signup successful. You are now logged in.")
                    st.session_state.logged_in = True
                    st.session_state.username = reg_username
                    save_login_activity(reg_username)
                    initialize_user_profile(reg_username)
                    st.rerun()
                else:
                    st.warning("⚠️ Username already exists. Try logging in.")
            except Exception as e:
                logging.error(f"Registration error: {str(e)}")
                st.error("Error during registration. Please try again.")

def render_taste_preferences_form():
    """Render the taste preferences form"""
    with st.expander("🎬 Tell Us Your Movie Preferences", expanded=True):
        st.write("Help us recommend movies you'll love by telling us about your tastes:")
        
        # Get available data
        movies_df, _, precomputed = st.session_state.cached_data
        
        # Favorite genres
        st.subheader("Favorite Genres")
        available_genres = precomputed.get('genre_set', [])
        selected_genres = st.multiselect(
            "Select your favorite genres (select up to 5)", 
            available_genres,
            default=st.session_state.user_preferences.get('preferred_genres', []),
            max_selections=5
        )
        
        # Preferred era
        st.subheader("Preferred Movie Era")
        era_options = ["Any", "Recent (2010-Now)", "Classic (Pre-2000)"]
        selected_era = st.selectbox(
            "Which era of movies do you prefer?",
            era_options,
            index=era_options.index(st.session_state.user_preferences.get('preferred_era', "Any")))
        
        # Favorite actors
        st.subheader("Favorite Actors/Actresses")
        all_actors = set()
        for actors_list in movies_df['actors']:
            if isinstance(actors_list, list):
                for actor in actors_list:
                    all_actors.add(actor)
        selected_actors = st.multiselect(
            "Select your favorite actors/actresses (select up to 5)",
            sorted(all_actors),
            default=st.session_state.user_preferences.get('preferred_actors', []),
            max_selections=5
        )
        
        # Favorite directors
        st.subheader("Favorite Directors")
        all_directors = set(movies_df['director'].dropna().unique())
        selected_directors = st.multiselect(
            "Select your favorite directors (select up to 3)",
            sorted(all_directors),
            default=st.session_state.user_preferences.get('preferred_directors', []),
            max_selections=3
        )
        
        # Save button
        if st.button("Save Preferences", key="save_prefs_btn", use_container_width=True):
            try:
                st.session_state.user_preferences['preferred_genres'] = selected_genres
                st.session_state.user_preferences['preferred_era'] = selected_era
                st.session_state.user_preferences['preferred_actors'] = selected_actors
                st.session_state.user_preferences['preferred_directors'] = selected_directors
                save_user_taste_preferences()
            except Exception as e:
                logging.error(f"Error saving taste preferences: {str(e)}")
                st.error("Error saving preferences. Please try again.")

# =========================================
# MODULE 8: MAIN APPLICATION LOGIC
# =========================================
def render_home_tab():
    """Render the Home tab"""
    # Show movie details if a movie is selected
    if st.session_state.selected_movie:
        render_movie_details(st.session_state.selected_movie, st.session_state.selected_movie_title)
        if st.button("Back to Home"):
            st.session_state.selected_movie = None
            st.rerun()
        return
    
    # Show current date
    st.subheader(f"📅 {datetime.now().strftime('%A, %B %d, %Y')}")
    
    # Show taste preferences form if not set
    if not st.session_state.user_preferences_set:
        render_taste_preferences_form()
    
    # Movie similarity section
    st.markdown("### 🎬 Find Similar Movies")
    
    # Text input for movie search
    search_input = st.text_input(
        "Enter a movie name to find similar movies", 
        value=st.session_state.similarity_input,
        key="similarity_search",
        placeholder="Type a movie name..."
    )
    
    # Update session state with current input
    st.session_state.similarity_input = search_input
    
    # Show text-based suggestions as user types
    if search_input:
        suggestions = get_text_suggestions(search_input)
        if not suggestions.empty:
            st.markdown("#### 💡 Suggestions based on your input:")
            cols = st.columns(5)
            for idx, (_, row) in enumerate(suggestions.iterrows()):
                with cols[idx % 5]:
                    display_poster(row.get('poster_path'), class_name="poster-container", width=120,
                                  movie_id=row['id'], title=row['title'])
                    st.caption(f"**{row['title']}**")
    
    # Button to find similar movies
    if st.button("Find Similar Movies", key="find_similar_btn", use_container_width=True):
        if search_input:
            movie_title = find_movie_by_title(search_input, movies_df)
            if movie_title:
                similar_movies = get_similar_movies(movie_title, top_n=5)
                if not similar_movies.empty:
                    st.session_state.similarity_movies = similar_movies
                    st.success(f"Found movies similar to **{movie_title}**")
                else:
                    st.warning("No similar movies found. Please try a different movie.")
            else:
                st.warning("Movie not found. Please try a different title.")
        else:
            st.warning("Please enter a movie name first.")
    
    # Display similar movies if available
    if not st.session_state.similarity_movies.empty:
        st.markdown("### 🎯 Similar Movies")
        for _, row in st.session_state.similarity_movies.iterrows():
            movie_card(row, context="similarity")

def render_search_tab():
    """Render the Search & Browse tab"""
    st.subheader("🔍 Search & Browse Movies")
    
    # Search section
    st.markdown("### 🔍 Search Movies")
    search_term = st.text_input("Search by title, genre, or keyword", key="search_term")
    
    if search_term:
        movies_df, _, _ = st.session_state.cached_data
        
        # Search by title
        title_results = movies_df[movies_df['title'].str.contains(search_term, case=False, na=False)]
        
        # Search by genre
        genre_results = movies_df[movies_df['genres'].str.contains(search_term, case=False, na=False)]
        
        # Search by keyword in overview
        keyword_results = movies_df[movies_df['overview'].str.contains(search_term, case=False, na=False)]
        
        # Combine results
        results = pd.concat([title_results, genre_results, keyword_results]).drop_duplicates(subset=["id"])

        if not results.empty:
            st.write(f"🔍 Found {len(results)} matches")
            for _, row in results.head(10).iterrows():
                movie_card(row, show_feedback=True, context="search")
        else:
            st.warning("No movies found matching your search")
    
    # Browse section
    st.markdown("### 📂 Browse Movie Database")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        sort_options = [
            "Title", "Rating", "Popularity", "Release Date (Newest)", 
            "Release Date (Oldest)", "Budget (High to Low)", "Budget (Low to High)"
        ]
        sort_by = st.selectbox("Sort by", sort_options, key="popular_sort")
    with col2:
        num_movies = st.slider("Number per page", 10, 100, 20, key="num_movies_slider")
    
    # Year filter
    st.markdown("### 📅 Filter by Year")
    years = list(range(2000, 2025))
    selected_years = st.multiselect("Select years", years, default=[2023, 2024], key="year_filter")
    
    # Pagination
    page_number = st.number_input("Page", min_value=1, value=1, step=1, key="browse_page")
    start_idx = (page_number - 1) * num_movies
    end_idx = start_idx + num_movies
    
    movies_df, _, _ = st.session_state.cached_data
    
    # Filter by year
    if selected_years:
        year_filter = movies_df['release_date'].apply(
            lambda x: any(str(year) in x for year in selected_years) if isinstance(x, str) else False
        )
        filtered_df = movies_df[year_filter]
    else:
        filtered_df = movies_df.copy()
    
    # Sort the dataframe
    if sort_by == "Rating":
        sorted_df = filtered_df.sort_values("vote_average", ascending=False)
    elif sort_by == "Popularity":
        sorted_df = filtered_df.sort_values("popularity", ascending=False)
    elif sort_by == "Release Date (Newest)":
        sorted_df = filtered_df.sort_values("release_date", ascending=False)
    elif sort_by == "Release Date (Oldest)":
        sorted_df = filtered_df.sort_values("release_date", ascending=True)
    elif sort_by == "Budget (High to Low)":
        sorted_df = filtered_df.sort_values("budget", ascending=False)
    elif sort_by == "Budget (Low to High)":
        sorted_df = filtered_df.sort_values("budget", ascending=True)
    else:
        sorted_df = filtered_df.sort_values("title")
    
    # Display the slice
    st.write(f"📖 Showing {start_idx+1} - {min(end_idx, len(sorted_df))} of {len(sorted_df)} movies")
    for _, row in sorted_df.iloc[start_idx:end_idx].iterrows():
        movie_card(row, context="browse")

def render_recommendations_tab():
    """Render the Recommendations tab"""
    st.subheader("🎯 Personalized Recommendations")
    
    # Hybrid recommendations section
    st.markdown("### 💡 Hybrid Recommendations")
    st.info("Combines content-based filtering with collaborative filtering for personalized results")
    
    # Get available data
    movies_df, _, precomputed = st.session_state.cached_data
    available_genres = precomputed.get('genre_set', [])
    
    # Movie type selection
    selected_types = st.multiselect(
        "Filter by movie types", 
        available_genres, 
        default=["Action", "Drama"], 
        key="hybrid_type_filter"
    )
    
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

    if st.button("Generate Hybrid Recommendations", key="hybrid_btn", use_container_width=True):
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
                
                # Show recommendations
                for _, row in results.iterrows():
                    movie_card(row, context="hybrid")
            else:
                st.warning("⚠️ No recommendations found matching your criteria")
    
    # Personalized recommendations section
    st.markdown("### 🤖 Personalized Recommendations")
    st.info("Recommendations based on your preferences and liked movies")
    
    # Show user preferences context
    if st.session_state.user_preferences.get('liked_movies', []):
        top_genres = get_user_preferred_genres()
        if top_genres:
            st.write(f"🎯 Based on your preferences for: **{', '.join(top_genres)}**")
    
    if st.button("Generate Personalized Recommendations", key="personalized_btn", use_container_width=True):
        try:
            personalized = get_personalized_recommendations(top_n=5)
            
            if not personalized.empty:
                st.subheader("🌟 Personalized For You")
                
                # Show recommendation context
                liked_movies = st.session_state.user_preferences.get('liked_movies', [])
                if liked_movies:
                    st.write(f"✨ Based on your likes: **{', '.join(liked_movies[:3])}**")
                
                # Show recommendations
                for i, row in personalized.iterrows():
                    unique_index = f"{i}_{uuid.uuid4().hex[:6]}"
                    movie_card(row, context="personalized", index=unique_index)
                    if "username" in st.session_state:
                        log_event(st.session_state.username, row['title'], "recommended")
            else:
                st.warning("No personalized recommendations found. Try rating more movies or expanding your preferences.")

        except Exception as e:
            logging.error(f"Personalized recommendation error: {str(e)}")
            st.error(f"❌ Error: {str(e)}")

def render_profile_tab():
    """Render the Profile & Analytics tab"""
    st.subheader(f"👤 {st.session_state.username}'s Profile")
    
    # Accessibility toggle
    st.checkbox("Enable High Contrast Mode", 
                value=st.session_state.high_contrast, 
                key="high_contrast_toggle",
                on_change=lambda: setattr(st.session_state, 'high_contrast', not st.session_state.high_contrast))

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
            
        # Sustainability impact
        st.markdown("#### 🌱 Environmental Impact")
        co2_savings = st.session_state.co2_savings
        st.metric("Estimated CO₂ Savings", f"{co2_savings:.1f} kg", 
                  help="Calculated based on the assumption that watching at home saves 2.5 kg CO₂ per movie compared to theater visits")
        st.caption("By streaming movies at home, you've helped reduce carbon emissions!")

    # Activity log section
    st.markdown("### 📝 Your Activity")
    log_file = f'user_data/{st.session_state.username}_log.csv'
    if os.path.exists(log_file):
        logs = pd.read_csv(log_file)
        st.dataframe(logs.sort_values("Timestamp", ascending=False).head(10))
    else:
        st.info("No activity recorded yet")

    # Analytics section
    st.markdown("### 📊 Movie Analytics Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["Genre Analysis", "Rating Insights", "Word Cloud"])
    
    with tab1:
        st.subheader("🎭 Genre Distribution")
        movies_df, _, _ = st.session_state.cached_data
        genre_count = defaultdict(int)
        for g_list in movies_df['genres']:
            if isinstance(g_list, str):
                for genre in g_list.split(', '):
                    clean_genre = genre.strip()
                    if clean_genre:
                        genre_count[clean_genre] += 1
        
        # Create DataFrame from genre_count
        if genre_count:
            genre_df = pd.DataFrame(list(genre_count.items()), columns=['Genre', 'Count'])
            genre_df = genre_df.sort_values('Count', ascending=False)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x='Count', y='Genre', data=genre_df.head(15), palette="viridis", ax=ax)
            ax.set_title("Top 15 Movie Genres")
            st.pyplot(fig)
        else:
            st.info("No genre data available")

    
    with tab2:
        st.subheader("⭐ Rating Insights")
        fig, ax = plt.subplots(1, 2, figsize=(14, 5))
        
        # Rating histogram
        if 'vote_average' in movies_df.columns:
            sns.histplot(movies_df['vote_average'].dropna(), bins=20, kde=True, ax=ax[0], color='skyblue')
            ax[0].set_title("Vote Average Distribution")
            ax[0].set_xlabel("Rating")
            ax[0].set_ylabel("Frequency")
        
        # Rating vs. Budget
        if 'budget' in movies_df.columns and 'vote_average' in movies_df.columns:
            budget_movies = movies_df[movies_df['budget'] > 0]
            sample_size = min(500, len(budget_movies))
            if sample_size > 0:
                budget_sample = budget_movies.sample(sample_size)
                sns.scatterplot(x='vote_average', y='budget', data=budget_sample, ax=ax[1], alpha=0.6)
                ax[1].set_title("Rating vs. Budget")
                ax[1].set_xlabel("Rating")
                ax[1].set_ylabel("Budget (Millions)")
                ax[1].set_yscale('log')
        
        st.pyplot(fig)
    
    with tab3:
        st.subheader("☁️ Overview Word Cloud")
        if 'overview' in movies_df.columns:
            text = " ".join(movies_df['overview'].dropna().astype(str))
            
            if text:
                wordcloud = WordCloud(width=800, height=400, background_color='black').generate(text)
                fig, ax = plt.subplots(figsize=(12, 8))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
            else:
                st.warning("No overview text available")
        else:
            st.warning("No overview data available")
    
    # Clear preferences button
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear All Preferences", use_container_width=True):
            st.session_state.user_preferences = {
                'liked_movies': [],
                'disliked_movies': [],
                'preferred_genres': [],
                'watchlist': [],
                'mood_preferences': [],
                'preferred_era': "Any",
                'preferred_actors': [],
                'preferred_directors': []
            }
            st.session_state.user_vector = None
            st.session_state.user_preferences_set = False
            save_user_profile(st.session_state.username)
            st.success("Preferences cleared!")
            st.rerun()
    with col2:
        if st.button("🔒 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.success("You have been logged out. Please login again.")
            time.sleep(2)
            st.rerun()

def render_ai_assistant_tab():
    """Render the AI Assistant tab with Groq integration"""
    st.subheader("🤖 AI Movie Assistant")
    st.info("Chat with our AI assistant to get personalized movie recommendations based on your preferences")
    
    # Initialize chat messages if not exists
    if not st.session_state.ai_assistant_messages:
        st.session_state.ai_assistant_messages = [{
            "role": "assistant", 
            "content": "Hi! I'm your AI movie assistant. I can help you find great movies based on your preferences. What kind of movies are you interested in today?"
        }]
    
    # Display chat messages
    for message in st.session_state.ai_assistant_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about movie recommendations..."):
        # Add user message to chat history
        st.session_state.ai_assistant_messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            
            try:
                # Get user preferences for context
                user_prefs = st.session_state.user_preferences
                liked_movies = user_prefs.get('liked_movies', [])
                preferred_genres = user_prefs.get('preferred_genres', [])
                
                # Create context for the AI
                context = f"""
                User preferences:
                - Liked movies: {', '.join(liked_movies[:5]) if liked_movies else 'None yet'}
                - Preferred genres: {', '.join(preferred_genres) if preferred_genres else 'None specified'}
                
                Current query: {prompt}
                
                Please provide helpful, personalized movie recommendations based on the user's preferences and query.
                """
                
                # Initialize Groq client
                client = groq.Client(api_key=st.secrets["GROQ_API_KEY"])
                
                # Generate response
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful movie recommendation assistant. Provide personalized movie suggestions based on the user's preferences and query. Keep responses concise and engaging."
                        },
                        *st.session_state.ai_assistant_messages,
                        {
                            "role": "user",
                            "content": context
                        }
                    ],
                    temperature=0.7,
                    max_tokens=1024,
                    top_p=1,
                    stream=True
                )
                
                # Stream the response
                full_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
                # Add assistant response to chat history
                st.session_state.ai_assistant_messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                logging.error(f"AI assistant error: {str(e)}")
                error_msg = "Sorry, I'm having trouble connecting to the AI service. Please try again later."
                message_placeholder.markdown(error_msg)
                st.session_state.ai_assistant_messages.append({"role": "assistant", "content": error_msg})
    
    # Clear chat button
    if st.button("🗑️ Clear Conversation", key="clear_chat"):
        st.session_state.ai_assistant_messages = [{
            "role": "assistant", 
            "content": "Hi! I'm your AI movie assistant. I can help you find great movies based on your preferences. What kind of movies are you interested in today?"
        }]
        st.rerun()

def main_app():
    """Main application logic after login"""
    st.markdown(f'<h1 class="neon-title">🎬 Movie Recommender Pro</h1>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align: center; margin-bottom: 30px;">Welcome back, <strong>{st.session_state.username}</strong>!</div>', unsafe_allow_html=True)
    
    # Debug panel in sidebar
    with st.sidebar:
        st.markdown("### 🐞 Debug Panel")
        st.session_state.show_debug = st.checkbox("Show User Preferences State", value=st.session_state.show_debug)
        if st.session_state.show_debug:
            st.write("Current Preferences:")
            st.json(st.session_state.user_preferences)
            st.write("User Vector:")
            st.write(st.session_state.user_vector)
    
    # Simplified tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Home",
        "Search & Browse",
        "Recommendations",
        "Profile & Analytics"
    ])
    
    with tab1:
        render_home_tab()
    with tab2:
        render_search_tab()
    with tab3:
        render_recommendations_tab()
    with tab4:
        render_profile_tab()

def main():
    """Main application entry point"""
    # High contrast mode toggle
    if st.session_state.high_contrast:
        st.markdown('<style>:root {--primary: #ff0000; --secondary: #00ffff; --accent: #ffff00; --background: #000000; --card: #111111; --text: #ffffff;}</style>', unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        render_login_signup()
    else:
        try:
            # Load data if not already cached
            if st.session_state.cached_data is None:
                with st.spinner("Loading movie data. This may take a few minutes..."):
                    api_key = st.secrets["TMDB_API_KEY"]
                    movies_df, ratings_df, precomputed = load_data(api_key)
                    st.session_state.cached_data = (movies_df, ratings_df, precomputed)
            
            # Load deep learning model
            global dl_model
            dl_model = train_dl_model()
            
            # Render main application
            main_app()
        except Exception as e:
            logging.error(f"Main app error: {str(e)}")
            st.error(f"Application error: {str(e)}")

# =========================================
# STYLESHEET
# =========================================
def load_styles():
    """Load custom CSS styles"""
    st.markdown("""
    <style>
        :root {
            --primary: #ff6b6b;
            --secondary: #4ecdc4;
            --accent: #ffbe0b;
            --background: #0f0c29;
            --card: rgba(30, 30, 46, 0.8);
            --text: #ffffff;
            --text-secondary: #f0f0f0;
        }
        
        /* Improved contrast for accessibility */
        body, .main { 
            background-color: var(--background);
            color: var(--text);
            font-family: 'Poppins', sans-serif;
            overflow-x: hidden;
            line-height: 1.6;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: var(--accent);
        }
        
        a {
            color: var(--secondary);
            text-decoration: underline;
        }
        
        /* Accessibility: Ensure proper contrast for all text */
        .stTextInput>div>div>input, 
        .stSelectbox>div>div>select,
        .stTextArea>div>div>textarea {
            color: #333 !important;
            background-color: #fff !important;
        }
        
        /* Glassmorphism effect for cards */
        .glass-card {
            background: linear-gradient(135deg, rgba(255, 107, 107, 0.15), rgba(78, 205, 196, 0.15));
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.36);
            padding: 20px;
            margin: 15px 0;
        }
        
        .glass-card:hover {
            transform: translateY(-5px);
            border: 1px solid rgba(255, 190, 11, 0.4);
        }
        
        /* Feature cards */
        .feature-card {
            background: linear-gradient(135deg, rgba(255, 107, 107, 0.2), rgba(78, 205, 196, 0.2));
            border-radius: 16px;
            padding: 25px;
            margin: 15px 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .feature-card:hover {
            transform: scale(1.02);
        }
        
        /* Gradient buttons */
        .stButton>button {
            background: linear-gradient(45deg, var(--primary), var(--accent)) !important;
            color: #1a1a2e !important;
            border: none !important;
            border-radius: 50px !important;
            padding: 10px 25px !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 1px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
            width: 100%;
        }
        
        .stButton>button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3) !important;
            background: linear-gradient(45deg, var(--accent), var(--primary)) !important;
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
            background: linear-gradient(45deg, var(--primary), var(--accent)) !important;
            color: #1a1a2e !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25) !important;
            border: none !important;
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
            transition: all 0.3s ease;
        }
        
        .stTextInput>div>div>input:focus, 
        .stSelectbox>div>div>select:focus,
        .stTextArea>div>div>textarea:focus {
            border: 1px solid var(--accent) !important;
            box-shadow: 0 0 10px rgba(255, 190, 11, 0.3);
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
            box-shadow: 0 12px 40px rgba(255, 107, 107, 0.4);
        }
        
        .tag {
            display: inline-block;
            background: rgba(78, 205, 196, 0.2);
            border-radius: 20px;
            padding: 6px 15px;
            margin-right: 8px;
            margin-bottom: 8px;
            font-size: 0.85rem;
            color: var(--text);
            border: 1px solid rgba(78, 205, 196, 0.3);
        }
        
        .tag-bollywood {
            background: linear-gradient(135deg, #FFD700, #FFA500) !important;
            color: #000 !important;
            border: 1px solid #FF8C00 !important;
        }
        
        .tag-webseries {
            background: linear-gradient(135deg, #00FF7F, #00CED1) !important;
            color: #000 !important;
            border: 1px solid #008B8B !important;
        }
        
        .tag-seasons {
            background: linear-gradient(135deg, #1E90FF, #4169E1) !important;
            color: #fff !important;
            border: 1px solid #0000CD !important;
        }
        
        .tag-genre {
            background: linear-gradient(135deg, #FF69B4, #FF1493) !important;
            color: #fff !important;
            border: 1px solid #C71585 !important;
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
            
            .stButton>button {
                padding: 8px 15px !important;
                font-size: 12px !important;
            }
        }
        
        /* Animation for all sections */
        .section-animation {
            animation: sectionFadeIn 1s ease forwards;
            opacity: 0;
            transform: translateY(20px);
        }
        
        @keyframes sectionFadeIn {
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* High contrast mode for accessibility */
        .high-contrast {
            --primary: #ff0000;
            --secondary: #00ffff;
            --accent: #ffff00;
            --background: #000000;
            --card: #111111;
            --text: #ffffff;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Add animated background
    st.markdown('<div class="animated-bg"></div>', unsafe_allow_html=True)

# =========================================
# APPLICATION ENTRY POINT
# =========================================
if __name__ == "__main__":
    # Apply custom styles
    load_styles()
    
    # Configure page
    configure_page()
    
    # Initialize session state
    initialize_session_state()
    
    # Load deep learning model
    dl_model = None
    
    # Run main application
    main()
