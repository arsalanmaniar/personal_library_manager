import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# Set page configuration
st.set_page_config(
    page_title="Library Manager",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem !important;
        color: #000000 !important;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
        text-shadow: 2px 2px 2px #f5f5f5;
    }
    .subheader {
        font-size: 1.8rem !important;
        color: #000000 !important;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 1px solid #c3e6cb;
        border-radius: 0.375rem;
    }
    .warning-message {
        padding: 1rem;
        background-color: #fff3cd;
        border-left: 5px solid #ffeeba;
        border-radius: 0.375rem;
    }
    .book-card {
        background-color: #f5f5f5;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 5px solid #f5f5f5;
        transition: transform 0.3s ease;
    }
    .book-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Initialize session state
if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"

def load_library():
    if os.path.exists("library.json"):
        with open("library.json", "r") as file:
            st.session_state.library = json.load(file)

def save_library():
    with open("library.json", "w") as file:
        json.dump(st.session_state.library, file)

def add_book(title, author, publication_year, genre, read_status):
    book = {
        "title": title,
        "author": author,
        "publication_year": publication_year,
        "genre": genre,
        "read_status": read_status,
        "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True

def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True

def search_book(search_term, search_by):
    search_term = search_term.lower()
    results = [book for book in st.session_state.library if search_term in book[search_by.lower()].lower()]
    st.session_state.search_results = results

def get_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book["read_status"])
    percentage_read = (read_books / total_books) * 100 if total_books else 0
    return {"total_books": total_books, "read_books": read_books, "percentage_read": percentage_read}

def create_visualizations(stats):
    if stats["total_books"] > 0:
        fig_read_status = go.Figure(data=[go.Pie(
            labels=["Read", "Unread"],
            values=[stats["read_books"], stats["total_books"] - stats["read_books"]],
            hole=.4,
            marker_colors=["#28a745", "#dc3545"],
        )])
        st.plotly_chart(fig_read_status, use_container_width=True)

# Load the library
load_library()

st.sidebar.title("Navigation")
nav_option = st.sidebar.radio("Choose an option", ["View Library", "Add Book", "Search Book", "Library Statistics"])

if nav_option == "View Library":
    st.session_state.current_view = "library"
elif nav_option == "Add Book":
    st.session_state.current_view = "add_book"
elif nav_option == "Search Book":
    st.session_state.current_view = "search_book"
elif nav_option == "Library Statistics":
    st.session_state.current_view = "stats"

if st.session_state.current_view == "stats":
    stats = get_library_stats()
    st.metric("Total Books", stats['total_books'])
    st.metric("Books Read", stats['read_books'])
    st.metric("Percentage Read", f"{stats['percentage_read']:.1f}%")
    create_visualizations(stats)

st.markdown("---")
st.markdown("© 2025 Arsalan Maniar Personal Library Manager", unsafe_allow_html=True)
