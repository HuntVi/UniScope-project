import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

# Load shared sidebar navigation
SideBarLinks()

API_BASE_URL = "http://web-api:4000"

# Page header
st.title("Student Feedback")
st.write("View review summaries and read detailed student comments for each course.")


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
# Fetch summary metrics for one course
# Used for the top review snapshot
# ---------------------------------
def get_review_summary(course_id):
    try:
        r = requests.get(f"{API_BASE_URL}/courses/{course_id}/reviewsummary")
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0]
    except:
        pass
    return None


# ---------------------------------
# Fetch detailed reviews for one course
# ---------------------------------
def get_course_reviews(course_id):
    try:
        r = requests.get(f"{API_BASE_URL}/courses/{course_id}/reviews")
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []


courses = get_courses()

if not courses:
    st.error("Could not load courses.")
    st.stop()

# Build dropdown labels like:
# CS2500 - Fundamentals of Computer Science
course_options = {
    f"{c['course_code']} - {c['course_name']}": c["course_id"]
    for c in courses
}

selected_course_label = st.selectbox(
    "Select a course",
    options=list(course_options.keys())
)

selected_course_id = course_options[selected_course_label]

summary = get_review_summary(selected_course_id)
reviews = get_course_reviews(selected_course_id)

# Show summary metrics at the top if available
if summary:
    st.subheader("Feedback Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Reviews", int(summary.get("review_count", 0) or 0))
    col2.metric("Difficulty", summary.get("avg_difficulty", "N/A"))
    col3.metric("Workload", summary.get("avg_workload", "N/A"))

    col4, col5, col6 = st.columns(3)
    col4.metric("Clarity", summary.get("avg_clarity", "N/A"))
    col5.metric("Satisfaction", summary.get("avg_satisfaction", "N/A"))
    col6.metric("Fairness", summary.get("avg_fairness", "N/A"))

    avg_hours = summary.get("avg_weekly_hours")
    if avg_hours is not None:
        st.caption(f"Average weekly hours: {avg_hours}")

# Stop early if no detailed reviews exist yet
if not reviews:
    st.info("No reviews found for this course yet.")
    st.stop()

df = pd.DataFrame(reviews)

st.subheader("Filter Reviews")

col1, col2 = st.columns(2)

with col1:
    year_filter = st.multiselect(
        "Year",
        options=sorted(df["year"].dropna().unique().tolist(), reverse=True),
        default=sorted(df["year"].dropna().unique().tolist(), reverse=True)
    )

with col2:
    semester_filter = st.multiselect(
        "Semester",
        options=["Spring", "Summer", "Fall"],
        default=[s for s in ["Spring", "Summer", "Fall"] if s in df["semester"].dropna().unique().tolist()]
    )

# Start with all reviews, then apply filters
filtered_df = df.copy()

if year_filter:
    filtered_df = filtered_df[filtered_df["year"].isin(year_filter)]

if semester_filter:
    filtered_df = filtered_df[filtered_df["semester"].isin(semester_filter)]

# Sort filtered reviews so the newest semesters appear first
semester_order = {"Spring": 1, "Summer": 2, "Fall": 3}
filtered_df["semester_order"] = filtered_df["semester"].map(semester_order)

filtered_df = filtered_df.sort_values(
    by=["year", "semester_order"],
    ascending=[False, False]
)

st.subheader("Student Comments")

if filtered_df.empty:
    st.warning("No reviews match the selected filters.")
else:
    for _, row in filtered_df.iterrows():
        title = f"{row.get('semester', '')} {row.get('year', '')}"

        # Use a bordered container so each review feels like its own card
        with st.container(border=True):
            st.markdown(f"### 📘 {title}")

            # Show the review scores in a compact row
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Difficulty", row.get("difficulty_score", "N/A"))
            c2.metric("Workload", row.get("workload_score", "N/A"))
            c3.metric("Clarity", row.get("clarity_score", "N/A"))
            c4.metric("Satisfaction", row.get("satisfaction_score", "N/A"))
            c5.metric("Fairness", row.get("fairness_score", "N/A"))

            # Show a few extra course details below the scores
            c6, c7 = st.columns(2)
            c6.write(
                f"**Attendance Required:** {'Yes' if row.get('attendance_required') == 1 else 'No'}"
            )
            c7.write(f"**Weekly Hours:** {row.get('weekly_hours', 'N/A')}")

            # Highlight the written comment so it stands out from the numbers
            comment = row.get("comment_text", "")
            if comment:
                st.markdown(f"> {comment}")
            else:
                st.caption("No comment provided.")