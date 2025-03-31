import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
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
        font-size: 3rem;
        color: #000000;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
        text-shadow: 2px 2px 2px #f5f5f5;
    }
            
    .subheader {
        font-size: 1.8rem;
        color: #000000;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
            
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 3px solid #c3e6cb;
        border-radius: 0.375rem;
    }
    .warning-message {
        padding: 1rem;
        background-color: #fff3cd;
        border-left: 3px solid #ffeeba;
        border-radius: 0.375rem;
    }
            
    .book-card {
        background-color: #f5f5f5;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 3px solid #d1d1d1;
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


# Set page configuration
st.set_page_config(
    page_title="Library Manager",
    page_icon="\U0001F4DA",
    layout="wide",
    initial_sidebar_state="expanded",
)

def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None
    
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
        st.error(f"Error saving library: {e}")
        return False

# Add book to library
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
        genres[book["genre"]] = genres.get(book["genre"], 0) + 1
        authors[book["author"]] = authors.get(book["author"], 0) + 1
        decade = (int(book["publication_year"]) // 10) * 10
        decades[decade] = decades.get(decade, 0) + 1


# Sort by count
genres = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))
authors = dict(sorted(authors.items(), key=lambda x: x[1], reverse=True))
decades = dict(sorted(decades.items(), key=lambda x: x[0]))
def get_data():
    return {"key": "value"  # ✅ Ye theek hai
    "total_books": total_books,
    "read_books": read_books,
    "percentage_read": percentage_read,
    "genres": genres,
    "authors": authors,
    "decades": decades,
}

def create_visualizations(stats):
    if stats["total_books"] > 0:
        fig_read_status = go.Figure(data=[go.Pie(
            labels=["Read", "Unread"],
            values=[stats["read_books"], stats["total_books"] - stats["read_books"]],
            hole=.4,
            marker_colors=["#28a745", "#dc3545"],
        )])
        fig_read_status.update_layout(
            title_text="Read vs Unread Books",
            showlegend=True,
        )
        st.plotly_chart(fig_read_status, use_container_width=True)

        if stats['genres']:
            genres_df = pd.DataFrame({
                'Genre': list(stats['genres'].keys()),
                'Count': list(stats['genres'].values()),
            })
            fig_genres = px.bar(
                genres_df,
                x='Genre',
                y='Count',
                color='Count',
                color_continuous_scale=px.colors.sequential.Viridis,
            )
            fig_genres.update_layout(
                title_text="Books by Genre",
                xaxis_title="Genres",
                yaxis_title="Number of books",
                height=400,
            )
            st.plotly_chart(fig_genres, use_container_width=True)

    if stats and isinstance(stats, dict) and 'decades' in stats:
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
            title_text="Books by Publication Decade",
            xaxis_title="Decade",
            yaxis_title="Number of books",
            height=400,
        )
        st.plotly_chart(fig_decades, use_container_width=True)

# Load library
load_library()
st.sidebar.markdown("<h1 style='text-align: center;'> Navigation</h1>", unsafe_allow_html=True)

lottie_book = load_lottie_url("https://assets6.lottiefiles.com/packages/lf20_7zjzjz.json")
if lottie_book:
    st_lottie(lottie_book, height=200, key="book_animation")

nav_option = st.sidebar.radio(
    "Choose an option",
    ["View Library", "Add Book", "Search Book", "Library Statistics"],
)

if nav_option == "View Library":
    st.session_state.current_view = "library"
elif nav_option == "Add Book":
    st.session_state.current_view = "add_book"
elif nav_option == "Search Book":
    st.session_state.current_view = "search_book"
elif nav_option == "Library Statistics":
    st.session_state.current_view = "stats"

st.markdown("<h1 class='main-header'>Library Manager</h1>", unsafe_allow_html=True)
if st.session_state.current_view == "add_book":
    st.markdown("<h2 class='subheader'>Add a New Book</h2>", unsafe_allow_html=True)

def add_book(title, author, publication_year, genre, read_bool):
    book = {
        "title": title,
        "author": author,
        "publication_year": publication_year,
        "genre": genre,
        "read_status": read_bool,
    }
    st.session_state.library.append(book)
    st.session_state.book_added = True

def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        st.session_state.book_removed = True
        return True
    return False

def save_library():
    pass

def search_book(term, by):
    st.session_state.search_results = [
        book for book in st.session_state.library if term.lower() in book[by.lower()].lower()
    ]

def get_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book['read_status'])
    percentage_read = (read_books / total_books * 100) if total_books else 0
    authors = {}
    for book in st.session_state.library:
        authors[book['author']] = authors.get(book['author'], 0) + 1
    return {"total_books": total_books, "read_books": read_books, "percentage_read": percentage_read, "author": authors}

if "library" not in st.session_state:
    st.session_state.library = []
    st.session_state.book_added = False
    st.session_state.book_removed = False
    st.session_state.current_view = "add_book"

st.title("Personal Library Manager")

if st.session_state.current_view == "add_book":
    with st.form(key="add_book_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Book Title", max_chars=100)
            author = st.text_input("Author", max_chars=100)
            publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, value=datetime.now().year)
        with col2:
            genre = st.selectbox("Genre", [
                "Fiction", "Non Fiction", "Science", "Technology", "Fantasy", "Romance", "Poetry", "Self-help", "Art", "Religion", "History", "Other"
            ])
            read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True)
            read_bool = read_status == "Read"
        submit_button = st.form_submit_button(label="Add Book")

        if submit_button and title and author:
            add_book(title, author, publication_year, genre, read_bool)
            st.success("Book added successfully!")
            st.balloons()
            st.session_state.book_added = False

elif st.session_state.current_view == "library":
    st.subheader("Your Library")
    if not st.session_state.library:
        st.warning("Your library is empty. Add some books to get started!")
    else:
        cols = st.columns(2)
        for i, book in enumerate(st.session_state.library):
            with cols[i % 2]:
                st.markdown(f"""
                **{book['title']}**  
                *Author:* {book['author']}  
                *Year:* {book['publication_year']}  
                *Genre:* {book['genre']}  
                **Status:** {'✅ Read' if book['read_status'] else '❌ Unread'}
                """)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Remove", key=f"remove_{i}"):
                        if remove_book(i):
                            st.rerun()
                with col2:
                    new_status = not book['read_status']
                    status_label = "Mark as Read" if not book['read_status'] else "Mark as Unread"
                    if st.button(status_label, key=f"status_{i}"):
                        st.session_state.library[i]['read_status'] = new_status
                        save_library()
                        st.rerun()

elif st.session_state.current_view == "search":
    st.subheader("Search Books")
    search_by = st.selectbox("Search by", ["Title", "Author", "Genre"])
    search_term = st.text_input("Enter search term")
    if st.button("Search"):
        if search_term:
            with st.spinner("Searching..."):
                time.sleep(0.5)
                search_book(search_term, search_by)
    
    if hasattr(st.session_state, "search_results"):
        if st.session_state.search_results:
            st.write(f"Found {len(st.session_state.search_results)} result(s):")
            for book in st.session_state.search_results:
                st.write(f"**{book['title']}** by {book['author']} ({book['publication_year']})")
        else:
            st.warning("No books found matching your search.")

elif st.session_state.current_view == "stats":
    st.subheader("Library Statistics")
    if not st.session_state.library:
        st.warning("Your library is empty. Add some books to get started!")
    else:
        stats = get_library_stats()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Books", stats['total_books'])
        col2.metric("Books Read", stats['read_books'])
        col3.metric("Percentage Read", f"{stats['percentage_read']:.1f}%")

        if stats['author']:
            st.subheader("Top Authors")
            top_authors = dict(list(stats['author'].items())[:5])
            for author, count in top_authors.items():
                st.write(f"**{author}**: {count} book(s)")

st.markdown("---")
st.markdown("© 2025 Arsalan Maniar - Personal Library Manager", unsafe_allow_html=True)
