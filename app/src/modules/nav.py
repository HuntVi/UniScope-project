import streamlit as st


# General

def home_nav():
    st.sidebar.page_link('Home.py', label='Home', icon='🏠')


# Role: student (Jason)

def student_home_nav():
    st.sidebar.page_link('pages/00_Student_Home.py', label='Student Home', icon='👤')

def course_reviews_nav():
    st.sidebar.page_link('pages/01_Course_Reviews.py', label='Course Reviews', icon='📋')

def submit_review_nav():
    st.sidebar.page_link('pages/02_Submit_Review.py', label='Submit a Review', icon='✏️')

def semester_plan_nav():
    st.sidebar.page_link('pages/03_Semester_Plan.py', label='Semester Plans', icon='📅')


# Role: professor (Josh)

def professor_home_nav():
    st.sidebar.page_link('pages/10_Professor_Home.py', label='Professor Home', icon='👤')

def course_ratings_nav():
    st.sidebar.page_link('pages/11_Course_Ratings.py', label='My Course Ratings', icon='📊')

def course_trends_nav():
    st.sidebar.page_link('pages/12_Course_Trends.py', label='Rating Trends', icon='📈')

def student_feedback_nav():
    st.sidebar.page_link('pages/13_Student_Feedback.py', label='Student Feedback', icon='💬')


# Role: advisor (Muhammad)

def advisor_home_nav():
    st.sidebar.page_link('pages/20_Advisor_Home.py', label='Advisor Home', icon='👤')

def course_comparison_nav():
    st.sidebar.page_link('pages/21_Course_Comparison.py', label='Course Comparison', icon='🔍')

def student_profile_nav():
    st.sidebar.page_link('pages/22_Student_Profile.py', label='Student Profile', icon='🎓')

def plan_evaluator_nav():
    st.sidebar.page_link('pages/23_Plan_Evaluator.py', label='Plan Evaluator', icon='⚖️')


# Role: admin (Barry)

def admin_home_nav():
    st.sidebar.page_link('pages/30_Admin_Home.py', label='Admin Home', icon='🖥️')

def review_moderation_nav():
    st.sidebar.page_link('pages/31_Review_Moderation.py', label='Review Moderation', icon='🛡️')

def flag_management_nav():
    st.sidebar.page_link('pages/32_Flag_Management.py', label='Flag Management', icon='🚩')

def system_logs_nav():
    st.sidebar.page_link('pages/33_System_Logs.py', label='System Logs', icon='📜')


# Sidebar

def SideBarLinks(show_home=False):
    st.sidebar.image('assets/logo.png', width=150)

    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page('Home.py')

    if show_home:
        home_nav()

    if st.session_state['authenticated']:

        if st.session_state['role'] == 'student':
            student_home_nav()
            course_reviews_nav()
            submit_review_nav()
            semester_plan_nav()

        if st.session_state['role'] == 'professor':
            professor_home_nav()
            course_ratings_nav()
            course_trends_nav()
            student_feedback_nav()

        if st.session_state['role'] == 'advisor':
            advisor_home_nav()
            course_comparison_nav()
            student_profile_nav()
            plan_evaluator_nav()

        if st.session_state['role'] == 'admin':
            admin_home_nav()
            review_moderation_nav()
            flag_management_nav()
            system_logs_nav()

    if st.session_state['authenticated']:
        if st.sidebar.button('Logout'):
            del st.session_state['role']
            del st.session_state['authenticated']
            st.switch_page('Home.py')
