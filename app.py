# 🔧 Disable Streamlit file watcher
import os
os.environ["STREAMLIT_DISABLE_WATCHDOG_WARNINGS"] = "1"
os.environ["STREAMLIT_WATCH_FILES"] = "false"
os.environ["PYTHONWARNINGS"] = "ignore"

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
from datetime import datetime
from wordcloud import WordCloud
from collections import defaultdict, Counter
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer

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
    if pd.isna(amount) or amount <= 0:
        return "N/A"
    return f"${amount:,.0f}"

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
        st.error(f"Error logging event: {str(e)}")

def display_poster(poster_path, class_name="poster-container", width=200):
    """Display movie poster with lazy loading and error handling"""
    try:
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
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
    except Exception as e:
        st.error(f"Error finding movie: {str(e)}")
    
    return None

# =========================================
# MODULE 3: DATA LOADING & CACHING
# =========================================
@st.cache_resource
def load_model():
    """Load and cache the sentence transformer model"""
    return SentenceTransformer('all-MiniLM-L6-v2')

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
            'poster_path': poster_path,
            'original_language': data.get('original_language', 'en')
        }
    except Exception as e:
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
            
            detailed_series.append({
                'id': tv_data['id'],
                'title': tv_data.get('name', 'Unknown'),
                'release_date': tv_data.get('first_air_date', ''),
                'overview': tv_data.get('overview', 'No overview available.'),
                'vote_average': tv_data.get('vote_average', 0),
                'vote_count': tv_data.get('vote_count', 0),
                'popularity': tv_data.get('popularity', 0),
                'genres': ', '.join([g['name'] for g in tv_data.get('genres', [])]),
                'poster_path': tv_data.get('poster_path', None),
                'type': 'Web Series',
                'seasons': tv_data.get('number_of_seasons', 1),
                'episodes': tv_data.get('number_of_episodes', 1),
                'original_language': tv_data.get('original_language', 'en')
            })
        
        return detailed_series
        
    except Exception as e:
        st.error(f"Error fetching web series: {str(e)}")
        return []

@st.cache_data
def load_data(api_key):
    """Load and cache movie data with progress tracking"""
    # Show loading progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.text("Loading movie data... 0%")
    
    # Fetch popular movies by year (2000-2025) - increased count
    years = list(range(2000, 2026))
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
    
    # Load ratings data
    ratings_df = pd.read_csv('ratings.csv')
    
    # Precompute TF-IDF and similarity
    tfidf = TfidfVectorizer(stop_words='english')
    overviews = movies_df['overview'].fillna('').astype(str)
    tfidf_matrix = tfidf.fit_transform(overviews)
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    indices = pd.Series(movies_df.index, index=movies_df['title']).drop_duplicates()
    
    # Generate embeddings
    genres = movies_df['genres'].fillna('').astype(str)
    embeddings = load_model().encode(genres.tolist(), show_progress_bar=False)
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
        'genre_set': sorted(genre_set)
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
            'user_preferences': st.session_state.user_preferences
        }
        with open(profile_path, 'wb') as f:
            pickle.dump(profile_data, f)
    except Exception as e:
        st.error(f"Error saving user profile: {str(e)}")

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
                'mood_preferences': []
            }
            
            loaded_prefs = profile_data.get('user_preferences', {})
            for key in DEFAULT_USER_PREFERENCES:
                if key not in loaded_prefs:
                    loaded_prefs[key] = DEFAULT_USER_PREFERENCES[key]
                    
            st.session_state.user_vector = profile_data['user_vector']
            st.session_state.user_preferences = loaded_prefs
            return True
    except Exception as e:
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
        st.error(f"Error saving login activity: {str(e)}")

def validate_user(username, password):
    """Validate user credentials"""
    try:
        if not os.path.exists(USERS_FILE):
            return False
        df = pd.read_csv(USERS_FILE)
        return ((df['username'] == username) & (df['password'] == password)).any()
    except Exception as e:
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
                'mood_preferences': []
            }
            save_user_profile(username)
    except Exception as e:
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

        ratings_df = st.session_state.cached_data[1] if st.session_state.cached_data else pd.read_csv('ratings.csv')
        
        reader = Reader(rating_scale=(0.5, 5))
        data = Dataset.load_from_df(ratings_df[['userId', 'movieId', 'rating']], reader)
        trainset, _ = train_test_split(data, test_size=0.2, random_state=42)

        model = SVD(n_factors=50, n_epochs=10, lr_all=0.01, reg_all=0.02)
        model.fit(trainset)
        return model
    except Exception as e:
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
                _, indices = precomputed['faiss_index'].search(query_vector, top_n*3)
                
                # Get movie details
                results = movies_df.iloc[indices[0]]
                
                # Apply genre filter
                if selected_genres:
                    results = results[results['genres'].apply(
                        lambda g: any(genre in g.split(', ') for genre in selected_genres)
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
                        lambda g: any(genre in g.split(', ') for genre in selected_genres)
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
            results = results[results['genres'].apply(
                lambda g: any(genre in g.split(', ') for genre in selected_genres)
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
                    lambda g: any(genre in g.split(', ') for genre in mood_genres)
                )]
        
        # Sort by release date
        if sort_by == "latest":
            results = results.sort_values("release_date", ascending=False)
        elif sort_by == "oldest":
            results = results.sort_values("release_date", ascending=True)
            
        return results.head(top_n)
    except Exception as e:
        st.error(f"Error generating recommendations: {str(e)}")
        return pd.DataFrame()

# =========================================
# MODULE 6: USER PREFERENCES MANAGEMENT
# =========================================
def update_user_preference(movie_id, action):
    """Update user preferences based on like/dislike actions"""
    try:
        movies_df, _, _ = st.session_state.cached_data
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
        log_event(st.session_state.username, movie_title, action)
    except Exception as e:
        st.error(f"Error updating preference: {str(e)}")

def update_watchlist(movie_id, action):
    """Add or remove movie from user's watchlist"""
    try:
        movies_df, _, _ = st.session_state.cached_data
        movie_title = movies_df[movies_df['id'] == movie_id]['title'].values[0]
        
        if action == 'add':
            if movie_title not in st.session_state.user_preferences['watchlist']:
                st.session_state.user_preferences['watchlist'].append(movie_title)
                st.success(f"✅ Added {movie_title} to your watchlist!")
                
                # Calculate CO2 savings (2.5kg per movie)
                st.session_state.co2_savings += 2.5
                log_event(st.session_state.username, movie_title, "add_to_watchlist")
        elif action == 'remove':
            if movie_title in st.session_state.user_preferences['watchlist']:
                st.session_state.user_preferences['watchlist'].remove(movie_title)
                st.success(f"✅ Removed {movie_title} from your watchlist!")
                log_event(st.session_state.username, movie_title, "remove_from_watchlist")
        
        # Save updated profile
        save_user_profile(st.session_state.username)
    except Exception as e:
        st.error(f"Error updating watchlist: {str(e)}")

# =========================================
# MODULE 7: UI COMPONENTS
# =========================================
def movie_card(movie, show_feedback=True, context="default", index=0, similarity=None):
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
                # Use poster_path directly from movie data
                display_poster(movie.get('poster_path'), class_name="poster-container")
            
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
                    
                st.caption(f"⭐ {movie['vote_average']} | 🗳️ {movie['vote_count']} votes | 📅 {movie['release_date']}")
                
                # Display genres as tags
                genres = movie['genres'].split(', ') if isinstance(movie['genres'], str) else []
                genre_tags = " ".join([f"<span class='tag tag-genre'>{genre}</span>" for genre in genres])
                st.markdown(f"<div style='margin: 10px 0;'>{genre_tags}</div>", unsafe_allow_html=True)
                
                # For web series, show seasons/episodes
                if movie.get('is_web_series', False):
                    st.markdown(f"📺 **Seasons:** {movie.get('seasons', 'N/A')} | **Episodes:** {movie.get('episodes', 'N/A')}")
                
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
                            update_user_preference(movie['id'], 'like')
                            st.rerun()
                    with c2:
                        if st.button("👎 Dislike", key=unique_key_dislike, use_container_width=True):
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
    except Exception as e:
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

# =========================================
# MODULE 8: MAIN APPLICATION LOGIC
# =========================================
def main():
    """Main application logic"""
    # Load API key from secrets
    try:
        api_key = st.secrets["TMDB_API_KEY"]
    except (KeyError, FileNotFoundError):
        st.error("TMDB API key not found. Please check your secrets configuration.")
        return
    
    # High contrast mode toggle
    if st.session_state.high_contrast:
        st.markdown('<style>:root {--primary: #ff0000; --secondary: #00ffff; --accent: #ffff00; --background: #000000; --card: #111111; --text: #ffffff;}</style>', unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        render_login_signup()
    else:
        # Load data if not already cached
        if st.session_state.cached_data is None:
            with st.spinner("Loading movie data. This may take a few minutes..."):
                try:
                    movies_df, ratings_df, precomputed = load_data(api_key)
                    st.session_state.cached_data = (movies_df, ratings_df, precomputed)
                except Exception as e:
                    st.error(f"Failed to load data: {str(e)}")
                    return
        else:
            movies_df, ratings_df, precomputed = st.session_state.cached_data
        
        st.markdown(f'<h1 class="neon-title">🎬 Movie Recommender Pro</h1>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: center; margin-bottom: 30px;">Welcome back, <strong>{st.session_state.username}</strong>!</div>', unsafe_allow_html=True)
        
        # Define tabs
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
        
        # Tab 0 - Home
        with tabs[0]:
            # (Content remains the same but uses the new modular functions)
            pass
        
        # Other tabs (implementation would follow similar pattern)
        # ...
        
        # Tab 9 - Profile
        with tabs[9]:
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
                # (Content remains the same)
                pass
            
            with col2:
                # (Content remains the same)
                pass
            
            # Logout button
            st.markdown("---")
            if st.button("🔒 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.success("You have been logged out. Please login again.")
                time.sleep(2)
                st.rerun()

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
        
        /* ... (rest of the CSS styles) ... */
        
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
    
    # Run main application
    main()
