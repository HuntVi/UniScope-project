import streamlit as st
import requests
from modules.nav import SideBarLinks

# Load shared sidebar navigation
SideBarLinks()

API_BASE_URL = "http://web-api:4000"

# Page header
st.title("Course Ratings")
st.write("View overall course ratings and quickly spot courses with high difficulty or low satisfaction.")


# ---------------------------------
# Fetch all courses for dropdown
# ---------------------------------
def get_courses():
    try:
        r = requests.get(f"{API_BASE_URL}/courses")
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []


# ---------------------------------
# Fetch summarized review metrics
# for one selected course
# ---------------------------------
def get_review_summary(course_id):
    try:
        r = requests.get(f"{API_BASE_URL}/courses/{course_id}/reviewsummary")
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None


# ---------------------------------
# Safe numeric conversion
# Helps avoid crashes if values are
# missing or returned as strings
# ---------------------------------
def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# ---------------------------------
# Format numbers for display
# Show 2 decimals or N/A
# ---------------------------------
def format_metric(value):
    num = to_float(value)
    if num is None:
        return "N/A"
    return f"{num:.2f}"


courses = get_courses()

if not courses:
    st.error("Could not load courses.")
else:
    # Build dropdown labels like:
    # CS2500 - Fundamentals of Computer Science
    course_map = {
        f"{c['course_code']} - {c['course_name']}": c['course_id']
        for c in courses
    }

    selected_course = st.selectbox("Select a course", list(course_map.keys()))
    selected_course_id = course_map[selected_course]

    summary = get_review_summary(selected_course_id)

    if not summary:
        st.warning("No review summary found for this course.")
    else:
        # API returns a list, so use the first row
        if isinstance(summary, list) and len(summary) > 0:
            summary = summary[0]

        difficulty_raw = summary.get("avg_difficulty")
        workload_raw = summary.get("avg_workload")
        clarity_raw = summary.get("avg_clarity")
        satisfaction_raw = summary.get("avg_satisfaction")
        fairness_raw = summary.get("avg_fairness")

        # Check whether this course has any usable numeric review data
        has_any_data = any(
            to_float(summary.get(key)) is not None
            for key in [
                "avg_difficulty",
                "avg_workload",
                "avg_clarity",
                "avg_satisfaction",
                "avg_fairness"
            ]
        )

        # Show a note right away if the course has little or no review data
        if not has_any_data:
            st.warning("⚠️ This course does not have enough review data yet.")

        st.subheader("Aggregated Ratings")

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Difficulty", format_metric(difficulty_raw))
        col2.metric("Workload", format_metric(workload_raw))
        col3.metric("Clarity", format_metric(clarity_raw))
        col4.metric("Satisfaction", format_metric(satisfaction_raw))
        col5.metric("Fairness", format_metric(fairness_raw))

        st.divider()
        st.subheader("Quick Take")

        # Convert selected fields to numbers for simple interpretation
        difficulty = to_float(difficulty_raw)
        satisfaction = to_float(satisfaction_raw)

        if not has_any_data:
            st.info("This course does not have enough review data yet.")
        elif difficulty is not None and satisfaction is not None:
            if difficulty >= 4 and satisfaction <= 2.5:
                st.warning(
                    "Students rate this course as relatively difficult, and satisfaction is also on the lower side."
                )
            elif difficulty >= 4:
                st.info("Students rate this course as relatively difficult.")
            elif satisfaction <= 2.5:
                st.info("Student satisfaction for this course is on the lower side.")
            else:
                st.success("No major difficulty or satisfaction flags stand out based on the current review summary.")
        else:
            st.info("Not enough numeric data is available for a quick summary yet.")