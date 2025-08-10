# 🔧 Improved Movie Recommender Pro - Modular and Production Ready
import os
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

# Suppress warnings
warnings.filterwarnings('ignore')

# ========================
# CONFIGURATION MANAGEMENT
# ========================
class Config:
    """Configuration management class"""
    def __init__(self):
        self.TMDB_API_KEY = os.getenv("TMDB_API_KEY", "623d4838545cb2f9581d85baa9c89ed8")
        self.USER_PROFILES_DIR = "user_profiles"
        self.USERS_FILE = "users.csv"
        self.LOGIN_ACTIVITY_FILE = "login_activity.csv"
        self.RATINGS_FILE = "ratings.csv"
        self.MODEL_NAME = 'all-MiniLM-L6-v2'
        
    def ensure_directories(self):
        """Create necessary directories"""
        os.makedirs(self.USER_PROFILES_DIR, exist_ok=True)

config = Config()
config.ensure_directories()

# ========================
# UTILITY FUNCTIONS
# ========================
class Utils:
    @staticmethod
    def safe_request(url, params=None, timeout=10):
        """Safe HTTP request with error handling"""
        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            return None

    @staticmethod
    def clean_text(text):
        """Clean and validate text input"""
        if not text or not isinstance(text, str):
            return ""
        return text.strip()[:500]  # Limit length

    @staticmethod
    def validate_movie_data(movie_data):
        """Validate movie data structure"""
        required_fields = ['id', 'title', 'overview']
        return all(field in movie_data for field in required_fields)

# ========================
# DATA MANAGEMENT
# ========================
class DataManager:
    def __init__(self):
        self.config = config
        
    def save_user_profile(self, username, user_vector, user_preferences):
        """Save user profile with error handling"""
        try:
            profile_path = os.path.join(self.config.USER_PROFILES_DIR, f"{username}_profile.pkl")
            profile_data = {
                'user_vector': user_vector,
                'user_preferences': user_preferences,
                'last_updated': datetime.now().isoformat()
            }
            with open(profile_path, 'wb') as f:
                pickle.dump(profile_data, f)
            return True
        except Exception as e:
            st.error(f"Failed to save profile: {str(e)}")
            return False

    def load_user_profile(self, username):
        """Load user profile with error handling"""
        try:
            profile_path = os.path.join(self.config.USER_PROFILES_DIR, f"{username}_profile.pkl")
            if os.path.exists(profile_path):
                with open(profile_path, 'rb') as f:
                    profile_data = pickle.load(f)
                return profile_data
            return None
        except Exception as e:
            st.error(f"Failed to load profile: {str(e)}")
            return None

    def save_login_activity(self, username):
        """Log user activity with error handling"""
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if os.path.exists(self.config.LOGIN_ACTIVITY_FILE):
                logs = pd.read_csv(self.config.LOGIN_ACTIVITY_FILE)
            else:
                logs = pd.DataFrame(columns=["Username", "Timestamp"])

            new_entry = pd.DataFrame({"Username": [username], "Timestamp": [now]})
            logs = pd.concat([logs, new_entry], ignore_index=True)
            logs.to_csv(self.config.LOGIN_ACTIVITY_FILE, index=False)
            return True
        except Exception as e:
            st.error(f"Failed to log activity: {str(e)}")
            return False

# ========================
# MOVIE DATA FETCHER
# ========================
class MovieDataFetcher:
    def __init__(self):
        self.config = config
        self.utils = Utils()
        
    def fetch_movie_details(self, movie_id):
        """Fetch detailed movie info with error handling"""
        try:
            url = f"https://api.themoviedb.org/3/movie/{movie_id}"
            params = {
                "api_key": self.config.TMDB_API_KEY,
                "append_to_response": "credits"
            }
            
            data = self.utils.safe_request(url, params)
            if not data:
                return None
                
            # Extract director safely
            director = "Unknown"
            if 'credits' in data and 'crew' in data['credits']:
                for person in data['credits']['crew']:
                    if person.get('job') == 'Director':
                        director = person.get('name', 'Unknown')
                        break
            
            # Extract top 3 actors safely
            actors = []
            if 'credits' in data and 'cast' in data['credits']:
                cast = data['credits']['cast']
                actors = [person.get('name', '') for person in cast[:3] if person.get('name')]
            
            # Extract genres safely
            genres = []
            if 'genres' in data and isinstance(data['genres'], list):
                genres = [g.get('name', '') for g in data['genres'] if g.get('name')]
            
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
                'poster_path': data.get('poster_path'),
                'original_language': data.get('original_language', 'en')
            }
        except Exception as e:
            st.error(f"Error fetching movie {movie_id}: {str(e)}")
            return None

    def fetch_popular_movies_by_year(self, years, movies_per_year=50):
        """Fetch popular movies with better error handling"""
        all_movies = []
        
        for year in years:
            try:
                # Fetch Hollywood movies
                url = "https://api.themoviedb.org/3/discover/movie"
                params = {
                    'api_key': self.config.TMDB_API_KEY,
                    'primary_release_year': year,
                    'sort_by': 'popularity.desc',
                    'page': 1
                }
                
                data = self.utils.safe_request(url, params)
                if data and 'results' in data:
                    movies = data['results'][:movies_per_year]
                    all_movies.extend([{
                        'id': m.get('id'),
                        'title': m.get('title', 'Unknown Title'),
                        'release_date': m.get('release_date', f'{year}-01-01'),
                        'poster_path': m.get('poster_path'),
                        'is_bollywood': False
                    } for m in movies if m.get('id')])
                
                # Add small delay to avoid rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                st.warning(f"Error fetching movies for {year}: {str(e)}")
                continue
        
        return all_movies

# ========================
# RECOMMENDATION ENGINE
# ========================
class RecommendationEngine:
    def __init__(self):
        self.model = None
        self.tfidf_matrix = None
        self.cosine_sim = None
        self.indices = None
        self.embeddings = None
        self.faiss_index = None
        self.movies_df = None
        
    @st.cache_resource
    def load_model(_self):
        """Load sentence transformer model with caching"""
        try:
            return SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            st.error(f"Failed to load model: {str(e)}")
            return None

    def initialize(self, movies_df):
        """Initialize recommendation engine with data"""
        try:
            self.movies_df = movies_df
            self.model = self.load_model()
            
            if self.model is None:
                return False
                
            # Precompute TF-IDF and similarity
            tfidf = TfidfVectorizer(stop_words='english')
            overviews = movies_df['overview'].fillna('').astype(str)
            self.tfidf_matrix = tfidf.fit_transform(overviews)
            self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
            self.indices = pd.Series(movies_df.index, index=movies_df['title']).drop_duplicates()
            
            # Generate embeddings
            genres = movies_df['genres'].fillna('').astype(str)
            self.embeddings = self.model.encode(genres.tolist(), show_progress_bar=False)
            
            # Create FAISS index
            dim = self.embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatL2(dim)
            self.faiss_index.add(np.array(self.embeddings))
            
            return True
            
        except Exception as e:
            st.error(f"Failed to initialize recommendation engine: {str(e)}")
            return False

    def get_recommendations(self, title=None, user_vector=None, top_n=10, selected_genres=None):
        """Get movie recommendations with error handling"""
        try:
            if title and title in self.indices:
                # Content-based recommendations
                idx = self.indices[title]
                sim_scores = list(enumerate(self.cosine_sim[idx]))
                sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
                movie_indices = [i[0] for i in sim_scores[1:top_n+1]]
                results = self.movies_df.iloc[movie_indices]
                
            elif user_vector is not None:
                # User preference based recommendations
                query_vector = user_vector.reshape(1, -1)
                _, indices = self.faiss_index.search(query_vector, top_n*3)
                results = self.movies_df.iloc[indices[0]]
                
            else:
                # Popular movies fallback
                results = self.movies_df.sort_values('weighted_score', ascending=False)
            
            # Apply genre filter if specified
            if selected_genres and len(selected_genres) > 0:
                results = results[results['genres'].apply(
                    lambda g: any(genre in str(g).split(', ') for genre in selected_genres)
                )]
            
            return results.head(top_n)
            
        except Exception as e:
            st.error(f"Recommendation failed: {str(e)}")
            return pd.DataFrame()

# ========================
# USER INTERFACE
# ========================
class MovieRecommenderUI:
    def __init__(self):
        self.data_manager = DataManager()
        self.movie_fetcher = MovieDataFetcher()
        self.recommendation_engine = RecommendationEngine()
        self.setup_page_config()
        self.apply_custom_css()
        
    def setup_page_config(self):
        """Configure Streamlit page"""
        st.set_page_config(
            page_title="🎬 Movie Recommender Pro", 
            layout="wide", 
            page_icon="🎥", 
            initial_sidebar_state="expanded"
        )

    def apply_custom_css(self):
        """Apply improved CSS with better organization"""
        st.markdown("""
        <style>
        /* Base styles */
        :root {
            --primary: #ff6b6b;
            --secondary: #4ecdc4;
            --accent: #ffbe0b;
            --background: #0f0c29;
            --card: rgba(30, 30, 46, 0.8);
            --text: #ffffff;
        }
        
        body, .main { 
            background: linear-gradient(135deg, var(--background), #24243e);
            color: var(--text);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* Card styles */
        .movie-card {
            background: var(--card);
            border-radius: 16px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
            border-left: 4px solid var(--accent);
        }
        
        .movie-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(255, 107, 107, 0.4);
        }
        
        /* Button improvements */
        .stButton>button {
            background: linear-gradient(45deg, var(--primary), var(--accent)) !important;
            color: white !important;
            border: none !important;
            border-radius: 25px !important;
            padding: 10px 25px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3) !important;
        }
        
        /* Error and success message styling */
        .stAlert {
            border-radius: 10px !important;
            border-left: 4px solid var(--accent) !important;
        }
        </style>
        """, unsafe_allow_html=True)

    def display_poster(self, poster_path, width=200):
        """Display movie poster with error handling"""
        try:
            if poster_path:
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                st.markdown(
                    f'<div style="width:{width}px"><img src="{poster_url}" style="width:100%; border-radius:10px;" alt="Movie Poster"></div>',
                    unsafe_allow_html=True
                )
                return True
        except Exception as e:
            st.error(f"Error displaying poster: {str(e)}")
        
        # Fallback placeholder
        st.markdown(
            f'<div style="width:{width}px; height:300px; background:#333; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#aaa;">No Poster Available</div>',
            unsafe_allow_html=True
        )
        return False

    def movie_card(self, movie, show_feedback=True, context="default", index=0):
        """Display movie card with improved error handling"""
        try:
            with st.container():
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    self.display_poster(movie.get('poster_path'), width=150)
                
                with col2:
                    st.subheader(movie.get('title', 'Unknown Title'))
                    
                    # Safe access to movie attributes
                    director = movie.get('director', 'Unknown')
                    actors = movie.get('actors', [])
                    vote_average = movie.get('vote_average', 0)
                    vote_count = movie.get('vote_count', 0)
                    release_date = movie.get('release_date', 'Unknown')
                    genres = movie.get('genres', '')
                    overview = movie.get('overview', 'No overview available.')
                    
                    st.markdown(f"🎬 **Director:** {director}")
                    
                    if isinstance(actors, list) and len(actors) > 0:
                        st.markdown(f"👥 **Cast:** {', '.join(actors)}")
                    
                    st.caption(f"⭐ {vote_average} | 🗳️ {vote_count} votes | 📅 {release_date}")
                    
                    # Display genres
                    if genres:
                        genre_list = genres.split(', ') if isinstance(genres, str) else []
                        if genre_list:
                            st.markdown(f"**Genres:** {', '.join(genre_list)}")
                    
                    # Overview with length limit
                    st.write(overview[:200] + "..." if len(overview) > 200 else overview)
                    
                    # Feedback buttons with unique keys
                    if show_feedback:
                        col_like, col_dislike, col_watchlist = st.columns(3)
                        
                        unique_id = f"{context}_{movie.get('id', index)}_{uuid.uuid4().hex[:6]}"
                        
                        with col_like:
                            if st.button("👍 Like", key=f"like_{unique_id}"):
                                st.success("Added to liked movies!")
                        
                        with col_dislike:
                            if st.button("👎 Dislike", key=f"dislike_{unique_id}"):
                                st.success("Added to disliked movies!")
                        
                        with col_watchlist:
                            if st.button("➕ Watchlist", key=f"watchlist_{unique_id}"):
                                st.success("Added to watchlist!")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Error displaying movie card: {str(e)}")

    def load_data_with_progress(self):
        """Load data with progress indication and error handling"""
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Loading movie data... 0%")
            
            # Fetch movies for recent years with error handling
            years = list(range(2020, 2026))  # Reduced range for faster loading
            movie_fetcher = MovieDataFetcher()
            movies_list = movie_fetcher.fetch_popular_movies_by_year(years, movies_per_year=20)
            
            progress_bar.progress(30)
            status_text.text("Processing movie details... 30%")
            
            # Process movie details with error handling
            detailed_movies = []
            for i, movie in enumerate(movies_list[:50]):  # Limit for demo
                if movie.get('id'):
                    details = movie_fetcher.fetch_movie_details(movie['id'])
                    if details and Utils.validate_movie_data(details):
                        detailed_movies.append(details)
                
                # Update progress
                if i % 10 == 0:
                    progress = 30 + (i / len(movies_list[:50])) * 50
                    progress_bar.progress(int(progress))
            
            progress_bar.progress(80)
            status_text.text("Creating recommendation engine... 80%")
            
            # Create DataFrame
            if not detailed_movies:
                raise ValueError("No valid movie data found")
                
            movies_df = pd.DataFrame(detailed_movies)
            movies_df = movies_df.drop_duplicates(subset=['id'])
            
            # Add weighted score
            v = movies_df['vote_count'].fillna(0)
            R = movies_df['vote_average'].fillna(0)
            C = movies_df['vote_average'].mean()
            m = movies_df['vote_count'].quantile(0.60)
            movies_df['weighted_score'] = ((v / (v + m)) * R) + ((m / (v + m)) * C)
            
            progress_bar.progress(100)
            status_text.text("Data loaded successfully!")
            
            # Clean up progress indicators
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            
            return movies_df
            
        except Exception as e:
            st.error(f"Failed to load data: {str(e)}")
            progress_bar.empty()
            status_text.empty()
            return pd.DataFrame()

    def run(self):
        """Main application runner"""
        try:
            st.title("🎬 Movie Recommender Pro")
            st.caption("Improved & Production Ready | Advanced ML Recommendations")
            
            # Load data
            if 'movies_data' not in st.session_state:
                with st.spinner("Loading movie database..."):
                    st.session_state.movies_data = self.load_data_with_progress()
            
            movies_df = st.session_state.movies_data
            
            if movies_df.empty:
                st.error("Failed to load movie data. Please try again later.")
                return
            
            # Initialize recommendation engine
            if not hasattr(st.session_state, 'rec_engine_initialized'):
                with st.spinner("Initializing recommendation engine..."):
                    if self.recommendation_engine.initialize(movies_df):
                        st.session_state.rec_engine_initialized = True
                        st.success("Recommendation engine ready!")
                    else:
                        st.error("Failed to initialize recommendation engine")
                        return
            
            # Sidebar
            with st.sidebar:
                st.header("🎯 Preferences")
                
                # Genre selection
                available_genres = set()
                for genres in movies_df['genres']:
                    if isinstance(genres, str):
                        for genre in genres.split(', '):
                            if genre.strip():
                                available_genres.add(genre.strip())
                
                selected_genres = st.multiselect(
                    "Select Genres", 
                    sorted(available_genres), 
                    default=[]
                )
                
                num_recommendations = st.slider("Number of Recommendations", 1, 10, 5)
                
                st.metric("Movies in Database", len(movies_df))
            
            # Main tabs
            tab1, tab2, tab3 = st.tabs(["🏠 Discover", "🔍 Search", "📊 Analytics"])
            
            with tab1:
                st.subheader("🌟 Recommended for You")
                
                # Get recommendations
                recommendations = self.recommendation_engine.get_recommendations(
                    top_n=num_recommendations,
                    selected_genres=selected_genres
                )
                
                if not recommendations.empty:
                    for _, movie in recommendations.iterrows():
                        self.movie_card(movie, context="discover")
                else:
                    st.warning("No recommendations found. Try adjusting your preferences.")
            
            with tab2:
                st.subheader("🔍 Search Movies")
                
                search_term = st.text_input("Search by title or keyword")
                
                if search_term:
                    # Simple search implementation
                    search_results = movies_df[
                        movies_df['title'].str.contains(search_term, case=False, na=False) |
                        movies_df['overview'].str.contains(search_term, case=False, na=False)
                    ]
                    
                    if not search_results.empty:
                        st.write(f"Found {len(search_results)} results")
                        for _, movie in search_results.head(5).iterrows():
                            self.movie_card(movie, context="search")
                    else:
                        st.warning("No movies found matching your search.")
            
            with tab3:
                st.subheader("📊 Movie Analytics")
                
                # Simple analytics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    avg_rating = movies_df['vote_average'].mean()
                    st.metric("Average Rating", f"{avg_rating:.1f}")
                
                with col2:
                    total_movies = len(movies_df)
                    st.metric("Total Movies", total_movies)
                
                with col3:
                    latest_year = movies_df['release_date'].str[:4].mode().iloc[0] if not movies_df.empty else "N/A"
                    st.metric("Most Common Year", latest_year)
                
                # Genre distribution
                if st.checkbox("Show Genre Distribution"):
                    genre_counts = defaultdict(int)
                    for genres in movies_df['genres']:
                        if isinstance(genres, str):
                            for genre in genres.split(', '):
                                if genre.strip():
                                    genre_counts[genre.strip()] += 1
                    
                    if genre_counts:
                        genre_df = pd.DataFrame(list(genre_counts.items()), columns=['Genre', 'Count'])
                        genre_df = genre_df.sort_values('Count', ascending=False).head(10)
                        st.bar_chart(genre_df.set_index('Genre'))
                
        except Exception as e:
            st.error(f"Application error: {str(e)}")
            st.info("Please refresh the page to try again.")

# ========================
# MAIN APPLICATION
# ========================
def main():
    """Main function with error handling"""
    try:
        # Disable warnings for cleaner output
        os.environ["PYTHONWARNINGS"] = "ignore"
        
        # Initialize and run the application
        app = MovieRecommenderUI()
        app.run()
        
    except Exception as e:
        st.error(f"Critical error: {str(e)}")
        st.info("Please check your internet connection and try again.")

if __name__ == "__main__":
    main()
