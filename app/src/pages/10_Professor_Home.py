import streamlit as st
from modules.nav import SideBarLinks

# Load shared sidebar navigation
SideBarLinks()

# Page title with fallback if session name is missing
st.title(f"Welcome, {st.session_state.get('first_name', 'Professor')}!")

# Simple, natural intro
st.write("What would you like to look at today?")
st.divider()

# Create 3 columns for the main tools
col1, col2, col3 = st.columns(3)

# -------------------------------
# Tool 1: Course Ratings
# -------------------------------
with col1:
    with st.container(border=True):
        st.markdown("### 📊 Course Ratings")
        st.write(
            "See overall course ratings like difficulty, workload, clarity, and satisfaction."
        )
        # Direct navigation instead of relying only on sidebar
        st.page_link("pages/11_Course_Ratings.py", label="View Course Ratings")


# -------------------------------
# Tool 2: Course Trends
# -------------------------------
with col2:
    with st.container(border=True):
        st.markdown("### 📈 Course Trends")
        st.write(
            "Track how ratings change across semesters and spot patterns over time."
        )
        st.page_link("pages/12_Course_Trends.py", label="View Course Trends")


# -------------------------------
# Tool 3: Student Feedback
# -------------------------------
with col3:
    with st.container(border=True):
        st.markdown("### 💬 Student Feedback")
        st.write(
            "Read student comments and review summaries to understand the student experience."
        )
        st.page_link("pages/13_Student_Feedback.py", label="View Student Feedback")