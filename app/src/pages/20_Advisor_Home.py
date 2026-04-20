import streamlit as st
from modules.nav import SideBarLinks

SideBarLinks()

st.title(f'Welcome, {st.session_state.get("first_name", "Muhammad")}! 👋')
st.write('### Your Advisor Dashboard')
st.write(
    'Help your students plan their academic journey with data-driven insights. '
    'Explore the tools below to compare courses, review student profiles, '
    'and evaluate semester plans.'
)

st.divider()

st.subheader('🔧 What would you like to do today?')

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("### 📊 Course Comparison")
        st.write(
            "Compare multiple courses across departments. "
            "View difficulty trends and workload data to recommend "
            "the right electives for your students."
        )
        if st.button("Open Course Comparison", key="btn_compare", use_container_width=True):
            st.switch_page('pages/21_Course_Comparison.py')

with col2:
    with st.container(border=True):
        st.markdown("### 👤 Student Profile")
        st.write(
            "View a student's academic profile, "
            "including their department, year, and completed credit hours."
        )
        if st.button("Open Student Profile", key="btn_profile", use_container_width=True):
            st.switch_page('pages/22_Student_Profile.py')

with col3:
    with st.container(border=True):
        st.markdown("### 📋 Plan Evaluator")
        st.write(
            "Create, evaluate, and manage semester plans. "
            "Add or remove courses and check whether a plan is balanced."
        )
        if st.button("Open Plan Evaluator", key="btn_plan", use_container_width=True):
            st.switch_page('pages/23_Plan_Evaluator.py')

st.divider()

st.caption(
    "💡 Tip: Start with the **Student Profile** to understand your advisee, "
    "then use **Course Comparison** to explore options, "
    "and finally build their schedule in the **Plan Evaluator**."
)