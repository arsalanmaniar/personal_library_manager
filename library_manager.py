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
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem; !important;
        color: #000000; !important;
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
    """,unsafe_allow_html=True,)

def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None
    
if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'book added' not in st.session_state:
    st.session_state.book_added = False
if 'book remove' not in st.session_state:
    st.session_state.book_removed = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"


def load_library():
    try:
        if os.path.exists("library.json"):
            with open("library.json", "r") as file:
                st.session_state.library = json.load(file)
                return True
            return False
    except Exception as e:
        st.error(f"Error loading library: {e}")
        return False

# Save library
def save_library():
    try:
        with open("library.json", "w") as file:
            json.dump(st.session_state.library, file)
        return True
    except Exception as e:
        st.error(f"Error loading library: {e}")
        return False

# Add book to library
def add_book(title, author, publication_year,genre, read_status):
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
    time.sleep(0.5) # Animation time

# Remove book from library
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
    results = []

    for book in st.session_state.library:
        if search_by == "Title" and search_term in book["title"].lower():
            results.append(book)
        elif search_by == "Author" and search_term in book["author"].lower():
            results.append(book)
        elif search_by == "Genre" and search_term in book["genre"].lower():
            results.append(book)
    st.session_state.search_results = results

# Calculate reading stats
def get_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book["read_status"])
    percentage_read = (read_books / total_books) * 100 if total_books > 0 else 0

    genres = {}
    authors = {}
    decades = {}
    
    for book in st.session_state.library:
        if book["genre"] in genres:
            genres[book["genre"]] += 1
        else:
            genres[book["genre"]] = 1

        # Count authors
        if book["author"] in authors:
            authors[book["author"]] += 1
        else:
            authors[book["author"]] = 1

        # Count decades
        decade = (book["publication_year"] // 10) * 10
        if decade in decades:
            decades[decade] += 1
        else:
            decades[decade] = 1

 #sort by count
        genres = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))
        authors = dict(sorted(authors.items(), key=lambda x: x[1], reverse=True))
        decades = dict(sorted(decades.items(), key=lambda x: x[0],))

        return{
                "total_books": total_books,
                "read_books": read_books,
                "percentage_read": percentage_read,
                "genres": genres,
                "authors": authors,
                "decades": decades,
        }
    
def create_visualizations(stats):
    if stats["total_books"] > 0:
        fig_read_status = go.Figure(data=[go.pie(
            labels=["Read", "Unread"],
            values=[stats["read_books"], stats["total_books"] - stats["read_books"]],
            hole=.4,
            marker_colors=["#28a745", "#dc3545"],
        )])
        fig_read_status.update_layout(
            title_text="Read vs Unread Books",
            showlegend=True,
            highlight=400,
        )
        st.plotly_chart(fig_read_status , use_container_width=True)

        if stats['genres']:
            genres_df = pd.DataFrame({
                'Genre': list(stats['genres'].keys()),
                'Count': list(stats['genres'].values()),
            })
            fig_genres = px.bar(
                genres_df,
                x='Genre',
                y='Count',
                color = 'count',
                color_continuous_scale=px.colors.sequential.Viridis,

            )
            fig_genres.update_layout(
                title_text="Books by publication decade",
                xaxis_title="Genres",
                yaxis_title="Number of books",
                hight=400,
            )
            st.plotly_chart(fig_genres, use_container_width=True)
if stats['decades']:
    decades_df = pd.DataFrame({
        'Decade': [f"{decade}s" for decade in stats['decades'].keys()],
        'Count': list(stats['decades'].values()),
    })
    fig_decades = px.line(
        decades_df,
        x='Decade',
        y='Count',
        markers=True,
        line_shape='spline',

    )
    fig_decades.update_layout(
        title_text="Books by publication decade",
        xaxis_title="Decade",
        yaxis_title="Number of books",
        hight=400,
    )
    st.plotly_chart(fig_decades, use_container_width=True)

    # load library
load_library()
st.sidebar.markdown("<h1 style='text-align: center;'> Navigation</h1>", unsafe_allow_html=True)
lottie_book = load_lottie_url("https://assets6.lottiefiles.com/packages/lf20_7zjzjz.json")
if lottie_book:
    st_lottie(lottie_book, height=200, key="book_animation")

nav_option = st.sidebar.radio(
    "choose an option",
    ["View Library", "Add Book", "Search Book", "Library Statistics"],)

if nav_option == "View Library":
    st.session_state.current_view = "library"
elif nav_option == "Add Book":
    st.session_state.current_view = "add_book"
elif nav_option == "Search Book":
    st.session_state.current_view = "search_book"
elif nav_option == "Library Statistics":
    st.session_state.current_view = "stats"


st.markdown("<h1 class='main-header'>Library Manager</h1>", unsafe_allow_html=True)
if st.session_state.current_view == "add":
    st.markdown("<h2 class='subheader'>Add a New Book</h2>", unsafe_allow_html=True)
    

    # adding book input form
    with st.form(key="add_book_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Book Title", max_chars=100)
            author = st.text_input("Author", max_chars=100)
            publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, value=datetime.now().year)
        with col2:
            genre = st.selectbox("Genre"[
                "Friction", "Non Friction", "Science", "Technology", "Fantasy" "Romance", "Poetry", "Self-help","Art", "Religion", "History", "Other"
            ])
            read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True)
            read_bool = read_status == "Read"
        submit_button = st.form_submit_button(label="Add Book")

        if submit_button and title and author:
            add_book(title,author,publication_year,genre,read_bool)

    if st.session_state.book_added:
        st.markdown("<div class='success-message'> Book added successfully!</div>", unsafe_allow_html=True)
        st.balloons()
        st.session_state.book_added = False
elif st.session_state.current_view == "library":
    st.markdown("<h2 class = 'sub-header'> Your Library</h2>", unsafe_allow_html=True)

    if not st.session_state.library:
        st.markdown("div class= 'Warning-message'> Your library is empty. Add some books to get started!</div>", unsafe_allow_html=True)
    else:
        cols = st.columns(2)
        for i , book in enumerate(st.session_state.library):
            with cols[i % 2]:
                st.markdown(f"""<div class = 'book-card'>
                            <h3>{book['title']}</h3>
                            <p><strong>Author:</strong> {book['author']}</p>
                            <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                            <p><strong>Genre:</strong> {book['genre']}</p>
                            <p><span class='{"read-badge" if book ["read_status"] else "unread-badge"}'>{
                                "Read" if book["read_status"] else "Unread"
                            }</span></p>
                            </div>
""",unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Remove", key=f"remove_{i}", use_container_width=True):
                        if remove_book(i):
                            st.rerun()
                    with col2:
                        new_status = not book['read_status']
                        status_label = "Mark as read" if not book['read_status'] else "Mark as Unread"
                        if st.button(status_label, key=f"status{i}", use_container_width=True):
                            st.session_state.library[i]['read_status'] = new_status
                            save_library()
                            st.rerun()
    if st.session_state.book_removed:
        st.markdown("<div class= 'success-message'> Book removed successfully!</div>", unsafe_allow_html=True)
        st.session_state.book_removed = False
elif st.session_state.current_view == "search":
    st.markdown("<h2 class 'sub-header'> search book</h2>", unsafe_allow_html=True) 

    search_by = st.selectbox("Search by:", ["Title", "Author", "Genre"])
    search_term = st.text_input("Enter search term:")

    if st.button("search", use_container_width=False):
        if search_term:
            with st.spinner("Searching..."):
                time.sleep(0.5)
                search_book(search_term, search_by)
    if hasattr(st.session_state,'search_results'):
        if st.session_state.search_results:
            st.markdown(f"<h3> Found {len(st.session_state.search_results)}results:</h3>", unsafe_allow_html=True)
            
            for i, book in enumerate(st.session_state.search_results):
                st.markdown(f"""
                           <div class = 'book-card'>
                            <h3>{book['title']}</h3>
                            <p><strong>Author:</strong> {book['author']}</p>
                            <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                            <p><strong>Genre:</strong> {book['genre']}</p>
                            <p><span class='{"read-badge" if book ["read_status"] else "unread-badge"}'>{
                                "Read" if book["read_status"] else "Unread"
                            }</span></p>
                            </div>
""",unsafe_allow_html=True)
        elif search_term:
            st.markdown(f"<div class='warning-message'>No books found matching your search.</div>", unsafe_allow_html=True)

elif st.session_state.current_view == "stats":
    st.markdown("<h2 class='subheader'>Library Statistics</h2>", unsafe_allow_html=True)

    if not st.session_state.library:
        st.markdown("<div class='warning-message'>Your library is empty. Add some books to get started!</div>", unsafe_allow_html=True)
    else:
        stats = get_library_stats()
        col1,col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Books", stats['total_books'])
        with col2:
            st.metric("Book Read", stats['read_books'])
        with col3:
            st.metric("Percentage Read",f"{stats['percentage_read']:.1f}%")
        create_visualizations()


        if stats['author']:
            st.markdown("<h3> Top Author</h3>",unsafe_allow_html=True)
            top_authors = dict(list(stats['author'].item())[:5])
            for author, count in top_authors.items():
                st.markdown(f"**{author}**: {count} book {'s' if count > 1 else ''}")
st.markdown("---")
st.markdown("Copyright @ 2025 Arsalan Maniar Personal Library Manager", unsafe_allow_html=True)
