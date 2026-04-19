import streamlit as st
from modules.nav import SideBarLinks

SideBarLinks()

st.title(f'Welcome, {st.session_state.get("first_name", "Student")}!')
st.write('What would you like to do today?')
st.divider()

# TODO: add navigation cards or buttons to student feature pages

f1, f2, f3 = st.columns(3)

# Feature1: Course Explorer
with f1:
    st.subheader("Course Explorer")
    st.write("Browse courses, check difficulty ratings, and read structured reviews from real students.")
    st.page_link("pages/01_Course_Reviews.py", label="Explore Courses")

# Feature2: My Reviews
with f2:
    st.subheader("My Reviews")
    st.write("Share your experience! Submit new reviews, edit past feedback, or report inappropriate comments.")
    st.page_link("pages/02_Submit_Review.py", label="Manage My Reviews")

# Feature3: Semester Planner
with f3:
    st.subheader("Semester Planner")
    st.write("Create, adjust, and evaluate your upcoming semester schedules based on workload data.")
    st.page_link("pages/03_Semester_Plan.py", label="Plan My Semester")