# 🔧 Disable Streamlit file watcher
import os
os.environ["STREAMLIT_DISABLE_WATCHDOG_WARNINGS"] = "1"
os.environ["STREAMLIT_WATCH_FILES"] = "false"
os.environ["PYTHONWARNINGS"] = "ignore"

# Add your custom CSS here at the VERY TOP
# Add custom CSS for modern UI
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap');
    
    :root {
        --primary: #1a2a6c;
        --secondary: #0a5f38;
        --accent: #00c853;
        --accent2: #00b8d4;
        --dark: #0a0f1f;
        --darker: #050916;
        --light: #f8f9fa;
        --success: #00c853;
        --danger: #ff5252;
        --warning: #ffab00;
        --info: #2962ff;
        --card-bg: rgba(255, 255, 255, 0.9);
        --card-border: rgba(0, 0, 0, 0.1);
        --vibrant-blue: rgba(70, 130, 180, 0.8);
        --vibrant-green: rgba(50, 205, 50, 0.8);
        --vibrant-orange: rgba(255, 140, 0, 0.8);
        --vibrant-red: rgba(220, 20, 60, 0.8);
        --vibrant-pink: rgba(255, 20, 147, 0.8);
        --vibrant-cyan: rgba(0, 255, 255, 0.8);
        --vibrant-teal: rgba(0, 150, 136, 0.8);
    }
    
    * {
        font-family: 'Montserrat', sans-serif;
    }
    
    body {
        background: linear-gradient(135deg, var(--darker), var(--dark));
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: var(--light) !important;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50% }
        50% { background-position: 100% 50% }
        100% { background-position: 0% 50% }
    }
    
    .header { 
        font-size: 3rem; 
        font-weight: 800; 
        background: linear-gradient(90deg, var(--accent), var(--accent2));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 20px;
        text-shadow: 0 0 20px rgba(0, 200, 83, 0.3);
        letter-spacing: 1px;
        animation: glow 1.5s ease-in-out infinite alternate;
    }
    
    .subheader {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(90deg, var(--accent), var(--accent2));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        border-bottom: 3px solid var(--accent);
        padding-bottom: 10px;
        margin-top: 20px;
        margin-bottom: 25px;
    }
    
    .metric-card {
        background: var(--vibrant-teal);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid var(--card-border);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        transition: all 0.4s ease;
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
        color: white;
        z-index: 1;
    }
    
    .metric-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
        border: 1px solid var(--accent);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #1d976c, #93f9b9, #00b8d4, #0052d4);
        z-index: -1;
        filter: blur(5px);
        animation: glowing 3s ease-in-out infinite alternate;
        background-size: 400% 400%;
    }
    
    @keyframes glowing {
        0% { background-position: 0% 50%; opacity: 0.5; }
        100% { background-position: 100% 50%; opacity: 0.8; }
    }
    
    .stButton>button {
        background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
        color: white !important;
        border-radius: 30px !important;
        font-weight: 600 !important;
        padding: 10px 25px !important;
        border: none !important;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
        position: relative;
        overflow: hidden;
    }
    
    .stButton>button::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #1d976c, #93f9b9, #00b8d4, #0052d4);
        z-index: -1;
        filter: blur(5px);
        animation: glowing 3s ease-in-out infinite alternate;
        background-size: 400% 400%;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 200, 83, 0.4);
    }
    
    .news-item {
        padding: 20px;
        margin-bottom: 20px;
        border-radius: 12px;
        font-size: 1rem;
        font-weight: 500;
        background: var(--vibrant-green);
        border: 1px solid var(--card-border);
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        animation: fadeIn 0.6s ease-out;
        position: relative;
        overflow: hidden;
        z-index: 1;
        color: black;
    }
    
    .news-item::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #1d976c, #93f9b9, #00b8d4, #0052d4);
        z-index: -1;
        filter: blur(5px);
        animation: glowing 3s ease-in-out infinite alternate;
        background-size: 400% 400%;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .news-item:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 25px rgba(0, 0, 0, 0.2);
    }
    
    .positive {
        border-left: 6px solid var(--success);
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.3), var(--vibrant-green));
    }
    
    .negative {
        border-left: 6px solid var(--danger);
        background: linear-gradient(135deg, rgba(244, 67, 54, 0.3), var(--vibrant-green));
    }
    
    .neutral {
        border-left: 6px solid var(--info);
        background: linear-gradient(135deg, rgba(41, 98, 255, 0.3), var(--vibrant-green));
    }
    
    .news-item a {
        color: #1a2a6c !important;
        font-weight: bold;
        text-decoration: none;
        transition: all 0.3s ease;
    }
    
    .news-item a:hover {
        color: #0a5f38 !important;
        text-decoration: underline;
    }
    
    .feature-card {
        background: var(--vibrant-teal);
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        border: 1px solid var(--card-border);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        transition: all 0.4s ease;
        backdrop-filter: blur(10px);
        animation: cardAppear 0.8s ease-out;
        color: white;
        position: relative;
        overflow: hidden;
        z-index: 1;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #1d976c, #93f9b9, #00b8d4, #0052d4);
        z-index: -1;
        filter: blur(5px);
        animation: glowing 3s ease-in-out infinite alternate;
        background-size: 400% 400%;
    }
    
    @keyframes cardAppear {
        0% { opacity: 0; transform: scale(0.95); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    .feature-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
        border: 1px solid var(--accent);
    }
    
    .feature-card h3 {
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 15px;
        border-bottom: 2px solid rgba(255, 255, 255, 0.3);
        padding-bottom: 10px;
    }
    
    .feature-card h4 {
        color: white;
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 15px;
    }
    
    .feature-card ul {
        padding-left: 20px;
        margin-bottom: 15px;
    }
    
    .feature-card li {
        margin-bottom: 10px;
        position: relative;
        padding-left: 20px;
        color: white;
    }
    
    .feature-card li::before {
        content: '•';
        color: white;
        position: absolute;
        left: 0;
        font-size: 1.5rem;
    }
    
    .gauge {
        text-align: center;
        padding: 20px;
        border-radius: 15px;
        background: linear-gradient(90deg, var(--danger) 0%, var(--warning) 50%, var(--success) 100%);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        margin: 20px 0;
        animation: pulse 2s infinite;
        position: relative;
        overflow: hidden;
        z-index: 1;
    }
    
    .gauge::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #1d976c, #93f9b9, #00b8d4, #0052d4);
        z-index: -1;
        filter: blur(5px);
        animation: glowing 3s ease-in-out infinite alternate;
        background-size: 400% 400%;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(0, 200, 83, 0.4); }
        70% { box-shadow: 0 0 0 15px rgba(0, 200, 83, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 200, 83, 0); }
    }
    
    .gauge-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--accent);
        text-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
        margin: 10px 0;
    }
    
    .stTabs [role="tablist"] {
        background: rgba(19, 28, 58, 0.8) !important;
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 30px;
        border: 1px solid var(--card-border);
        position: relative;
        overflow: hidden;
        z-index: 1;
    }
    
    .stTabs [role="tablist"]::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #1d976c, #93f9b9, #00b8d4, #0052d4);
        z-index: -1;
        filter: blur(5px);
        animation: glowing 3s ease-in-out infinite alternate;
        background-size: 400% 400%;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
        color: white !important;
        font-weight: 600;
        border-radius: 12px !important;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    }
    
    .stTabs [role="tab"] {
        color: var(--light) !important;
        padding: 10px 20px !important;
        border-radius: 12px !important;
        transition: all 0.3s ease;
    }
    
    .stTabs [role="tab"]:hover {
        background: rgba(0, 200, 83, 0.1) !important;
    }
    
    .ai-response {
        background: linear-gradient(135deg, var(--vibrant-teal), var(--vibrant-cyan));
        padding: 25px;
        border-radius: 15px;
        margin-top: 20px;
        border-left: 4px solid var(--accent);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        animation: fadeIn 0.8s ease-out;
        position: relative;
        overflow: hidden;
        z-index: 1;
        color: white;
    }
    
    .ai-response::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #1d976c, #93f9b9, #00b8d4, #0052d4);
        z-index: -1;
        filter: blur(5px);
        animation: glowing 3s ease-in-out infinite alternate;
        background-size: 400% 400%;
    }
    
    .strategy-card {
        background: var(--vibrant-teal);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        cursor: pointer;
        transition: all 0.4s ease;
        border: 1px solid var(--card-border);
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
        z-index: 1;
        color: var(--accent);
    }
    
    .strategy-card::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #1d976c, #93f9b9, #00b8d4, #0052d4);
        z-index: -1;
        filter: blur(5px);
        animation: glowing 3s ease-in-out infinite alternate;
        background-size: 400% 400%;
    }
    
    .strategy-card:hover {
        transform: scale(1.03);
        box-shadow: 0 12px 25px rgba(0, 0, 0, 0.4);
        border: 1px solid var(--accent);
    }
    
    .strategy-card h4 {
        color: var(--accent);
        font-size: 1.5rem;
        margin-bottom: 15px;
    }
    
    .macro-metric {
        background: var(--vibrant-teal);
        border-radius: 15px;
        padding: 20px;
        margin: 15px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        border: 1px solid var(--card-border);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        z-index: 1;
        color: white;
    }
    
    .macro-metric::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #1d976c, #93f9b9, #00b8d4, #0052d4);
        z-index: -1;
        filter: blur(5px);
        animation: glowing 3s ease-in-out infinite alternate;
        background-size: 400% 400%;
    }
    
    .macro-metric:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 25px rgba(0, 200, 83, 0.2);
    }
    
    .macro-metric h5 {
        color: white;
        margin-bottom: 15px;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    .options-payoff {
        background: linear-gradient(135deg, var(--vibrant-teal), var(--vibrant-orange));
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        border: 1px solid var(--card-border);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
        z-index: 1;
    }
    
    .options-payoff::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #1d976c, #93f9b9, #00b8d4, #0052d4);
        z-index: -1;
        filter: blur(5px);
        animation: glowing 3s ease-in-out infinite alternate;
        background-size: 400% 400%;
    }
    
    .stAlert {
        border-radius: 15px !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid var(--card-border) !important;
        position: relative;
        overflow: hidden;
        z-index: 1;
    }
    
    .stAlert::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #1d976c, #93f9b9, #00b8d4, #0052d4);
        z-index: -1;
        filter: blur(5px);
        animation: glowing 3s ease-in-out infinite alternate;
        background-size: 400% 400%;
    }
    
    .stSpinner > div {
        background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    .glow-text {
        text-shadow: 0 0 10px var(--accent), 0 0 20px var(--accent);
        animation: glow 1.5s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { text-shadow: 0 0 5px var(--accent), 0 0 10px var(--accent); }
        to { text-shadow: 0 0 15px var(--accent), 0 0 30px var(--accent); }
    }
    
    /* Attention heatmap styling */
    .attention-heatmap {
        border-radius: 15px;
        padding: 20px;
        background: var(--vibrant-teal);
        margin: 20px 0;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
    }
    
    .shap-plot {
        border-radius: 15px;
        padding: 20px;
        background: var(--vibrant-teal);
        margin: 20px 0;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Movie card styling */
    .movie-card {
        background: var(--vibrant-teal);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border: 1px solid var(--card-border);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        transition: all 0.4s ease;
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
        color: white;
        z-index: 1;
    }
    
    .movie-card::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #1d976c, #93f9b9, #00b8d4, #0052d4);
        z-index: -1;
        filter: blur(5px);
        animation: glowing 3s ease-in-out infinite alternate;
        background-size: 400% 400%;
    }
    
    .movie-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
        border: 1px solid var(--accent);
    }
    
    .poster-container {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        transition: all 0.4s ease;
    }
    
    .poster-container:hover {
        transform: scale(1.05);
    }
    
    .poster-img {
        width: 100%;
        height: auto;
        border-radius: 15px;
    }
    
    .tag {
        display: inline-block;
        background: rgba(78, 205, 196, 0.2);
        border-radius: 20px;
        padding: 6px 15px;
        margin-right: 8px;
        margin-bottom: 8px;
        font-size: 0.85rem;
        color: white;
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
    
    .neon-title {
        text-shadow: 0 0 10px var(--primary), 
                    0 0 20px var(--primary), 
                    0 0 30px var(--accent);
    }
</style>
"""

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
    if "user_preferences_set" not in st.session_state:
        st.session_state.user_preferences_set = False

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
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

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
@st.cache_resource(show_spinner=False)
def load_model():
    """Load and cache the sentence transformer model - simplified to avoid tokenization issues"""
    try:
        return SentenceTransformer('all-MiniLM-L6-v2')
    except Exception as e:
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
            'user_preferences': st.session_state.user_preferences,
            'user_preferences_set': st.session_state.user_preferences_set
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
                'mood_preferences': [],
                'preferred_era': "Any",
                'preferred_actors': [],
                'preferred_directors': []
            }
            st.session_state.user_preferences_set = False
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
                distances, indices = precomputed['faiss_index'].search(query_vector, top_n*3)
                
                # Get movie details
                results = movies_df.iloc[indices[0]]
                
                # Calculate similarity scores (1 - normalized distance)
                max_distance = distances[0].max()
                results['similarity'] = 1 - (distances[0] / max_distance)
                
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
                    lambda g: any(genre in g.split(', ') for genre in preferred_genres)
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
        st.error(f"Error getting personalized recommendations: {str(e)}")
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
                
            # Update user vector - more significant impact for likes
            movie_idx = movies_df.index[movies_df['id'] == movie_id].tolist()[0]
            movie_embedding = st.session_state.cached_data[2]['embeddings'][movie_idx]
            
            if st.session_state.user_vector is None:
                st.session_state.user_vector = movie_embedding
            else:
                st.session_state.user_vector = st.session_state.user_vector * 0.5 + movie_embedding * 0.5
                
        elif action == 'dislike':
            if movie_title in st.session_state.user_preferences['liked_movies']:
                st.session_state.user_preferences['liked_movies'].remove(movie_title)
            if movie_title not in st.session_state.user_preferences['disliked_movies']:
                st.session_state.user_preferences['disliked_movies'].append(movie_title)
            
            # Update user vector - less significant impact for dislikes
            movie_idx = movies_df.index[movies_df['id'] == movie_id].tolist()[0]
            movie_embedding = st.session_state.cached_data[2]['embeddings'][movie_idx]
            
            if st.session_state.user_vector is not None:
                st.session_state.user_vector = st.session_state.user_vector * 0.9 - movie_embedding * 0.1
        
        # Save updated profile
        save_user_profile(st.session_state.username)
        log_event(st.session_state.username, movie_title, action)
        
        # Force UI refresh to show updated recommendations
        st.rerun()
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

def save_user_taste_preferences():
    """Save user's taste preferences from the form"""
    try:
        st.session_state.user_preferences_set = True
        save_user_profile(st.session_state.username)
        st.success("Preferences saved successfully! 🎉")
        st.session_state.preferences_expanded = False
        st.rerun()
    except Exception as e:
        st.error(f"Error saving preferences: {str(e)}")

# =========================================
# MODULE 7: UI COMPONENTS
# =========================================
def movie_card(movie, show_feedback=True, context="default", index=0):
    """Display movie information in a styled card with new UI"""
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
            
            st.markdown(f"<div class='movie-card'>", unsafe_allow_html=True)
            
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
                    unique_key_like = f"{context}_like_{movie['id']}_{index}_{uuid.uuid4().hex[:6]}"
                    unique_key_dislike = f"{context}_dislike_{movie['id']}_{index}_{uuid.uuid4().hex[:6]}"
                    unique_key_watchlist = f"{context}_watchlist_{movie['id']}_{index}_{uuid.uuid4().hex[:6]}"
                    
                    with c1:
                        if st.button("👍 Like", key=unique_key_like, use_container_width=True):
                            update_user_preference(movie['id'], 'like')
                    with c2:
                        if st.button("👎 Dislike", key=unique_key_dislike, use_container_width=True):
                            update_user_preference(movie['id'], 'dislike')
                    with c3:
                        # Safely access watchlist with default
                        watchlist = st.session_state.user_preferences.get('watchlist', [])
                        if movie['title'] in watchlist:
                            if st.button("❌ Remove Watchlist", key=unique_key_watchlist, use_container_width=True):
                                update_watchlist(movie['id'], 'remove')
                        else:
                            if st.button("➕ Add to Watchlist", key=unique_key_watchlist, use_container_width=True):
                                update_watchlist(movie['id'], 'add')

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
                st.rerun()
            else:
                st.warning("⚠️ Username already exists. Try logging in.")

def render_taste_preferences_form():
    """Render the taste preferences form"""
    with st.expander("🎬 Tell Us Your Movie Preferences", expanded=True):
        st.write("Help us recommend movies you'll love by telling us about your tastes:")
        
        # Get available data
        movies_df, _, precomputed = st.session_state.cached_data
        
        # Favorite genres
        st.subheader("Favorite Genres")
        selected_genres = st.multiselect(
            "Select your favorite genres (select up to 5)", 
            precomputed['genre_set'],
            default=st.session_state.user_preferences.get('preferred_genres', []),
            max_selections=5
        )
        
        # Preferred era
        st.subheader("Preferred Movie Era")
        era_options = ["Any", "Recent (2010-Now)", "Classic (Pre-2000)"]
        selected_era = st.selectbox(
            "Which era of movies do you prefer?",
            era_options,
            index=era_options.index(st.session_state.user_preferences.get('preferred_era', "Any"))
        )
        
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
            st.session_state.user_preferences['preferred_genres'] = selected_genres
            st.session_state.user_preferences['preferred_era'] = selected_era
            st.session_state.user_preferences['preferred_actors'] = selected_actors
            st.session_state.user_preferences['preferred_directors'] = selected_directors
            st.session_state.user_preferences_set = True
            save_user_profile(st.session_state.username)
            st.success("Preferences saved successfully! 🎉")
            st.rerun()

# =========================================
# MODULE 8: MAIN APPLICATION LOGIC
# =========================================
def render_home_tab():
    """Render the home tab content"""
    # Get data
    movies_df, _, precomputed = st.session_state.cached_data
    
    # Show taste preferences form if not set
    if not st.session_state.user_preferences_set:
        render_taste_preferences_form()
    
    # Project description
    with st.expander("🌟 About Movie Recommender Pro", expanded=True):
        st.markdown("""
        <div style="padding: 20px; border-radius: 15px; background: linear-gradient(135deg, rgba(255, 107, 107, 0.2), rgba(78, 205, 196, 0.2));">
            <h3 style="color: #ffbe0b; text-align: center;">Discover Your Next Favorite Movie!</h3>
            <p style="font-size: 1.1rem;">Movie Recommender Pro uses advanced AI algorithms to find perfect movie matches based on your unique preferences. 
            Our hybrid recommendation system combines multiple techniques to deliver personalized suggestions.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature showcase
        st.subheader("✨ Key Features")
        
        # Feature cards in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h4>🔍 Smart Search</h4>
                <p>Find movies by title, genre, or keywords</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="feature-card">
                <h4>🤖 AI Recommendations</h4>
                <p>Deep learning models personalize suggestions</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h4>💡 Hybrid System</h4>
                <p>Combines content-based and collaborative filtering</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="feature-card">
                <h4>📈 Visual Analytics</h4>
                <p>Explore movie trends and genre distributions</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown("""
            <div class="feature-card">
                <h4>👤 Personal Profile</h4>
                <p>Track your liked/disliked movies</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="feature-card">
                <h4>🌱 Sustainability Focus</h4>
                <p>Track your environmental impact</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Real-time data section
    st.subheader("🔥 Real-Time Trending")
    realtime_data = fetch_realtime_data(st.secrets["TMDB_API_KEY"])
    
    if realtime_data['trending']:
        st.markdown("### 🚀 Trending Today")
        cols = st.columns(5)
        for idx, movie in enumerate(realtime_data['trending'][:5]):
            with cols[idx % 5]:
                display_poster(movie.get('poster_path'), class_name="poster-container", width=150)
                st.caption(f"**{movie['title']}**")
                st.caption(f"⭐ {movie.get('vote_average', 'N/A')}")
    
    if realtime_data['new_releases']:
        st.markdown("### 🆕 New Releases")
        cols = st.columns(5)
        for idx, movie in enumerate(realtime_data['new_releases'][:5]):
            with cols[idx % 5]:
                display_poster(movie.get('poster_path'), class_name="poster-container", width=150)
                st.caption(f"**{movie['title']}**")
                st.caption(f"📅 {movie.get('release_date', 'N/A')}")
    
    # Bollywood section
    st.markdown("### 🎬 Bollywood Spotlight")
    bollywood_movies = movies_df[movies_df['is_bollywood'] == True].sort_values('weighted_score', ascending=False).head(10)
    
    if not bollywood_movies.empty:
        cols = st.columns(5)
        for idx, (_, row) in enumerate(bollywood_movies.head(5).iterrows()):
            with cols[idx % 5]:
                display_poster(row.get('poster_path'), class_name="poster-container", width=150)
                st.caption(f"**{row['title']}**")
                st.progress(row['weighted_score'] / 10, text=f"⭐ {row['vote_average']}")
    else:
        st.info("No Bollywood movies available")
    
    # Personalized Recommendations
    st.markdown("### 🎯 Personalized Recommendations For You")
    if st.session_state.user_preferences_set:
        personalized = get_personalized_recommendations(top_n=3)
        if not personalized.empty:
            for _, row in personalized.iterrows():
                movie_card(row, context="home")
        else:
            st.info("No personalized recommendations found. Try expanding your preferences.")
    else:
        st.info("Complete your taste preferences to get personalized recommendations")
    
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

def render_search_tab():
    """Render the search tab content"""
    movies_df, _, _ = st.session_state.cached_data
    st.subheader("🔍 Search Movies")
    search_term = st.text_input("Search by title, genre, or keyword")
    
    if search_term:
        try:
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
                for _, row in results.head(10).iterrows():
                    movie_card(row, show_feedback=True, context="search")
            else:
                st.warning("No movies found matching your search")
        except Exception as e:
            st.error(f"Error during search: {str(e)}")

def render_popular_tab():
    """Render the popular movies tab"""
    movies_df, _, _ = st.session_state.cached_data
    st.subheader("📂 Browse Movie Database")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        sort_options = [
            "Title", "Rating", "Popularity", "Release Date (Newest)", 
            "Release Date (Oldest)", "Budget (High to Low)", "Budget (Low to High)"
        ]
        sort_by = st.selectbox("Sort by", sort_options, key="popular_sort")
    with col2:
        num_movies = st.slider("Number per page", 10, 100, 20, key="num_movies_slider")
    
    # Pagination
    page_number = st.number_input("Page", min_value=1, value=1, step=1)
    start_idx = (page_number - 1) * num_movies
    end_idx = start_idx + num_movies
    
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
    
    # Display the slice
    st.write(f"📖 Showing {start_idx+1} - {min(end_idx, len(sorted_df))} of {len(sorted_df)} movies")
    for _, row in sorted_df.iloc[start_idx:end_idx].iterrows():
        movie_card(row, context="browse")

def render_genre_tab():
    """Render the genre filter tab"""
    movies_df, _, precomputed = st.session_state.cached_data
    st.subheader("🎯 Discover by Genre")
    # Get available genres
    available_genres = precomputed['genre_set']
    valid_defaults = ["Action", "Comedy"]
    
    selected_genres = st.multiselect(
        "Select genres", 
        available_genres, 
        default=valid_defaults, 
        key="genre_filter"
    )
    
    if selected_genres:
        try:
            # Use exact match filtering
            filtered = movies_df[movies_df['genres'].apply(
                lambda g: any(genre in g.split(', ') for genre in selected_genres)
            )]
            
            # Validation for empty results
            if len(filtered) == 0:
                st.warning("No movies found with the selected genres")
                return
                
            st.write(f"🎬 Found {len(filtered)} movies")
            
            # Pagination
            num_per_page = st.slider("Movies per page", 5, 50, 10, key="genre_per_page")
            page = st.number_input("Page", min_value=1, max_value=len(filtered)//num_per_page+1, value=1)
            start = (page-1) * num_per_page
            end = start + num_per_page
            
            # Display results
            for _, row in filtered.iloc[start:end].iterrows():
                movie_card(row, context="genre")
        except Exception as e:
            st.error(f"Error filtering by genre: {str(e)}")
    else:
        st.warning("Please select at least one genre")

def render_latest_tab():
    """Render the latest releases tab"""
    movies_df, _, precomputed = st.session_state.cached_data
    st.subheader("🎬 Latest Movie Releases")
    
    # Year selector
    selected_year = st.selectbox("Select Year", list(range(2018, 2026)), index=2024-2018)
    
    # Get movies for selected year
    current_year_movies = movies_df[
        (movies_df['release_date'].str.startswith(str(selected_year))) | 
        (movies_df['release_date'].str.contains(f"^{selected_year}-", na=False))
    ]
    
    # Count movies by industry
    hollywood_count = len(current_year_movies[current_year_movies['is_bollywood'] == False])
    bollywood_count = len(current_year_movies[current_year_movies['is_bollywood'] == True])
    
    st.markdown(f"### 🎉 Movies of {selected_year}")
    st.write(f"🎥 **Hollywood:** {hollywood_count} movies | 🎬 **Bollywood:** {bollywood_count} movies")
    
    if not current_year_movies.empty:
        # Genre filter
        selected_genres = st.multiselect("Filter by genres", precomputed['genre_set'], key="latest_genre_filter")
        
        if selected_genres:
            def genre_filter(genres_str):
                if not isinstance(genres_str, str):
                    return False
                genres_list = [g.strip() for g in genres_str.split(',')]
                return any(genre in genres_list for genre in selected_genres)
            
            current_year_movies = current_year_movies[current_year_movies['genres'].apply(genre_filter)]
        
        st.write(f"📊 **Filtered:** {len(current_year_movies)} movies")
        
        # Sort by release date (newest first)
        current_year_movies = current_year_movies.sort_values("release_date", ascending=False)
        
        # Pagination
        num_per_page = st.slider("Movies per page", 10, 100, 20, key="latest_per_page")
        page = st.number_input("Page", min_value=1, max_value=len(current_year_movies)//num_per_page+1, value=1)
        start = (page-1) * num_per_page
        end = start + num_per_page
        
        # Show movie cards
        for _, row in current_year_movies.iloc[start:end].iterrows():
            movie_card(row, context="latest", show_feedback=True)
    else:
        st.warning(f"No movies found for {selected_year} with selected genres.")

def render_analytics_tab():
    """Render the analytics tab"""
    movies_df, _, _ = st.session_state.cached_data
    st.subheader("📊 Movie Analytics Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["Genre Analysis", "Rating Insights", "Word Cloud"])
    
    with tab1:
        st.subheader("🎭 Genre Distribution")
        genre_count = defaultdict(int)
        for g_list in movies_df['genres']:
            if isinstance(g_list, str):
                for genre in g_list.split(', '):
                    clean_genre = genre.strip()
                    if clean_genre:
                        genre_count[clean_genre] += 1
        
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

def render_actor_director_tab():
    """Render the actor/director tab"""
    movies_df, _, _ = st.session_state.cached_data
    st.subheader("🎭 Find Movies by Actor or Director")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_name = st.text_input("Enter actor or director name", key="actor_director_search")
    with col2:
        num_results = st.slider("Number of results", 5, 50, 10, key="actor_num_slider")
    
    if search_name:
        with st.spinner(f"Searching for movies with {search_name}..."):
            try:
                # Search for actor in cast or director
                results = movies_df[
                    (movies_df['director'].str.contains(search_name, case=False)) |
                    (movies_df['actors'].apply(lambda x: any(search_name.lower() in actor.lower() for actor in x) if isinstance(x, list) else False))
                ]
                
                if not results.empty:
                    st.success(f"🎬 Found {len(results)} movies featuring {search_name}")
                    
                    # Sort by popularity
                    results = results.sort_values('popularity', ascending=False)
                    
                    # Pagination
                    num_per_page = min(num_results, 10)
                    page = st.number_input("Page", min_value=1, max_value=len(results)//num_per_page+1, value=1, key="actor_page")
                    start = (page-1) * num_per_page
                    end = start + num_per_page
                    
                    # Display results
                    for _, row in results.iloc[start:end].iterrows():
                        movie_card(row, context="actor", show_feedback=True)
                else:
                    st.warning(f"No movies found with {search_name}")
            except Exception as e:
                st.error(f"Error searching for actor/director: {str(e)}")

def render_hybrid_tab():
    """Render the hybrid recommendations tab"""
    st.subheader("💡 Hybrid Recommendations")
    st.info("Combines content-based filtering with collaborative filtering for personalized results")
    
    movies_df, _, precomputed = st.session_state.cached_data
    
    # Movie type selection
    available_genres = precomputed['genre_set']
    valid_defaults = ["Action", "Comedy"]
    
    selected_types = st.multiselect(
        "Filter by movie types", 
        available_genres, 
        default=valid_defaults, 
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
                
                # Show recommendations
                for _, row in results.iterrows():
                    movie_card(row, context="hybrid")
            else:
                st.warning("⚠️ No recommendations found matching your criteria")

def render_dl_tab():
    """Render the deep learning recommendations tab"""
    st.subheader("🤖 Deep Learning Recommendations")
    st.info("Personalized recommendations based on your taste profile")
    
    movies_df, _, _ = st.session_state.cached_data
    
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
            
            # Get all movie IDs
            all_movie_ids = movies_df['id'].tolist()
            
            # Predict ratings
            predictions = []
            for idx, movie_id in enumerate(all_movie_ids):
                pred = dl_model.predict(user_id, movie_id)
                predictions.append((movie_id, pred.est))
            
            # Sort predictions
            predictions.sort(key=lambda x: x[1], reverse=True)
            top_movie_ids = [mid for mid, _ in predictions[:10]]
            recs_df = movies_df[movies_df['id'].isin(top_movie_ids)]
            
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

def render_profile_tab():
    """Render the user profile tab"""
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

def main_app():
    """Main application logic after login"""
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
    
    with tabs[0]:
        render_home_tab()
    with tabs[1]:
        render_search_tab()
    with tabs[2]:
        render_popular_tab()
    with tabs[3]:
        render_genre_tab()
    with tabs[4]:
        render_latest_tab()
    with tabs[5]:
        render_analytics_tab()
    with tabs[6]:
        render_actor_director_tab()
    with tabs[7]:
        render_hybrid_tab()
    with tabs[8]:
        render_dl_tab()
    with tabs[9]:
        render_profile_tab()

def main():
    """Main application entry point"""
    # Configure page
    configure_page()
    
    # Initialize session state
    initialize_session_state()
    
    # Load deep learning model
    global dl_model
    dl_model = None
    
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
            dl_model = train_dl_model()
            
            # Render main application
            main_app()
        except Exception as e:
            st.error(f"Application error: {str(e)}")

# =========================================
# APPLICATION ENTRY POINT
# =========================================
if __name__ == "__main__":
    main()
