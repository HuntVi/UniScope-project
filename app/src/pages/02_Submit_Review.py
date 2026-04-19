import streamlit as st
import requests
from modules.nav import SideBarLinks
from datetime import datetime

SideBarLinks()

st.title('Submit a Review')

# TODO: implement (Jason user stories 1 & 2)
# - Submit, edit, delete a course review
# - Report inappropriate review
API_BASE_URL = "http://web-api:4000"

# Getter
def get_courses():
    try:
        r = requests.get(f"{API_BASE_URL}/courses")
        if r.status_code == 200:
            return r.json() 
        else: 
            return []
    except: 
        return []
    
courses = get_courses()

# Check if app actually get the courses instead of any empty list
if len(courses) > 0:
    course_map = {f"{c['course_code']} - {c['course_name']}": c['course_id'] for c in courses}

    # 1.1 Post Review
    with st.expander("Post a New Review", expanded=True):
        with st.form("new_review_form"):
            selected_course = st.selectbox("Select Course:", options=list(course_map.keys()))
            
            # Formatting
            col1, col2 = st.columns(2)
            current_year = datetime.now().year
            sem = col1.selectbox("Semester:", ["Fall", "Spring", "Summer"])
            yr = col2.number_input("Year:", 2020, 2030, current_year) # Min 2020, Max 2030, Default current yr
            
            # Draw a line on GUI to seperate scoring from time info above
            st.write("---") 

            # Slider for User to select whole number score, default at 3
            d_score = st.select_slider("Difficulty (1=Easy, 5=Hard):", options=[1,2,3,4,5], value=3)
            w_score = st.select_slider("Workload (1=Light, 5=Heavy):", options=[1,2,3,4,5], value=3)
            c_score = st.select_slider("Clarity:", options=[1,2,3,4,5], value=3)
            s_score = st.select_slider("Overall Satisfaction:", options=[1,2,3,4,5], value=3)
            f_score = st.select_slider("Fairness of Grading:", options=[1,2,3,4,5], value=3)

            col_a, col_b = st.columns(2)
            w_hours = col_a.number_input("Weekly Hours Spent:", min_value=0, max_value=168, value=10)
            a_needs = col_b.checkbox("Is Attendance Required?")
            
            comment = st.text_area("Your Review:", placeholder="Leave your experience with us.")
            
            submit_btn = st.form_submit_button("Submit Review")

            if submit_btn:
                if not comment:
                    st.warning("Please enter a comment.")
                else:
                    # Packageing comment 
                    payload = {
                        "student_id": 1, #Test purposes
                        "offering_id": 1, #Test purposes
                        "course_id": course_map[selected_course],
                        "difficulty_score": d_score,
                        "workload_score": w_score,
                        "clarity_score": c_score,
                        "satisfaction_score": s_score,
                        "fairness_score": f_score,
                        "attendance_required": 1 if a_needs else 0,
                        "weekly_hours": w_hours,
                        "comment_text": comment,
                        "semester": sem,
                        "year": yr,
                        "review_date": datetime.now().strftime("%Y-%m-%d")
                    }
                    res = requests.post(f"{API_BASE_URL}/reviews", json=payload)
                    if res.status_code in [200, 201]:
                        st.success("Review submitted successfully!")
                        st.balloons()
                        st.rerun() # Rerun so after sucessful submission, comment should appear
                    else:
                        st.error(f"Error from API: {res.text}")

    # 1.1 Edit or delete past reviews
    st.divider()
    st.subheader("Your Past Reviews")
    
    try:
        # Pull all reviews
        all_reviews = requests.get(f"{API_BASE_URL}/reviews").json()
        st.write(f"Debug: Total reviews found: {len(all_reviews)}")
        
        if all_reviews:
            for r in all_reviews:
                with st.container(border=True):
                    # Check if the same comment
                    st.write(f"**Course ID: {r['course_id']}** | {r['semester']} {r['year']}")
                    st.write(f"Comment: {r['comment_text']}")
                    
                    edit_col, del_col, _ = st.columns([1, 1, 4])
                    
                    # Delete
                    if del_col.button("Delete", key=f"del_{r['review_id']}"):
                        del_res = requests.delete(f"{API_BASE_URL}/reviews/{r['review_id']}")
                        if del_res.status_code == 200:
                            st.toast("Review deleted!")
                            st.rerun()
                    
                    # Edit
                    if edit_col.button("Edit", key=f"edit_{r['review_id']}"):
                        st.session_state['editing_review'] = r
                        st.info("Edit mode: This would load the form above with these values.")
        else:
            st.info("You haven't submitted any reviews yet.")
    except Exception as e:
        st.write("Could not load your previous reviews at this time. Please try again later.")

else:
    st.error("No courses found.")