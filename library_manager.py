import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import random
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests
import statistics as stats 

# Set page configuration
st.set_page_config(
    page_title="Library Manager",
    page_icon="\ud83d\udcda",
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
    .read-badges {
        background-color: #d4edda;
        color: #155724;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .unread-badges {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .action-buttons {
        margin-right: 0.5rem;
    }
    .stButton>button {
        border-radius: 0.375rem;
    }
</style>
""", unsafe_allow_html=True)

# Load Lottie animation
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Session state variables
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

# Load library from file
def load_library():
    try:
        if os.path.exists("library.json"):
            with open("library.json", "r") as file:
                st.session_state.library = json.load(file)
    except Exception as e:
        st.error(f"Error loading library: {e}")

# Save library to file
def save_library():
    try:
        with open("library.json", "w") as file:
            json.dump(st.session_state.library, file)
    except Exception as e:
        st.error(f"Error saving library: {e}")

# Add book
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
    time.sleep(0.5)

# Remove book
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True
        return True
    return False

# Search book
def search_book(search_term, search_by):
    search_term = search_term.lower()
    results = [book for book in st.session_state.library if search_term in book[search_by].lower()]
    st.session_state.search_results = results

# Load library
load_library()

# Sidebar Navigation
st.sidebar.markdown("<h1 style='text-align: center;'>Navigation</h1>", unsafe_allow_html=True)
lottie_book = load_lottie_url("https://assets6.lottiefiles.com/packages/lf20_7zjzjz.json")
if lottie_book:
    st_lottie(lottie_book, height=200, key="book_animation")

nav_option = st.sidebar.radio("Choose an option", ["View Library", "Add Book", "Search Book"])
st.session_state.current_view = nav_option.lower().replace(" ", "_")

# Page Content
st.markdown("<h1 class='main-header'>Library Manager</h1>", unsafe_allow_html=True)
if st.session_state.current_view == "add_book":
    st.markdown("<h2 class='subheader'>Add a New Book</h2>", unsafe_allow_html=True)
    with st.form(key="add_book_form"):
        title = st.text_input("Book Title")
        author = st.text_input("Author")
        publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, value=datetime.now().year)
        genre = st.text_input("Genre")
        read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True) == "Read"
        if st.form_submit_button("Add Book"):
            add_book(title, author, publication_year, genre, read_status)
            st.success("Book added successfully!")
            st.balloons()

# More sections can be added here...

st.markdown("---")
st.markdown("Copyright @ 2025 Arsalan Maniar Personal Library Manager", unsafe_allow_html=True)
