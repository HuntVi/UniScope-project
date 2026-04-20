import streamlit as st
import requests
from modules.nav import SideBarLinks

SideBarLinks()

st.title("Student Profile Lookup")

# TODO: implement (Muhammad user stories 2 & 5)
# - View a student's academic profile and progress
# - View recent course comments and review data for context

API_BASE_URL = "http://web-api:4000"

# Getter for a single student's profile
def get_student(student_id):
    try:
        r = requests.get(f"{API_BASE_URL}/students/{student_id}")
        if r.status_code == 200:
            return r.json()
        else:
            return None
    except:
        return None

# Getter for that student's past reviews
def get_student_reviews(student_id):
    try:
        r = requests.get(f"{API_BASE_URL}/reviews", params={"student_id": student_id})
        if r.status_code == 200:
            return r.json()
        else:
            return []
    except:
        return []

# Student ID input
with st.expander("Look Up a Student", expanded=True):
    with st.form("student_lookup_form"):
        sid = st.number_input(
            "Enter Student ID:",
            min_value=1, max_value=500, value=1
        )
        lookup_btn = st.form_submit_button("Look Up")

        if lookup_btn:
            st.session_state["looked_up_sid"] = sid

# Display profile if a student has been looked up
if "looked_up_sid" in st.session_state:
    sid = st.session_state["looked_up_sid"]
    data = get_student(sid)

    if data:
        # API may return list or dict — handle both
        student = data[0] if isinstance(data, list) else data

        st.divider()
        st.subheader("Academic Profile")

        with st.container(border=True):
            st.write(f"### {student.get('student_name', 'Unknown')}")
            st.caption(f"📧 {student.get('student_email', 'N/A')} | Student ID: {student.get('student_id', 'N/A')}")

            st.divider()

            c1, c2, c3 = st.columns(3)
            c1.metric("Academic Year", student.get("academic_year", "N/A"))
            c2.metric("Total Hours", student.get("total_hours", 0))
            c3.metric("Department", student.get("department_name", "N/A"))

        # Past reviews by this student
        st.divider()
        st.subheader("Recent Reviews by This Student")
        st.caption("Shows what courses this student has reviewed — useful for advising context.")

        reviews = get_student_reviews(sid)

        if reviews:
            for r in reviews:
                with st.container(border=True):
                    st.write(f"### {r.get('course_code')} - {r.get('course_name')}")
                    st.caption(
                        f"📅 {r.get('semester')} {r.get('year')} | "
                        f"Submitted on: {r.get('review_date')}"
                    )

                    st.divider()

                    s1, s2, s3 = st.columns(3)
                    s1.metric("Difficulty", f"{r.get('difficulty_score', 0)}/5")
                    s2.metric("Workload", f"{r.get('workload_score', 0)}/5")
                    s3.metric("Satisfaction", f"{r.get('satisfaction_score', 0)}/5")

                    if r.get("comment_text"):
                        st.write(f"Comment: {r.get('comment_text')}")
        else:
            st.info("This student hasn't submitted any reviews yet.")
    else:
        st.error(f"Student with ID {sid} not found.")