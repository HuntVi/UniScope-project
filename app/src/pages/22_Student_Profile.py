import streamlit as st
import requests
from modules.nav import SideBarLinks

SideBarLinks()

API_BASE_URL = "http://web-api:4000"

# ========================================================
# Student Profile Page
# Corresponds to Muhammad's User Story 5:
# "View a student's academic profile and progress"
# ========================================================
st.title('👤 Student Profile Lookup')
st.write(
    "Enter a student ID to view their academic profile, "
    "including department, academic year, and completed credit hours."
)

st.divider()

# ---- Input ----
col1, col2 = st.columns([2, 1])
with col1:
    student_id = st.number_input(
        "Student ID",
        min_value=1,
        max_value=500,
        value=1,
        help="Enter the student's ID number"
    )
with col2:
    st.write("")
    st.write("")
    lookup_btn = st.button("🔍 Look up Student", type="primary", use_container_width=True)

# ---- Fetch & display profile ----
if lookup_btn or student_id:
    try:
        response = requests.get(f"{API_BASE_URL}/students/{student_id}")

        if response.status_code == 200:
            data = response.json()
            # API returns a list; take first element
            student = data[0] if isinstance(data, list) else data

            st.success(f"Profile loaded for Student ID {student_id}")

            # Display profile in a nice layout
            with st.container(border=True):
                st.subheader(f"📝 {student.get('student_name', 'Unknown')}")

                c1, c2, c3 = st.columns(3)
                c1.metric("Academic Year", student.get('academic_year', 'N/A'))
                c2.metric("Total Credit Hours", student.get('total_hours', 0))
                c3.metric("Department", student.get('department_name', 'N/A'))

                st.write(f"**Email:** {student.get('student_email', 'N/A')}")
                st.write(f"**Student ID:** {student.get('student_id', 'N/A')}")

            # ---- Extra insight: show recent reviews by this student ----
            st.divider()
            st.subheader("📝 Recent Reviews by This Student")
            st.caption("User Story 2: View recent course comments and review data")

            reviews_resp = requests.get(
                f"{API_BASE_URL}/reviews",
                params={"student_id": student_id}
            )

            if reviews_resp.status_code == 200:
                reviews = reviews_resp.json()
                if reviews:
                    for r in reviews[:5]:  # show top 5
                        with st.container(border=True):
                            st.write(
                                f"**{r.get('course_code', '')} — {r.get('course_name', '')}** "
                                f"({r.get('semester', '')} {r.get('year', '')})"
                            )
                            cc1, cc2, cc3 = st.columns(3)
                            cc1.metric("Difficulty", f"{r.get('difficulty_score', 0)}/5")
                            cc2.metric("Workload", f"{r.get('workload_score', 0)}/5")
                            cc3.metric("Satisfaction", f"{r.get('satisfaction_score', 0)}/5")
                            if r.get('comment_text'):
                                st.write(f"💬 _{r.get('comment_text')}_")
                else:
                    st.info("This student hasn't submitted any reviews yet.")
            else:
                st.warning("Could not load reviews for this student.")

        elif response.status_code == 404:
            st.error(f"❌ Student with ID {student_id} not found.")
        else:
            st.error(f"Error loading student: {response.status_code}")

    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")