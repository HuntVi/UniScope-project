import streamlit as st
from modules.nav import SideBarLinks

SideBarLinks()

st.title(f"Welcome, {st.session_state.get('first_name', 'Muhammad')}!")

# TODO: implement (Muhammad user stories overview)
# - Provide navigation to all advisor features
# - Quick overview of available tools

st.write("### Your Advisor Dashboard")
st.write(
    "Help your students plan their academic journey with data-driven insights. "
    "Use the tools below to compare courses, review student profiles, and evaluate semester plans."
)

st.divider()
st.subheader("What would you like to do today?")

# Navigation cards for the 3 main feature pages
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.write("### 📊 Course Comparison")
        st.caption("Compare courses across departments and see difficulty trends.")
        if st.button("Open", key="btn_compare", use_container_width=True):
            st.switch_page("pages/21_Course_Comparison.py")

with col2:
    with st.container(border=True):
        st.write("### 👤 Student Profile")
        st.caption("Look up a student's academic profile and recent reviews.")
        if st.button("Open", key="btn_profile", use_container_width=True):
            st.switch_page("pages/22_Student_Profile.py")

with col3:
    with st.container(border=True):
        st.write("### 📋 Plan Evaluator")
        st.caption("Create, evaluate, and manage semester plans.")
        if st.button("Open", key="btn_plan", use_container_width=True):
            st.switch_page("pages/23_Plan_Evaluator.py")

st.divider()
st.caption(
    "💡 Tip: Start with Student Profile to understand your advisee, "
    "then use Course Comparison to explore options, "
    "and finally build their schedule in the Plan Evaluator."
)