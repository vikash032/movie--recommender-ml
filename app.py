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
                logging.error(f"Actor/director search error: {str(e)}")
                st.error(f"Error searching for actor/director: {str(e)}")

def render_hybrid_tab():
    """Render the hybrid recommendations tab"""
    st.subheader("💡 Hybrid Recommendations")
    st.info("Combines content-based filtering with collaborative filtering for personalized results")
    
    movies_df, _, precomputed = st.session_state.cached_data
    
    # Movie type selection
    available_genres = precomputed.get('genre_set', [])
    valid_defaults = ["Family", "History"] if available_genres else []
    
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
            if dl_model is not None:
                for idx, movie_id in enumerate(all_movie_ids):
                    pred = dl_model.predict(user_id, movie_id)
                    predictions.append((movie_id, pred.est))
            else:
                st.warning("Deep learning model not available. Using content-based recommendations.")
                predictions = [(mid, 0) for mid in all_movie_ids]
            
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
            logging.error(f"DL recommendation error: {str(e)}")
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
    
    # Debug panel in sidebar
    with st.sidebar:
        st.markdown("### 🐞 Debug Panel")
        st.session_state.show_debug = st.checkbox("Show User Preferences State", value=st.session_state.show_debug)
        if st.session_state.show_debug:
            st.write("Current Preferences:")
            st.json(st.session_state.user_preferences)
            st.write("User Vector:")
            st.write(st.session_state.user_vector)
    
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
