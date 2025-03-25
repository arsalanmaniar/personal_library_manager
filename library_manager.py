import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import requests
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie

# Set page configuration
st.set_page_config(
    page_title="Library Manager",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load Lottie animation
@st.cache_data
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Initialize session state variables
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
    if os.path.exists("library.json"):
        with open("library.json", "r") as file:
            st.session_state.library = json.load(file)

# Save library to file
def save_library():
    with open("library.json", "w") as file:
        json.dump(st.session_state.library, file)

# Add a book to the library
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
    time.sleep(0.5)  # Animation time

# Remove a book from the library
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True
        return True
    return False

# Search for a book
def search_book(search_term, search_by):
    search_term = search_term.lower()
    results = [book for book in st.session_state.library if search_term in book[search_by].lower()]
    st.session_state.search_results = results

# Load the library on startup
load_library()

# Sidebar Navigation
st.sidebar.header("Navigation")
lottie_book = load_lottie_url("https://assets6.lottiefiles.com/packages/lf20_7zjzjz.json")
if lottie_book:
    st_lottie(lottie_book, height=200, key="book_animation")

nav_option = st.sidebar.radio("Choose an option", ["View Library", "Add Book", "Search Book"])
if nav_option == "View Library":
    st.session_state.current_view = "library"
elif nav_option == "Add Book":
    st.session_state.current_view = "add_book"
elif nav_option == "Search Book":
    st.session_state.current_view = "search_book"

# Main Page Title
st.title("📚 Library Manager")

if st.session_state.current_view == "add_book":
    st.subheader("Add a New Book")
    with st.form(key="add_book_form"):
        title = st.text_input("Book Title")
        author = st.text_input("Author")
        publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, value=datetime.now().year)
        genre = st.text_input("Genre")
        read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True)
        submit_button = st.form_submit_button(label="Add Book")
        
        if submit_button and title and author:
            add_book(title, author, publication_year, genre, read_status == "Read")

    if st.session_state.book_added:
        st.success("Book added successfully!")
        st.session_state.book_added = False

elif st.session_state.current_view == "library":
    st.subheader("Your Library")
    if not st.session_state.library:
        st.warning("Your library is empty. Add some books to get started!")
    else:
        for i, book in enumerate(st.session_state.library):
            st.markdown(f"**{book['title']}** by {book['author']} ({book['publication_year']})")
            st.text(f"Genre: {book['genre']}, Status: {'Read' if book['read_status'] else 'Unread'}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Remove", key=f"remove_{i}"):
                    if remove_book(i):
                        st.rerun()
            with col2:
                new_status = not book['read_status']
                if st.button(f"Mark as {'Read' if new_status else 'Unread'}", key=f"status_{i}"):
                    st.session_state.library[i]['read_status'] = new_status
                    save_library()
                    st.rerun()

    if st.session_state.book_removed:
        st.success("Book removed successfully!")
        st.session_state.book_removed = False

elif st.session_state.current_view == "search_book":
    st.subheader("Search Book")
    search_by = st.selectbox("Search by:", ["title", "author", "genre"])
    search_term = st.text_input("Enter search term:")
    if st.button("Search"):
        search_book(search_term, search_by)
    
    if st.session_state.search_results:
        st.subheader(f"Found {len(st.session_state.search_results)} results:")
        for book in st.session_state.search_results:
            st.markdown(f"**{book['title']}** by {book['author']} ({book['publication_year']})")
            st.text(f"Genre: {book['genre']}, Status: {'Read' if book['read_status'] else 'Unread'}")
    elif search_term:
        st.warning("No books found matching your search.")

st.markdown("---")
st.markdown("© 2025 Arsalan Maniar - Personal Library Manager")
