import streamlit as st
import requests
from modules.nav import SideBarLinks

SideBarLinks()

st.title('Course Reviews')
st.write("Explore course difficulty ratings and read structured reviews from students...")
st.divider()

# TODO: implement (Jason user stories 3 & 4)
# - View course difficulty ratings
# - Read structured course reviews

API_BASE_URL = "http://web-api:4000"

# Fetch course info from backends
@st.cache_data
def get_courses():
    try:
        response = requests.get(f"{API_BASE_URL}/courses")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Failed to connect to API: {e}")
    return []

# Fetch reviews with specific course_id
def get_reviews(course_id):
    try:
        response = requests.get(f"{API_BASE_URL}/courses/{course_id}/reviews")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Failed to fetch reviews: {e}")
    return []

courses = get_courses()

# Check if we actually get the courses instead of any empty list
if len(courses) > 0:
    course_options = {f"{c['course_code']} - {c['course_name']}": c for c in courses}

    # Allow user to select a course
    selected_course_label = st.selectbox("Search and select a course:", 
    options=list(course_options.keys())
    )

    if selected_course_label:
        course_data = course_options[selected_course_label]
        
        # Display Course Description
        st.subheader(f"📖 {course_data['course_code']} Description")
        st.write(course_data.get('description', 'No description available.'))

        # 1.3: View course ratings 
        st.subheader("Aggregated Metrics")
        
        # Formatting
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Difficulty", course_data.get('avg_difficulty') or "N/A")
        col2.metric("Workload", course_data.get('avg_workload') or "N/A")
        col3.metric("Satisfaction", course_data.get('avg_satisfaction') or "N/A")
        col4.metric("Total Reviews", course_data.get('review_count', 0))

        st.divider()

        # 1.4: Read course reviews
        st.subheader("Structured Reviews")
        
        reviews = get_reviews(course_data['course_id'])

        if reviews:
            for r in reviews:
                with st.container(border=True):
                    # Specify time of the course
                    st.write(f"Semester: {r['semester']} {r['year']} | Date: {r['review_date']}")
                    
                    # Individual comment scores for courses
                    score_col1, score_col2, score_col3, score_col4 = st.columns(4)
                    score_col1.write(f"**Difficulty:** {r['difficulty_score']}")
                    score_col2.write(f"**Workload:** {r['workload_score']}")
                    score_col3.write(f"**Clarity:** {r['clarity_score']}")
                    
                    # Attendance boolean check
                    attendance = "Yes" if r['attendance_required'] else "No"
                    score_col4.write(f"**Attendance Req:** {attendance}")
                    
                    # Print student comments on page
                    st.write(r['comment_text'])
        else:
            st.info("No reviews available for this course yet.")
else:
    st.warning("No courses found.")
