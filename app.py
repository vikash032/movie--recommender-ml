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
    if "movie_details" not in st.session_state:
        st.session_state.movie_details = {}
    if "tmdb_cache" not in st.session_state:
        st.session_state.tmdb_cache = {}
    if "last_api_call" not in st.session_state:
        st.session_state.last_api_call = 0
    if "ai_recommendations" not in st.session_state:
        st.session_state.ai_recommendations = ""

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

def display_poster(poster_path, class_name="poster-container", width=200, movie_id=None):
    """Display movie poster with lazy loading and error handling"""
    try:
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            click_js = f"onclick=\"window.streamlitApi.runMethod('set_movie_detail', '{movie_id}')\"" if movie_id else ""
            st.markdown(
                f"""
                <div class="{class_name}" style="width:{width}px; cursor: pointer;" {click_js}>
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
    click_js = f"onclick=\"window.streamlitApi.runMethod('set_movie_detail', '{movie_id}')\"" if movie_id else ""
    st.markdown(
        f"""
        <div class="{class_name}" style="width:{width}px; cursor: pointer;" {click_js}>
            <div style="background:#333; border-radius:10px; width:100%; height:300px; display:flex; align-items:center; justify-content:center;">
                <span style="color:#aaa; text-align:center;">No Poster<br>Available</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    return False

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

def rate_limited_tmdb_call(api_url):
    """Make TMDB API calls with rate limiting"""
    try:
        # Rate limiting - max 1 call per second
        current_time = time.time()
        time_since_last_call = current_time - st.session_state.last_api_call
        
        if time_since_last_call < 1.0:  # 1 second between calls
            time.sleep(1.0 - time_since_last_call)
        
        # Check cache first
        if api_url in st.session_state.tmdb_cache:
            cached_data = st.session_state.tmdb_cache[api_url]
            # Check if cache is still valid (5 minutes)
            if time.time() - cached_data['timestamp'] < 300:
                return cached_data['data']
        
        # Make API call
        response = requests.get(api_url, timeout=10)
        st.session_state.last_api_call = time.time()
        
        if response.status_code == 200:
            data = response.json()
            # Cache the response
            st.session_state.tmdb_cache[api_url] = {
                'data': data,
                'timestamp': time.time()
            }
            return data
        elif response.status_code == 429:
            st.warning("TMDB API rate limit reached. Please wait a moment.")
            time.sleep(2)
            return rate_limited_tmdb_call(api_url)  # Retry
        else:
            logging.error(f"TMDB API error: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Error in TMDB API call: {str(e)}")
        return None

def get_movie_rating(movie_id):
    """Get real-time movie rating from TMDB"""
    try:
        if not movie_id:
            return "N/A"
            
        api_key = st.secrets["TMDB_API_KEY"]
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
        
        data = rate_limited_tmdb_call(url)
        if data and 'vote_average' in data:
            return data['vote_average']
        return "N/A"
    except Exception as e:
        logging.error(f"Error getting movie rating: {str(e)}")
        return "N/A"

def show_movie_details(movie_id):
    """Show detailed movie information in a modal"""
    try:
        if not movie_id:
            return
            
        # Get movie data
        movies_df, _, _ = st.session_state.cached_data
        movie_data = movies_df[movies_df['id'] == movie_id].iloc[0]
        
        # Get real-time rating
        real_time_rating = get_movie_rating(movie_id)
        
        # Create modal
        with st.expander(f"🎬 {movie_data['title']} - Detailed Information", expanded=True):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                display_poster(movie_data.get('poster_path'), width=250)
                
            with col2:
                st.markdown(f"### {movie_data['title']}")
                
                # Real-time rating
                st.markdown(f"**⭐ Real-time Rating:** {real_time_rating}/10")
                st.markdown(f"**📅 Release Date:** {movie_data.get('release_date', 'N/A')}")
                
                # Genres
                genres = movie_data.get('genres', 'N/A')
                if isinstance(genres, str):
                    genre_tags = " ".join([f"<span class='tag tag-genre'>{genre.strip()}</span>" for genre in genres.split(',')])
                    st.markdown(f"**🎭 Genres:** <div style='margin: 5px 0;'>{genre_tags}</div>", unsafe_allow_html=True)
                
                # Director and cast
                st.markdown(f"**🎬 Director:** {movie_data.get('director', 'N/A')}")
                
                actors = movie_data.get('actors', [])
                if actors and isinstance(actors, list):
                    st.markdown(f"**👥 Cast:** {', '.join(actors[:5])}")
                
                # Budget and popularity
                st.markdown(f"**💰 Budget:** {format_currency(movie_data.get('budget', 0))}")
                st.markdown(f"**📊 Popularity:** {movie_data.get('popularity', 'N/A')}")
                
                # Overview
                overview = movie_data.get('overview', 'No overview available.')
                st.markdown(f"**📖 Overview:** {overview}")
                
    except Exception as e:
        logging.error(f"Error showing movie details: {str(e)}")
        st.error("Could not load movie details.")

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
        trending_data = rate_limited_tmdb_call(trending_url)
        trending_movies = trending_data.get('results', [])[:10] if trending_data else []
        
        # Fetch new releases
        now = datetime.now()
        release_date = now.strftime("%Y-%m-%d")
        new_releases_url = f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}&primary_release_date.gte={release_date}&sort_by=release_date.asc"
        new_releases_data = rate_limited_tmdb_call(new_releases_url)
        new_releases = new_releases_data.get('results', [])[:10] if new_releases_data else []
        
        # Fetch popular web series
        web_series_url = f"https://api.themoviedb.org/3/tv/popular?api_key={api_key}"
        web_series_data = rate_limited_tmdb_call(web_series_url)
        web_series = web_series_data.get('results', [])[:10] if web_series_data else []
        
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
        data = rate_limited_tmdb_call(url)
        
        if not data:
            return None
            
        # Extract director
        director = "Unknown"
        if 'credits' in data and 'crew' in data['credits']:
            for person in data['credits']['crew']:
                if person.get('job') == 'Director':
                    director = person.get('name', 'Unknown')
                    break
        
        # Extract top 3 actors
        actors = []
        if 'credits' in data and 'cast' in data['credits']:
            cast = data['credits']['cast']
            actors = [person.get('name', 'Unknown') for person in cast[:3] if person.get('name')]
        
        # Extract genres
        genres = []
        if 'genres' in data:
            genres = [g.get('name', '') for g in data['genres'] if g.get('name')]
        
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
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                movies = data.get('results', [])[:movies_per_year]
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
            bollywood_response = requests.get(url, params=bollywood_params, timeout=10)
            if bollywood_response.status_code == 200:
                bollywood_data = bollywood_response.json()
                bollywood_movies = bollywood_data.get('results', [])[:min(30, movies_per_year//2)]
                all_movies.extend([{
                    'id': m['id'],
                    'title': m.get('title', 'Unknown Title'),
                    'release_date': m.get('release_date', f'{year}-01-01'),
                    'poster_path': m.get('poster_path', None),
                    'is_bollywood': True
                } for m in bollywood_movies])
            
        except Exception as e:
            logging.error(f"Error fetching movies for {year}: {str(e)}")
            continue
    
    return all_movies

@st.cache_data(ttl=3600*24)  # Cache for 24 hours
def fetch_movies_by_actor(actor_name, api_key):
    """Fetch movies featuring a specific actor"""
    try:
        # Search for person
        search_url = f"https://api.themoviedb.org/3/search/person?api_key={api_key}&query={actor_name}"
        search_data = rate_limited_tmdb_call(search_url)
        
        if not search_data or not search_data.get('results'):
            return []
        
        person_id = search_data['results'][0]['id']
        
        # Get person credits
        credits_url = f"https://api.themoviedb.org/3/person/{person_id}/movie_credits?api_key={api_key}"
        credits_data = rate_limited_tmdb_call(credits_url)
        
        if not credits_data:
            return []
            
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
        return []

@st.cache_data(ttl=3600*24)  # Cache for 24 hours
def fetch_popular_web_series(api_key, num_series=30):
    """Fetch popular TV shows (web series)"""
    try:
        url = f"https://api.themoviedb.org/3/tv/popular?api_key={api_key}"
        response_data = rate_limited_tmdb_call(url)
        
        if not response_data:
            return []
            
        series_list = response_data.get('results', [])[:num_series]
        
        detailed_series = []
        for series in series_list:
            # Get TV show details
            tv_url = f"https://api.themoviedb.org/3/tv/{series['id']}?api_key={api_key}"
            tv_data = rate_limited_tmdb_call(tv_url)
            
            if not tv_data:
                continue
                
            # Handle missing overview
            overview = tv_data.get('overview', 'No overview available.')
            if not overview or overview.strip() == "":
                overview = "No overview available."
            
            # Extract genres
            genres = []
            if 'genres' in tv_data:
                genres = [g.get('name', '') for g in tv_data.get('genres', []) if g.get('name')]
            
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
        movies_list = fetch_popular_movies_by_year(years, api_key, movies_per_year=50)
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
        
        # Data validation
        movies_df = validate_movie_data(movies_df)
        
        # Load ratings data - with column validation
        ratings_df = pd.DataFrame(columns=['userId', 'movieId', 'rating'])
        if os.path.exists('ratings.csv'):
            try:
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
            except Exception as e:
                logging.error(f"Error loading ratings: {str(e)}")
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
            embeddings = np.zeros((len(movies_df), 384))
            index = faiss.IndexFlatL2(384)
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

def validate_movie_data(movies_df):
    """Validate and clean movie data"""
    try:
        # Ensure required columns exist
        required_columns = ['id', 'title', 'release_date', 'overview', 'vote_average', 
                           'vote_count', 'genres', 'director', 'actors', 'poster_path']
        
        for col in required_columns:
            if col not in movies_df.columns:
                movies_df[col] = None
        
        # Fill missing values
        movies_df['title'] = movies_df['title'].fillna('Unknown Title')
        movies_df['overview'] = movies_df['overview'].fillna('No overview available.')
        movies_df['vote_average'] = movies_df['vote_average'].fillna(0)
        movies_df['vote_count'] = movies_df['vote_count'].fillna(0)
        movies_df['genres'] = movies_df['genres'].fillna('Unknown')
        movies_df['director'] = movies_df['director'].fillna('Unknown')
        
        # Ensure actors is a list
        def ensure_actors_list(actors):
            if isinstance(actors, list):
                return actors
            elif isinstance(actors, str) and actors.startswith('['):
                try:
                    return eval(actors)
                except:
                    return []
            return []
        
        movies_df['actors'] = movies_df['actors'].apply(ensure_actors_list)
        
        return movies_df
    except Exception as e:
        logging.error(f"Error validating movie data: {str(e)}")
        return movies_df

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
                # Use poster_path directly from movie data with click functionality
                display_poster(movie.get('poster_path'), class_name="poster-container", movie_id=movie['id'])
            
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
                
                # Real-time rating
                real_time_rating = get_movie_rating(movie['id'])
                st.caption(f"⭐ {real_time_rating} | 🗳️ {movie['vote_count']} votes | 📅 {movie['release_date']}")
                
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
# MODULE 8: AI ASSISTANT WITH GROQ
# =========================================
def get_ai_recommendations():
    """Get AI-powered recommendations using Groq"""
    try:
        # Check if API key is available
        if "GROQ_API_KEY" not in st.secrets:
            return "AI recommendations are currently unavailable. Please configure the Groq API key."
        
        # Get user preferences
        prefs = st.session_state.user_preferences
        
        # Create prompt based on user preferences
        prompt = f"""
        As a movie recommendation expert, suggest 3-5 movies for a user with the following preferences:
        
        - Liked movies: {', '.join(prefs.get('liked_movies', [])) if prefs.get('liked_movies') else 'None yet'}
        - Preferred genres: {', '.join(prefs.get('preferred_genres', [])) if prefs.get('preferred_genres') else 'None specified'}
        - Preferred era: {prefs.get('preferred_era', 'Any')}
        - Favorite actors: {', '.join(prefs.get('preferred_actors', [])) if prefs.get('preferred_actors') else 'None specified'}
        - Favorite directors: {', '.join(prefs.get('preferred_directors', [])) if prefs.get('preferred_directors') else 'None specified'}
        
        Please provide personalized movie recommendations with brief explanations for each suggestion.
        Focus on both Hollywood and Bollywood movies.
        """
        
        # Initialize Groq client
        client = groq.Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        # Get completion
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful movie recommendation expert with knowledge of both Hollywood and Bollywood cinema."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        
        return completion.choices[0].message.content
        
    except Exception as e:
        logging.error(f"Error getting AI recommendations: {str(e)}")
        return f"Sorry, I couldn't generate recommendations at the moment. Error: {str(e)}"

def render_ai_assistant_tab():
    """Render the AI Assistant tab"""
    st.subheader("🤖 AI Movie Assistant")
    st.info("Get personalized movie recommendations powered by AI")
    
    # User preferences summary
    with st.expander("📋 Your Preferences Summary", expanded=True):
        prefs = st.session_state.user_preferences
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Liked Movies:**")
            if prefs.get('liked_movies'):
                for movie in prefs['liked_movies'][:3]:
                    st.write(f"- {movie}")
                if len(prefs['liked_movies']) > 3:
                    st.write(f"- ... and {len(prefs['liked_movies']) - 3} more")
            else:
                st.write("None yet")
                
            st.write("**Preferred Genres:**")
            if prefs.get('preferred_genres'):
                st.write(", ".join(prefs['preferred_genres']))
            else:
                st.write("None specified")
                
        with col2:
            st.write("**Preferred Era:**")
            st.write(prefs.get('preferred_era', 'Any'))
            
            st.write("**Favorite Actors:**")
            if prefs.get('preferred_actors'):
                st.write(", ".join(prefs['preferred_actors']))
            else:
                st.write("None specified")
                
            st.write("**Favorite Directors:**")
            if prefs.get('preferred_directors'):
                st.write(", ".join(prefs['preferred_directors']))
            else:
                st.write("None specified")
    
    # AI recommendations
    if st.button("🎬 Get AI Recommendations", use_container_width=True):
        with st.spinner("🤖 AI is analyzing your preferences..."):
            recommendations = get_ai_recommendations()
            st.session_state.ai_recommendations = recommendations
            
    if st.session_state.ai_recommendations:
        st.markdown("---")
        st.subheader("🎯 AI-Powered Recommendations")
        st.write(st.session_state.ai_recommendations)
        
        # Feedback buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 Helpful", use_container_width=True):
                st.toast("Thanks for your feedback! 👍")
        with col2:
            if st.button("👎 Not Helpful", use_container_width=True):
                st.toast("We'll improve our recommendations. 👎")
    
    # Search suggestions
    st.markdown("---")
    st.subheader("🔍 AI Search Suggestions")
    
    search_query = st.text_input("What type of movies are you looking for?", 
                                placeholder="e.g., action movies with strong female leads")
    
    if search_query:
        with st.spinner("Finding the perfect movies for you..."):
            # Simple search-based recommendations
            movies_df, _, _ = st.session_state.cached_data
            
            # Search in titles and overviews
            title_matches = movies_df[movies_df['title'].str.contains(search_query, case=False)]
            overview_matches = movies_df[movies_df['overview'].str.contains(search_query, case=False)]
            
            # Combine results
            results = pd.concat([title_matches, overview_matches]).drop_duplicates(subset=['id'])
            
            if not results.empty:
                st.success(f"Found {len(results)} movies matching your search")
                for _, row in results.head(3).iterrows():
                    movie_card(row, context="ai_search")
            else:
                st.warning("No movies found matching your search. Try different keywords.")

# =========================================
# MODULE 9: MAIN APPLICATION LOGIC
# =========================================
def render_discover_tab():
    """Render the Discover & Recommendations tab"""
    st.subheader("🔍 Discover Movies")
    
    # Search functionality
    search_col, filter_col = st.columns([3, 1])
    with search_col:
        search_term = st.text_input("Search movies by title, actor, or keyword", key="main_search")
    with filter_col:
        search_type = st.selectbox("Filter by", ["All", "Movies", "Web Series", "Bollywood"], key="search_filter")
    
    if search_term:
        movies_df, _, _ = st.session_state.cached_data
        
        # Apply filters
        results = movies_df.copy()
        if search_type == "Web Series":
            results = results[results['is_web_series'] == True]
        elif search_type == "Bollywood":
            results = results[results['is_bollywood'] == True]
        elif search_type == "Movies":
            results = results[results['is_web_series'] == False]
        # Search in titles, overviews, actors, and directors
        title_matches = results[results['title'].str.contains(search_term, case=False, na=False)]
        overview_matches = results[results['overview'].str.contains(search_term, case=False, na=False)]
        director_matches = results[results['director'].str.contains(search_term, case=False, na=False)]
        
        # Search in actors list
        actor_matches = results[results['actors'].apply(
            lambda x: any(search_term.lower() in actor.lower() for actor in x) if isinstance(x, list) else False
        )]
        
        # Combine results
        results = pd.concat([title_matches, overview_matches, director_matches, actor_matches]).drop_duplicates(subset=['id'])

        if not results.empty:
            st.write(f"🔍 Found {len(results)} matches")
            for _, row in results.head(10).iterrows():
                movie_card(row, show_feedback=True, context="search")
        else:
            st.warning("No movies found matching your search")
    
    # Trending and recommendations sections
    st.markdown("## 🚀 Trending Now")
    
    # Real-time trending data
    realtime_data = fetch_realtime_data(st.secrets["TMDB_API_KEY"])
    
    if realtime_data['trending']:
        cols = st.columns(5)
        for idx, movie in enumerate(realtime_data['trending'][:5]):
            with cols[idx % 5]:
                # Get movie details from our dataset if available
                movies_df, _, _ = st.session_state.cached_data
                movie_details = movies_df[movies_df['id'] == movie['id']]
                
                if not movie_details.empty:
                    display_poster(movie.get('poster_path'), class_name="poster-container", 
                                 width=150, movie_id=movie['id'])
                    st.caption(f"**{movie['title']}**")
                    st.caption(f"⭐ {get_movie_rating(movie['id'])}")
                else:
                    # Fallback to basic display
                    display_poster(movie.get('poster_path'), class_name="poster-container", width=150)
                    st.caption(f"**{movie['title']}**")
                    st.caption(f"⭐ {movie.get('vote_average', 'N/A')}")
    
    # Personalized Recommendations
    st.markdown("## 🎯 Personalized Recommendations")
    if st.session_state.user_preferences_set:
        with st.spinner("Generating personalized recommendations..."):
            personalized = get_personalized_recommendations(top_n=5)
            if not personalized.empty:
                for _, row in personalized.iterrows():
                    movie_card(row, context="personalized")
            else:
                st.info("No personalized recommendations found. Try expanding your preferences.")
    else:
        st.info("Complete your taste preferences to get personalized recommendations")
        if st.button("Set Preferences", key="pref_btn_main"):
            st.session_state.preferences_expanded = True
            st.rerun()
    
    # Genre exploration
    st.markdown("## 🎭 Explore by Genre")
    movies_df, _, precomputed = st.session_state.cached_data
    available_genres = precomputed.get('genre_set', [])
    
    if available_genres:
        selected_genre = st.selectbox("Choose a genre to explore", [""] + available_genres, key="genre_explore")
        
        if selected_genre:
            genre_movies = movies_df[movies_df['genres'].str.contains(selected_genre, case=False, na=False)]
            genre_movies = genre_movies.sort_values('popularity', ascending=False).head(10)
            
            if not genre_movies.empty:
                cols = st.columns(5)
                for idx, (_, row) in enumerate(genre_movies.head(5).iterrows()):
                    with cols[idx % 5]:
                        display_poster(row.get('poster_path'), class_name="poster-container", 
                                     width=150, movie_id=row['id'])
                        st.caption(f"**{row['title']}**")
                        st.caption(f"⭐ {get_movie_rating(row['id'])}")
            else:
                st.warning(f"No movies found in the {selected_genre} genre")

def render_analytics_tab():
    """Render the Profile & Analytics tab"""
    st.subheader("📊 Your Profile & Analytics")
    
    # User profile section
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 👤 Profile Settings")
        
        # Accessibility toggle
        high_contrast = st.toggle("High Contrast Mode", 
                                 value=st.session_state.high_contrast,
                                 help="Enhances visibility for users with visual impairments")
        
        if high_contrast != st.session_state.high_contrast:
            st.session_state.high_contrast = high_contrast
            st.rerun()
        
        # Preference management
        if st.button("Edit Preferences", key="edit_prefs"):
            st.session_state.preferences_expanded = True
            st.rerun()
            
        if st.button("Clear Watchlist", key="clear_watchlist"):
            st.session_state.user_preferences['watchlist'] = []
            save_user_profile(st.session_state.username)
            st.toast("Watchlist cleared!", icon="✅")
            st.rerun()
            
        if st.button("Reset Likes/Dislikes", key="reset_prefs"):
            st.session_state.user_preferences['liked_movies'] = []
            st.session_state.user_preferences['disliked_movies'] = []
            st.session_state.user_vector = np.zeros(384)
            save_user_profile(st.session_state.username)
            st.toast("Preferences reset!", icon="✅")
            st.rerun()
    
    with col2:
        st.markdown("### 📈 Your Activity Analytics")
        
        # Environmental impact
        st.markdown("#### 🌱 Environmental Impact")
        co2_savings = st.session_state.co2_savings
        st.metric("CO₂ Savings", f"{co2_savings:.1f} kg", 
                 help="Estimated carbon savings from streaming at home vs. theater visits")
        
        # Progress bar visualization
        st.progress(min(co2_savings / 50, 1.0), 
                   text=f"{co2_savings:.1f} kg of 50 kg goal")
        st.caption("By streaming movies at home, you're helping reduce carbon emissions!")
        
        # Watchlist stats
        watchlist_count = len(st.session_state.user_preferences.get('watchlist', []))
        st.metric("Movies in Watchlist", watchlist_count)
        
        # Liked movies stats
        liked_count = len(st.session_state.user_preferences.get('liked_movies', []))
        st.metric("Liked Movies", liked_count)
    
    # Analytics visualizations
    st.markdown("### 📊 Your Taste Profile")
    
    try:
        movies_df, _, _ = st.session_state.cached_data
        liked_movies = st.session_state.user_preferences.get('liked_movies', [])
        
        if liked_movies:
            # Genre distribution of liked movies
            genre_count = defaultdict(int)
            for movie_title in liked_movies:
                movie_row = movies_df[movies_df['title'] == movie_title]
                if not movie_row.empty:
                    genres = movie_row['genres'].iloc[0]
                    if isinstance(genres, str):
                        for genre in genres.split(', '):
                            genre_count[genre.strip()] += 1
            
            if genre_count:
                genre_df = pd.DataFrame(list(genre_count.items()), columns=['Genre', 'Count'])
                genre_df = genre_df.sort_values('Count', ascending=False)
                
                fig, ax = plt.subplots(figsize=(10, 4))
                sns.barplot(x='Count', y='Genre', data=genre_df.head(8), palette="viridis", ax=ax)
                ax.set_title("Your Favorite Genres")
                st.pyplot(fig)
            else:
                st.info("No genre data available for your liked movies")
        else:
            st.info("Like some movies to see your taste profile analytics")
    except Exception as e:
        logging.error(f"Error generating taste profile: {str(e)}")
        st.error("Could not generate taste profile analytics")
    
    # Activity log
    st.markdown("### 📝 Recent Activity")
    log_file = f'user_data/{st.session_state.username}_log.csv'
    if os.path.exists(log_file):
        logs = pd.read_csv(log_file)
        if not logs.empty:
            # Show last 10 activities
            recent_logs = logs.sort_values("Timestamp", ascending=False).head(10)
            st.dataframe(recent_logs, use_container_width=True)
        else:
            st.info("No activity recorded yet")
    else:
        st.info("No activity recorded yet")
    
    # Export data option
    st.markdown("### 💾 Data Management")
    if st.button("Export My Data", key="export_data"):
        # Create a downloadable JSON file with user data
        user_data = {
            'username': st.session_state.username,
            'preferences': st.session_state.user_preferences,
            'co2_savings': st.session_state.co2_savings,
            'activity_log': log_file if os.path.exists(log_file) else None
        }
        
        json_str = json.dumps(user_data, indent=2)
        st.download_button(
            label="Download Data",
            data=json_str,
            file_name=f"{st.session_state.username}_movie_data.json",
            mime="application/json"
        )

def main_app():
    """Main application logic after login"""
    st.markdown(f'<h1 class="neon-title">🎬 Movie Recommender Pro</h1>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align: center; margin-bottom: 30px;">Welcome back, <strong>{st.session_state.username}</strong>!</div>', unsafe_allow_html=True)
    
    # Show taste preferences form if not set
    if not st.session_state.user_preferences_set or st.session_state.get('preferences_expanded', False):
        render_taste_preferences_form()
        return
    
    # Simplified tab structure
    tab1, tab2, tab3 = st.tabs(["Discover & Recommendations", "Profile & Analytics", "AI Assistant"])
    
    with tab1:
        render_discover_tab()
    with tab2:
        render_analytics_tab()
    with tab3:
        render_ai_assistant_tab()

def main():
    """Main application entry point"""
    # High contrast mode toggle
    if st.session_state.high_contrast:
        st.markdown("""
        <style>
            :root {
                --primary: #ff0000;
                --secondary: #00ffff;
                --accent: #ffff00;
                --background: #000000;
                --card: #111111;
                --text: #ffffff;
            }
        </style>
        """, unsafe_allow_html=True)
    
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
        
        /* Loading spinner */
        .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: var(--accent);
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Add animated background
    st.markdown('<div class="animated-bg"></div>', unsafe_allow_html=True)
    
    # Add JavaScript for poster click handling
    st.markdown("""
    <script>
        function set_movie_detail(movie_id) {
            window.streamlitApi.runMethod('set_movie_detail', movie_id);
        }
    </script>
    """, unsafe_allow_html=True)

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
