import streamlit as st
import os
import time
import numpy as np
import pandas as pd
import librosa
import librosa.display
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from PIL import Image
import io
import base64
from scipy.io import wavfile
import tempfile
import json
from pathlib import Path
import random
import matplotlib.cm as cm
from datetime import datetime
from streamlit_plotly_events import plotly_events
import plotly.express as px
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_card import card
from streamlit_option_menu import option_menu
import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from scipy import signal
import requests
from pydub import AudioSegment

# App configuration
st.set_page_config(
    page_title="NeoBeat - Advanced Music Player",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'current_track' not in st.session_state:
    st.session_state.current_track = None
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False
if 'volume' not in st.session_state:
    st.session_state.volume = 0.5
if 'playlist' not in st.session_state:
    st.session_state.playlist = []
if 'favorites' not in st.session_state:
    st.session_state.favorites = []
if 'play_history' not in st.session_state:
    st.session_state.play_history = []
if 'theme' not in st.session_state:
    st.session_state.theme = "dark"
if 'audio_features' not in st.session_state:
    st.session_state.audio_features = None
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
if 'equalizer_settings' not in st.session_state:
    st.session_state.equalizer_settings = {
        'bass': 0.5,
        'mid': 0.5,
        'treble': 0.5
    }
if 'custom_playlists' not in st.session_state:
    st.session_state.custom_playlists = {}

# Song metadata storage structure
if 'music_library' not in st.session_state:
    st.session_state.music_library = []

# User statistics
if 'user_stats' not in st.session_state:
    st.session_state.user_stats = {
        'most_played': {},
        'favorite_genres': {},
        'listening_time': 0,
    }

# Function to load custom CSS
def load_css():
    css = """
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #121212 0%, #1e1e1e 100%);
        color: #f0f0f0;
    }
    
    .glassmorphic {
        background: rgba(25, 25, 25, 0.7);
        border-radius: 16px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        margin: 10px 0;
    }
    
    .player-controls {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
    }
    
    .control-button {
        background: rgba(255, 255, 255, 0.1);
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: flex;
        justify-content: center;
        align-items: center;
        color: white;
        font-size: 18px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .control-button:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: scale(1.1);
        box-shadow: 0 0 15px rgba(138, 43, 226, 0.7);
    }
    
    .track-info {
        text-align: center;
        margin: 20px 0;
    }
    
    .track-title {
        font-size: 24px;
        font-weight: bold;
        color: #f0f0f0;
        margin-bottom: 5px;
    }
    
    .track-artist {
        font-size: 18px;
        color: #b8b8b8;
    }
    
    .album-art {
        width: 300px;
        height: 300px;
        border-radius: 8px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin: 0 auto;
        display: block;
        transition: transform 0.5s ease;
    }
    
    .album-art:hover {
        transform: scale(1.05);
    }
    
    .neon-text {
        color: #fff;
        text-shadow: 0 0 5px #ff00de, 0 0 10px #ff00de, 0 0 20px #ff00de;
    }
    
    .neon-border {
        border: 2px solid rgba(138, 43, 226, 0.7);
        box-shadow: 0 0 15px rgba(138, 43, 226, 0.7);
    }
    
    /* Custom progress bar styling */
    .stProgress > div > div > div {
        background-color: #b64fc8;
    }
    
    /* Slider styling */
    .stSlider > div > div > div {
        background-color: #b64fc8 !important;
    }
    
    .stSlider > div > div > div > div {
        background-color: #ff00de !important;
    }
    
    /* Animated background */
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    
    .animated-bg {
        background: linear-gradient(-45deg, #121212, #1e1e1e, #2d1f3d, #1a1a2e);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: rgba(18, 18, 18, 0.9);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Button styling */
    .stButton button {
        border-radius: 20px;
        padding: 10px 24px;
        background: rgba(138, 43, 226, 0.7);
        color: white;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background: rgba(138, 43, 226, 1);
        box-shadow: 0 0 15px rgba(138, 43, 226, 0.7);
        transform: translateY(-2px);
    }
    
    /* Song list styling */
    .song-item {
        display: flex;
        align-items: center;
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        background: rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
    }
    
    .song-item:hover {
        background: rgba(255, 255, 255, 0.1);
        transform: translateX(5px);
    }
    
    /* Lyrics container */
    .lyrics-container {
        height: 300px;
        overflow-y: auto;
        padding: 15px;
        background: rgba(10, 10, 10, 0.7);
        border-radius: 8px;
        margin-top: 20px;
    }
    
    /* Equalizer styling */
    .equalizer-container {
        display: flex;
        justify-content: space-around;
        margin-top: 20px;
    }
    
    .eq-slider {
        width: 30%;
        text-align: center;
    }
    
    /* Custom tab styling */
    .custom-tab {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        margin-right: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .custom-tab.active {
        background: rgba(138, 43, 226, 0.7);
    }
    
    .custom-tab:hover {
        background: rgba(138, 43, 226, 0.5);
    }
    
    /* Playlist styling */
    .playlist-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px;
        background: rgba(138, 43, 226, 0.3);
        border-radius: 8px;
        margin-bottom: 10px;
    }
    
    /* Search bar styling */
    .search-container {
        margin: 20px 0;
    }
    
    .search-container input {
        width: 100%;
        padding: 10px 15px;
        border-radius: 20px;
        border: none;
        background: rgba(255, 255, 255, 0.1);
        color: white;
    }
    
    .search-container input:focus {
        outline: none;
        box-shadow: 0 0 10px rgba(138, 43, 226, 0.7);
    }
    
    /* Animations */
    @keyframes pulse {
        0% {transform: scale(1);}
        50% {transform: scale(1.05);}
        100% {transform: scale(1);}
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes fadeIn {
        from {opacity: 0;}
        to {opacity: 1;}
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    
    /* Progress bar animation */
    @keyframes progress {
        from {width: 0%;}
        to {width: 100%;}
    }
    
    .progress-animation {
        animation: progress 30s linear;
    }
    
    /* Stats card styling */
    .stats-card {
        background: rgba(30, 30, 30, 0.7);
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Light theme overrides */
    .light-theme {
        background: linear-gradient(135deg, #f0f0f0 0%, #e0e0e0 100%);
        color: #121212;
    }
    
    .light-theme .glassmorphic {
        background: rgba(255, 255, 255, 0.7);
        border: 1px solid rgba(0, 0, 0, 0.1);
    }
    
    .light-theme .track-title {
        color: #121212;
    }
    
    .light-theme .track-artist {
        color: #555555;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Load CSS
load_css()

# Utility functions
def extract_metadata(audio_file):
    """Extract metadata from uploaded audio file"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    temp_file.write(audio_file.getvalue())
    temp_file.close()
    
    try:
        audio = MP3(temp_file.name, ID3=ID3)
        
        # Default values
        metadata = {
            'title': 'Unknown Title',
            'artist': 'Unknown Artist',
            'album': 'Unknown Album',
            'genre': 'Unknown Genre',
            'duration': audio.info.length,
            'year': 'Unknown Year',
            'art': None
        }
        
        if audio.tags:
            # Extract title
            if 'TIT2' in audio.tags:
                metadata['title'] = str(audio.tags['TIT2'])
            
            # Extract artist
            if 'TPE1' in audio.tags:
                metadata['artist'] = str(audio.tags['TPE1'])
                
            # Extract album
            if 'TALB' in audio.tags:
                metadata['album'] = str(audio.tags['TALB'])
                
            # Extract genre
            if 'TCON' in audio.tags:
                metadata['genre'] = str(audio.tags['TCON'])
                
            # Extract year
            if 'TDRC' in audio.tags:
                metadata['year'] = str(audio.tags['TDRC'])
                
            # Extract album art
            if 'APIC:' in audio.tags:
                apic = audio.tags['APIC:']
                img = Image.open(io.BytesIO(apic.data))
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG")
                metadata['art'] = base64.b64encode(buffered.getvalue()).decode("utf-8")
    except Exception as e:
        st.error(f"Error extracting metadata: {e}")
    
    os.unlink(temp_file.name)
    return metadata

def get_dummy_library():
    """Generate dummy music library data for demo purposes"""
    return [
        {
            'id': 1,
            'title': 'Synthwave Dreams',
            'artist': 'Neon Eclipse',
            'album': 'Digital Horizon',
            'genre': 'Electronic',
            'duration': 242,
            'year': '2023',
            'art': 'https://ranbond-pharmaceuticals.s3.us-east-1.amazonaws.com/Synthwave+Dreams.webp',
            'path': 'dummy_path_1'
        },
        {
            'id': 2,
            'title': 'Midnight Drive',
            'artist': 'Cyber Pulse',
            'album': 'Neon Highways',
            'genre': 'Synthwave',
            'duration': 195,
            'year': '2023',
            'art': 'https://ranbond-pharmaceuticals.s3.us-east-1.amazonaws.com/Midnight+Drive.webp',
            'path': 'dummy_path_2'
        },
        {
            'id': 3,
            'title': 'Tokyo Lights',
            'artist': 'Digital Dreams',
            'album': 'Urban Glow',
            'genre': 'Chillwave',
            'duration': 278,
            'year': '2022',
            'art': 'https://ranbond-pharmaceuticals.s3.us-east-1.amazonaws.com/Tokyo+Lights.webp',
            'path': 'dummy_path_3'
        },
        {
            'id': 4,
            'title': 'Pixel Forest',
            'artist': 'Quantum Beats',
            'album': 'Virtual Reality',
            'genre': 'Electronic',
            'duration': 224,
            'year': '2023',
            'art': 'https://ranbond-pharmaceuticals.s3.us-east-1.amazonaws.com/Pixel+Forest.webp',
            'path': 'dummy_path_4'
        },
        {
            'id': 5,
            'title': 'Cyber Soul',
            'artist': 'Neon Eclipse',
            'album': 'Digital Horizon',
            'genre': 'Electronic',
            'duration': 253,
            'year': '2023',
            'art': 'https://ranbond-pharmaceuticals.s3.us-east-1.amazonaws.com/Cyber+Soul.webp',
            'path': 'dummy_path_5'
        }
    ]

def format_time(seconds):
    """Format seconds into MM:SS"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def get_mock_lyrics(track_name):
    """Get mock lyrics for demo purposes"""
    # This is a placeholder, in a real app you'd fetch real lyrics from an API
    dummy_lyrics = {
        'Synthwave Dreams': """
        [Verse 1]
        Neon lights in the digital sky
        Virtual worlds where dreams don't die
        Pixels forming a new reality
        A synthwave journey through infinity

        [Chorus]
        Synthwave dreams taking me higher
        Electric pulses, my heart's on fire
        Digital horizons stretching far
        In this cyber world, I am the star
        """,
        
        'Midnight Drive': """
        [Verse 1]
        Empty streets at 2 A.M.
        City lights like precious gems
        The engine purrs, the night is young
        This midnight story has just begun

        [Chorus]
        Midnight drive, just you and I
        Neon highways touch the sky
        The world asleep, but we're alive
        On this endless midnight drive
        """,
        
        'Tokyo Lights': """
        [Verse 1]
        Shinjuku crossing, people flow
        Neon signs put on a show
        Tokyo nights, a digital dream
        Life is more than what it seems

        [Chorus]
        Tokyo lights guide my way
        Through the night into the day
        Urban glow, electric soul
        In this city, I feel whole
        """,
        
        'Pixel Forest': """
        [Verse 1]
        Venture deep into the code
        Digital trees line the road
        Bits and bytes form a new world
        A pixel forest has unfurled

        [Chorus]
        Pixel forest, virtual trees
        A digital breeze, I feel so free
        Colors bright, beyond compare
        In this world, I have no care
        """,
        
        'Cyber Soul': """
        [Verse 1]
        Human heart in a digital chest
        Binary code put to the test
        Emotions flow through circuits clean
        A new kind of life, never before seen

        [Chorus]
        Cyber soul, a new frontier
        The line between is no longer clear
        Machine and man become as one
        A digital life has just begun
        """
    }
    
    return dummy_lyrics.get(track_name, "No lyrics available for this track.")

def generate_waveform(duration=30):
    """Generate a fake waveform for visualization purposes"""
    # In a real app, this would be generated from actual audio data
    x = np.linspace(0, duration, int(duration * 50))
    waveform = np.sin(2 * np.pi * 1 * x) * 0.3 + np.sin(2 * np.pi * 2 * x) * 0.2 + np.random.normal(0, 0.1, len(x))
    return x, waveform

def create_visualizer():
    """Create an audio visualizer visualization"""
    # This is a simulation - in a real app, this would use real-time audio data
    frequencies = np.arange(20)
    amplitudes = np.random.uniform(0.1, 1, 20)
    
    # Simulate the effect of equalizer settings
    amplitudes[:6] *= st.session_state.equalizer_settings['bass'] * 2
    amplitudes[6:14] *= st.session_state.equalizer_settings['mid'] * 2
    amplitudes[14:] *= st.session_state.equalizer_settings['treble'] * 2
    
    # Add some randomness for animation effect
    amplitudes *= np.random.uniform(0.7, 1.3, 20)
    
    fig = go.Figure(data=[
        go.Bar(
            x=frequencies,
            y=amplitudes,
            marker_color=[f'rgba({int(138 + i*5)}, {int(43 + i*10)}, {int(226 - i*5)}, 0.8)' for i in range(20)],
            width=0.8
        )
    ])
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=200,
        xaxis=dict(
            showgrid=False,
            showticklabels=False
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            range=[0, 2]
        )
    )
    
    return fig

def generate_recommendation(track_info):
    """Generate AI-powered song recommendations based on current track"""
    library = get_dummy_library()
    
    # Filter out the current track
    filtered_library = [track for track in library if track['title'] != track_info['title']]
    
    # In a real app, this would use ML algorithms
    # For demo, we'll use simple genre matching
    genre_matches = [track for track in filtered_library if track['genre'] == track_info['genre']]
    artist_matches = [track for track in filtered_library if track['artist'] == track_info['artist']]
    
    recommendations = []
    
    # Prioritize same artist
    if artist_matches:
        recommendations.extend(artist_matches)
    
    # Add genre matches
    if genre_matches:
        for track in genre_matches:
            if track not in recommendations:
                recommendations.append(track)
    
    # If still not enough, add random tracks
    while len(recommendations) < 3 and filtered_library:
        random_track = random.choice(filtered_library)
        if random_track not in recommendations:
            recommendations.append(random_track)
    
    return recommendations[:3]  # Return top 3 recommendations

def update_user_stats(track_info):
    """Update user listening statistics"""
    # Update most played songs
    title = track_info['title']
    if title in st.session_state.user_stats['most_played']:
        st.session_state.user_stats['most_played'][title] += 1
    else:
        st.session_state.user_stats['most_played'][title] = 1
    
    # Update genre stats
    genre = track_info['genre']
    if genre in st.session_state.user_stats['favorite_genres']:
        st.session_state.user_stats['favorite_genres'][genre] += 1
    else:
        st.session_state.user_stats['favorite_genres'][genre] = 1
    
    # Update listening time - in a real app, this would be more accurate
    st.session_state.user_stats['listening_time'] += track_info['duration']

def handle_play_button(track):
    """Handle play button click"""
    st.session_state.current_track = track
    st.session_state.is_playing = True
    st.session_state.start_time = time.time()
    
    # Update play history and stats
    if track not in st.session_state.play_history:
        st.session_state.play_history.append(track)
    update_user_stats(track)

def toggle_play_pause():
    """Toggle play/pause state"""
    st.session_state.is_playing = not st.session_state.is_playing

def handle_next_track():
    """Play next track in playlist"""
    if not st.session_state.playlist:
        return
    
    current_index = -1
    for i, track in enumerate(st.session_state.playlist):
        if track['id'] == st.session_state.current_track['id']:
            current_index = i
            break
    
    if current_index != -1 and current_index < len(st.session_state.playlist) - 1:
        handle_play_button(st.session_state.playlist[current_index + 1])

def handle_prev_track():
    """Play previous track in playlist"""
    if not st.session_state.playlist:
        return
    
    current_index = -1
    for i, track in enumerate(st.session_state.playlist):
        if track['id'] == st.session_state.current_track['id']:
            current_index = i
            break
    
    if current_index > 0:
        handle_play_button(st.session_state.playlist[current_index - 1])

def toggle_favorite(track):
    """Toggle favorite status of a track"""
    # Check if track is already in favorites
    track_ids = [t['id'] for t in st.session_state.favorites]
    
    if track['id'] in track_ids:
        # Remove from favorites
        st.session_state.favorites = [t for t in st.session_state.favorites if t['id'] != track['id']]
    else:
        # Add to favorites
        st.session_state.favorites.append(track)

def create_new_playlist(name):
    """Create a new custom playlist"""
    if name and name not in st.session_state.custom_playlists:
        st.session_state.custom_playlists[name] = []
        return True
    return False

def add_to_playlist(track, playlist_name):
    """Add a track to a custom playlist"""
    if playlist_name in st.session_state.custom_playlists:
        # Check if track is already in playlist
        track_ids = [t['id'] for t in st.session_state.custom_playlists[playlist_name]]
        
        if track['id'] not in track_ids:
            st.session_state.custom_playlists[playlist_name].append(track)
            return True
    return False

def remove_from_playlist(track_id, playlist_name):
    """Remove a track from a custom playlist"""
    if playlist_name in st.session_state.custom_playlists:
        st.session_state.custom_playlists[playlist_name] = [
            t for t in st.session_state.custom_playlists[playlist_name] if t['id'] != track_id
        ]

# Main UI functions
def render_sidebar():
    """Render the sidebar with navigation options"""
    st.sidebar.markdown(
        """
        <div class="glassmorphic">
            <h1 class="neon-text">NeoBeat</h1>
            <p>Advanced Music Player</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Navigation menu
    selected = option_menu(
        menu_title=None,
        options=["Library", "Playlists", "Favorites", "Stats", "Settings"],
        icons=["music-note-list", "collection-play", "heart", "graph-up", "gear"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical",
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#b64fc8", "font-size": "20px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "0px",
                "padding": "10px",
                "--hover-color": "rgba(138, 43, 226, 0.3)",
            },
            "nav-link-selected": {"background-color": "rgba(138, 43, 226, 0.7)"},
        }
    )
    
    # Mini player in sidebar (always visible)
    if st.session_state.current_track:
        st.sidebar.markdown("<div class='glassmorphic'>", unsafe_allow_html=True)
        
        # Display album art
        art_url = st.session_state.current_track.get('art', 'https://via.placeholder.com/100/8A2BE2/FFFFFF?text=No+Image')
        st.sidebar.markdown(
            f"""
            <div style="text-align: center;">
                <img src="{art_url}" width="100" height="100" style="border-radius: 8px;">
                <p><strong>{st.session_state.current_track['title']}</strong></p>
                <p>{st.session_state.current_track['artist']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Mini controls
        col1, col2, col3 = st.sidebar.columns(3)
        with col1:
            if st.button("⏮", key="mini_prev"):
                handle_prev_track()
        with col2:
            play_icon = "⏸" if st.session_state.is_playing else "▶️"
            if st.button(play_icon, key="mini_play"):
                toggle_play_pause()
        with col3:
            if st.button("⏭", key="mini_next"):
                handle_next_track()
                
        st.sidebar.markdown("</div>", unsafe_allow_html=True)
    
    # Upload section
    st.sidebar.markdown("<div class='glassmorphic'>", unsafe_allow_html=True)
    st.sidebar.markdown("## Upload Music")
    
    uploaded_file = st.sidebar.file_uploader("Drag & drop MP3 files", type=["mp3"], label_visibility="collapsed")
    if uploaded_file is not None:
        try:
            # Extract metadata
            metadata = extract_metadata(uploaded_file)
            
            # Create a new track entry
            new_track = {
                'id': len(st.session_state.music_library) + 1,
                'title': metadata['title'],
                'artist': metadata['artist'],
                'album': metadata['album'],
                'genre': metadata['genre'],
                'duration': metadata['duration'],
                'year': metadata['year'],
                'art': metadata.get('art', 'https://via.placeholder.com/300/8A2BE2/FFFFFF?text=No+Image'),
                'path': uploaded_file.name,
                'file': uploaded_file
            }
            
            # Add to library
            st.session_state.music_library.append(new_track)
            
            # Add to main playlist
            if new_track not in st.session_state.playlist:
                st.session_state.playlist.append(new_track)
                
            st.sidebar.success(f"Added {metadata['title']} to your library!")
            
        except Exception as e:
            st.sidebar.error(f"Error processing upload: {e}")
    
    st.sidebar.markdown("</div>", unsafe_allow_html=True)
    
    return selected

def render_library():
    """Render the music library view"""
    st.markdown(
        """
        <div class="glassmorphic">
            <h2>Music Library</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Initialize the library with dummy data if empty
    if not st.session_state.music_library and not st.session_state.playlist:
        st.session_state.music_library = get_dummy_library()
        st.session_state.playlist = get_dummy_library()
    
    # Search functionality
    st.markdown("<div class='glassmorphic search-container'>", unsafe_allow_html=True)
    search_query = st.text_input("Search for songs, artists, or albums", key="library_search")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Filter library based on search
    filtered_library = st.session_state.music_library
    if search_query:
        filtered_library = [
            track for track in st.session_state.music_library
            if search_query.lower() in track['title'].lower() or
               search_query.lower() in track['artist'].lower() or
               search_query.lower() in track['album'].lower()
        ]
    
    # Display library as a grid of cards
    st.markdown("<div class='glassmorphic'>", unsafe_allow_html=True)
    
    if not filtered_library:
        st.info("No songs found. Try a different search or upload some music!")
    else:
        # Display in a 3-column grid
        cols = st.columns(3)
        for i, track in enumerate(filtered_library):
            with cols[i % 3]:
                art_url = track.get('art', 'https://via.placeholder.com/150/8A2BE2/FFFFFF?text=No+Image')
                
                # Check if this is the currently playing track
                is_current = st.session_state.current_track and track['id'] == st.session_state.current_track['id']
                card_class = "neon-border" if is_current else ""
                
                # Check if track is in favorites
                is_favorite = track in st.session_state.favorites
                favorite_icon = "♥️" if is_favorite else "♡"
                
                st.markdown(
                    f"""
                    <div class="song-item {card_class}" style="margin-bottom: 20px;">
                        <img src="{art_url}" alt="Mountain" width="60" height="60" style="border-radius: 4px; margin-right: 10px;">
                        <div style="flex-grow: 1;">
                            <div><strong>{track['title']}</strong></div>
                            <div style="color: #b8b8b8;">{track['artist']}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button("▶️ Play", key=f"play_{track['id']}"):
                        handle_play_button(track)
                with col2:
                    if st.button(favorite_icon, key=f"fav_{track['id']}"):
                        toggle_favorite(track)
                with col3:
                    # Dropdown for playlists
                    playlist_options = list(st.session_state.custom_playlists.keys())
                    if playlist_options:
                        selected_playlist = st.selectbox(
                            "Add to Playlist",
                            options=["Add to..."] + playlist_options,
                            key=f"playlist_select_{track['id']}",
                            label_visibility="collapsed"
                        )
                        
                        if selected_playlist != "Add to...":
                            add_to_playlist(track, selected_playlist)
                            st.success(f"Added to {selected_playlist}")
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_playlists():
    """Render the playlists view"""
    st.markdown(
        """
        <div class="glassmorphic">
            <h2>Playlists</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Create new playlist section
    st.markdown("<div class='glassmorphic'>", unsafe_allow_html=True)
    st.subheader("Create New Playlist")
    
    new_playlist_name = st.text_input("Playlist Name", key="new_playlist_name")
    if st.button("Create Playlist"):
        if create_new_playlist(new_playlist_name):
            st.success(f"Created new playlist: {new_playlist_name}")
        else:
            st.error("Please enter a unique playlist name")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Display all playlists including the default "All Songs" playlist
    st.markdown("<div class='glassmorphic'>", unsafe_allow_html=True)
    st.subheader("Your Playlists")
    
    # Default playlist tab
    if st.button("All Songs", key="all_songs_playlist", use_container_width=True):
        st.session_state.selected_playlist = "All Songs"
    
    # Custom playlists tabs
    for playlist_name in st.session_state.custom_playlists.keys():
        if st.button(playlist_name, key=f"playlist_{playlist_name}", use_container_width=True):
            st.session_state.selected_playlist = playlist_name
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Display selected playlist content
    if 'selected_playlist' not in st.session_state:
        st.session_state.selected_playlist = "All Songs"
    
    st.markdown(
        f"""
        <div class='glassmorphic'>
            <div class='playlist-header'>
                <h3>{st.session_state.selected_playlist}</h3>
                <div>
                    {len(st.session_state.playlist if st.session_state.selected_playlist == "All Songs" else st.session_state.custom_playlists.get(st.session_state.selected_playlist, []))} songs
                </div>
            </div>
        """,
        unsafe_allow_html=True
    )
    
    # Display tracks in the selected playlist
    tracks_to_display = st.session_state.playlist if st.session_state.selected_playlist == "All Songs" else st.session_state.custom_playlists.get(st.session_state.selected_playlist, [])
    
    if not tracks_to_display:
        st.info(f"No songs in {st.session_state.selected_playlist} yet.")
    else:
        for track in tracks_to_display:
            art_url = track.get('art', 'https://via.placeholder.com/60/8A2BE2/FFFFFF?text=No+Image')
            is_current = st.session_state.current_track and track['id'] == st.session_state.current_track['id']
            row_class = "neon-border" if is_current else ""
            
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.markdown(
                    f"""
                    <div class="song-item {row_class}">
                        <img src="{art_url}" width="40" height="40" style="border-radius: 4px; margin-right: 10px;">
                        <div>
                            <div><strong>{track['title']}</strong></div>
                            <div style="color: #b8b8b8;">{track['artist']}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col2:
                st.text(format_time(track['duration']))
            
            with col3:
                if st.button("▶️", key=f"play_pl_{track['id']}"):
                    handle_play_button(track)
            
            with col4:
                if st.session_state.selected_playlist != "All Songs" and st.button("🗑️", key=f"remove_pl_{track['id']}"):
                    remove_from_playlist(track['id'], st.session_state.selected_playlist)
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_favorites():
    """Render the favorites view"""
    st.markdown(
        """
        <div class="glassmorphic">
            <h2>Favorites</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("<div class='glassmorphic'>", unsafe_allow_html=True)
    
    if not st.session_state.favorites:
        st.info("No favorite songs yet. Heart a song to add it to your favorites!")
    else:
        # Display favorites
        for track in st.session_state.favorites:
            art_url = track.get('art', 'https://via.placeholder.com/60/8A2BE2/FFFFFF?text=No+Image')
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(
                    f"""
                    <div class="song-item">
                        <img src="{art_url}" width="40" height="40" style="border-radius: 4px; margin-right: 10px;">
                        <div>
                            <div><strong>{track['title']}</strong></div>
                            <div style="color: #b8b8b8;">{track['artist']}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col2:
                if st.button("▶️", key=f"play_fav_{track['id']}"):
                    handle_play_button(track)
            
            with col3:
                if st.button("♥️", key=f"unfav_{track['id']}"):
                    toggle_favorite(track)
                    st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_stats():
    """Render user statistics view"""
    st.markdown(
        """
        <div class="glassmorphic">
            <h2>Your Listening Stats</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Calculate some stats
    total_songs = len(st.session_state.music_library)
    total_time = st.session_state.user_stats['listening_time']
    
    # Most played songs
    most_played = sorted(
        st.session_state.user_stats['most_played'].items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # Favorite genres
    genres = st.session_state.user_stats['favorite_genres']
    
    # Layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='glassmorphic stats-card'>", unsafe_allow_html=True)
        st.metric("Total Songs", total_songs)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='glassmorphic stats-card'>", unsafe_allow_html=True)
        st.subheader("Most Played Songs")
        if most_played:
            for title, count in most_played[:5]:
                st.markdown(f"**{title}** - Played {count} times")
        else:
            st.info("Start listening to see your stats!")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='glassmorphic stats-card'>", unsafe_allow_html=True)
        hours = int(total_time // 3600)
        minutes = int((total_time % 3600) // 60)
        st.metric("Listening Time", f"{hours} hrs {minutes} mins")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='glassmorphic stats-card'>", unsafe_allow_html=True)
        st.subheader("Favorite Genres")
        if genres:
            # Create a pie chart
            genre_df = pd.DataFrame({
                'Genre': list(genres.keys()),
                'Count': list(genres.values())
            })
            
            fig = px.pie(
                genre_df, 
                values='Count', 
                names='Genre',
                color_discrete_sequence=px.colors.sequential.Purp
            )
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=10, b=10),
                height=250
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Start listening to see your genre preferences!")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Listening history
    st.markdown("<div class='glassmorphic stats-card'>", unsafe_allow_html=True)
    st.subheader("Recently Played")
    
    if st.session_state.play_history:
        # Display in reverse order (most recent first)
        for track in reversed(st.session_state.play_history[-10:]):
            st.markdown(f"**{track['title']}** by {track['artist']}")
    else:
        st.info("No listening history yet.")
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_settings():
    """Render settings view"""
    st.markdown(
        """
        <div class="glassmorphic">
            <h2>Settings</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Theme settings
    st.markdown("<div class='glassmorphic'>", unsafe_allow_html=True)
    st.subheader("Theme")
    
    theme_options = ["Dark", "Light", "Synthwave", "Minimal"]
    theme = st.select_slider(
        "Select Theme",
        options=theme_options,
        value=theme_options[0]
    )
    
    # This would actually change the theme in a real app
    st.session_state.theme = theme.lower()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Equalizer settings
    st.markdown("<div class='glassmorphic'>", unsafe_allow_html=True)
    st.subheader("Equalizer")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.session_state.equalizer_settings['bass'] = st.slider(
            "Bass",
            0.0, 1.0, st.session_state.equalizer_settings['bass'],
            step=0.01
        )
    
    with col2:
        st.session_state.equalizer_settings['mid'] = st.slider(
            "Mid",
            0.0, 1.0, st.session_state.equalizer_settings['mid'],
            step=0.01
        )
    
    with col3:
        st.session_state.equalizer_settings['treble'] = st.slider(
            "Treble",
            0.0, 1.0, st.session_state.equalizer_settings['treble'],
            step=0.01
        )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Playback settings
    st.markdown("<div class='glassmorphic'>", unsafe_allow_html=True)
    st.subheader("Playback")
    
    st.checkbox("Crossfade between tracks", value=True)
    st.checkbox("Gapless playback", value=False)
    st.checkbox("Normalize volume", value=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # About section
    st.markdown("<div class='glassmorphic'>", unsafe_allow_html=True)
    st.subheader("About NeoBeat")
    
    st.markdown(
        """
        NeoBeat Music Player v1.0
        
        A cutting-edge music player built with Streamlit featuring a modern UI,
        audio visualization, and smart playlists.
        
        Created for demonstration purposes.
        """
    )
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_player():
    """Render the main music player component"""
    if not st.session_state.current_track:
        return
    
    st.markdown("<div class='glassmorphic'>", unsafe_allow_html=True)
    
    # Display album art and track info
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Album artwork
        art_url = st.session_state.current_track.get('art', 'https://via.placeholder.com/300/8A2BE2/FFFFFF?text=No+Image')
        st.markdown(
            f"""
            <div style="text-align: center;">
                <img src="{art_url}" class="album-art pulse">
                <div class="track-info">
                    <div class="track-title">{st.session_state.current_track['title']}</div>
                    <div class="track-artist">{st.session_state.current_track['artist']}</div>
                    <div>{st.session_state.current_track['album']} • {st.session_state.current_track['year']}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        # Audio visualizer
        st.markdown("<h3>Visualizer</h3>", unsafe_allow_html=True)
        
        # Create visualizer
        visualizer_fig = create_visualizer()
        st.plotly_chart(visualizer_fig, use_container_width=True)
        
        # Create waveform
        x, waveform = generate_waveform(st.session_state.current_track['duration'])
        
        # Calculate elapsed time for progress bar
        total_duration = st.session_state.current_track['duration']
        elapsed_time = min(
            time.time() - st.session_state.start_time if st.session_state.is_playing else 0,
            total_duration
        )
        
        # For demo purposes, we'll just simulate progress
        progress_percentage = min(elapsed_time / total_duration, 1.0) if st.session_state.is_playing else 0
        
        # Display track progress
        col_a, col_b, col_c = st.columns([1, 3, 1])
        with col_a:
            st.text(format_time(elapsed_time))
        with col_b:
            st.progress(progress_percentage)
        with col_c:
            st.text(format_time(total_duration))
    
    # Player controls
    st.markdown(
        """
        <div class="player-controls">
            <button class="control-button" id="shuffle">🔀</button>
            <button class="control-button" id="prev">⏮</button>
            <button class="control-button" id="play" style="width: 60px; height: 60px;">▶️</button>
            <button class="control-button" id="next">⏭</button>
            <button class="control-button" id="repeat">🔁</button>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Control buttons (functional versions)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("🔀 Shuffle", key="shuffle_btn"):
            # In a real app, this would shuffle the playlist
            pass
    
    with col2:
        if st.button("⏮ Previous", key="prev_btn"):
            handle_prev_track()
    
    with col3:
        play_text = "⏸ Pause" if st.session_state.is_playing else "▶️ Play"
        if st.button(play_text, key="play_btn"):
            toggle_play_pause()
    
    with col4:
        if st.button("⏭ Next", key="next_btn"):
            handle_next_track()
    
    with col5:
        if st.button("🔁 Repeat", key="repeat_btn"):
            # In a real app, this would toggle repeat mode
            pass
    
    # Volume control
    st.markdown("<div style='padding: 10px;'>", unsafe_allow_html=True)
    st.session_state.volume = st.slider(
        "Volume",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.volume,
        step=0.01,
        key="volume_slider"
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_details_and_lyrics():
    """Render additional details and lyrics for current track"""
    if not st.session_state.current_track:
        return
    
    st.markdown("<div class='glassmorphic'>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Lyrics", "Recommendations", "Details"])
    
    with tab1:
        lyrics = get_mock_lyrics(st.session_state.current_track['title'])
        st.markdown(
            f"""
            <div class="lyrics-container">
                <pre>{lyrics}</pre>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.checkbox("Karaoke Mode", value=False, help="Highlight lyrics in time with the music")
    
    with tab2:
        recommendations = generate_recommendation(st.session_state.current_track)
        
        if recommendations:
            st.subheader("You Might Also Like")
            
            cols = st.columns(len(recommendations))
            for i, track in enumerate(recommendations):
                with cols[i]:
                    art_url = track.get('art', 'https://via.placeholder.com/150/8A2BE2/FFFFFF?text=No+Image')
                    
                    st.markdown(
                        f"""
                        <div style="text-align: center;">
                            <img src="{art_url}" width="150" height="150" style="border-radius: 8px;">
                            <p><strong>{track['title']}</strong></p>
                            <p>{track['artist']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    if st.button("▶️ Play", key=f"play_rec_{track['id']}"):
                        handle_play_button(track)
        else:
            st.info("No recommendations available for this track.")
    
    with tab3:
        # Track details
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Track Details**")
            st.markdown(f"**Title:** {st.session_state.current_track['title']}")
            st.markdown(f"**Artist:** {st.session_state.current_track['artist']}")
            st.markdown(f"**Album:** {st.session_state.current_track['album']}")
            st.markdown(f"**Year:** {st.session_state.current_track['year']}")
            st.markdown(f"**Genre:** {st.session_state.current_track['genre']}")
            st.markdown(f"**Duration:** {format_time(st.session_state.current_track['duration'])}")
        
        with col2:
            # Audio features - in a real app, these would be actual audio features
            st.markdown("**Audio Features**")
            
            # Simulated audio features
            audio_features = {
                'Danceability': random.uniform(0.4, 0.9),
                'Energy': random.uniform(0.5, 0.95),
                'Valence': random.uniform(0.3, 0.8),
                'Acousticness': random.uniform(0.1, 0.7),
                'Instrumentalness': random.uniform(0.0, 0.8),
                'Tempo': random.randint(80, 160)
            }
            
            # Display as gauge chart
            feature_df = pd.DataFrame({
                'Feature': list(audio_features.keys())[:-1],  # Exclude tempo
                'Value': list(audio_features.values())[:-1]
            })
            
            fig = px.bar(
                feature_df,
                x='Feature',
                y='Value',
                color='Value',
                color_continuous_scale='Purp',
                range_y=[0, 1]
            )
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=10, b=10),
                height=250
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown(f"**Tempo:** {audio_features['Tempo']} BPM")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Main app
def main():
    # Render the sidebar
    selected_tab = render_sidebar()
    
    # Render the player if a track is selected (always visible at the top)
    render_player()
    
    # Render the selected view
    if selected_tab == "Library":
        render_library()
    elif selected_tab == "Playlists":
        render_playlists()
    elif selected_tab == "Favorites":
        render_favorites()
    elif selected_tab == "Stats":
        render_stats()
    elif selected_tab == "Settings":
        render_settings()
    
    # Render details and lyrics section if a track is selected
    if st.session_state.current_track:
        render_details_and_lyrics()
    
    # Auto-update every 1 second for live-like experience
    # This is a hack for Streamlit - in a real app, you would use proper
    # JavaScript for real-time updates
    if st.session_state.is_playing:
        time.sleep(1)
        st.rerun()

if __name__ == "__main__":
    main()