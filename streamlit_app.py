import streamlit as st


# Functions
# Function to display the Home page
def show_home():
    st.title("Welcome to My Blog!")
    st.write("Here's a blog about games, AI, programming, and sci-fi TV shows.")


# Function to display the Games page
def show_games():
    st.title("Games")
    st.write("Content about games will go here.")


# Function to display the AI page
def show_ai():
    st.title("AI")
    st.write("Content about AI will go here.")


# Function to display the Programming page
def show_programming():
    st.title("Programming")
    st.write("Content about programming will go here.")


# Function to display the Sci-Fi TV Shows page
def show_scifi():
    st.title("Sci-Fi TV Shows")
    st.write("Content about sci-fi TV shows will go here.")


# Sidebar with buttons
st.sidebar.title("Navigation")
if st.sidebar.button('Home'):
    show_home()
if st.sidebar.button('Games'):
    show_games()
if st.sidebar.button('AI'):
    show_ai()
if st.sidebar.button('Programming'):
    show_programming()
if st.sidebar.button('Sci-Fi TV Shows'):
    show_scifi()
