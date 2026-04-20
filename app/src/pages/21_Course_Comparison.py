import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

SideBarLinks()

st.title("Course Comparison")

# TODO: implement (Muhammad user stories 1 & 4)
# - Compare multiple courses across departments
# - View course difficulty trends / workload distribution

API_BASE_URL = "http://web-api:4000"

# Getter for departments
def get_departments():
    try:
        r = requests.get(f"{API_BASE_URL}/departments")
        if r.status_code == 200:
            return r.json()
        else:
            return []
    except:
        return []

# Getter for courses of a department
def get_department_courses(dept_id):
    try:
        r = requests.get(f"{API_BASE_URL}/departments/{dept_id}/courses")
        if r.status_code == 200:
            return r.json()
        else:
            return []
    except:
        return []

departments = get_departments()

# Check if we actually got departments
if len(departments) > 0:
    dept_map = {d["department_name"]: d["department_id"] for d in departments}

    with st.expander("Choose a Department to Compare", expanded=True):
        selected_dept = st.selectbox("Select Department:", options=list(dept_map.keys()))
        dept_id = dept_map[selected_dept]

    # Pull courses for that department
    courses = get_department_courses(dept_id)

    if courses:
        st.success(f"Found {len(courses)} courses in {selected_dept}")

        df = pd.DataFrame(courses)
        reviewed_df = df[df["review_count"].fillna(0) > 0]

        # Department-level summary metrics
        st.divider()
        st.subheader("Department Summary")

        if not reviewed_df.empty:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Courses Reviewed", len(reviewed_df))
            m2.metric("Avg Difficulty", f"{reviewed_df['avg_difficulty'].mean():.2f}/5")
            m3.metric("Avg Workload", f"{reviewed_df['avg_workload'].mean():.2f}/5")
            m4.metric("Avg Satisfaction", f"{reviewed_df['avg_satisfaction'].mean():.2f}/5")
        else:
            st.info("No reviews yet in this department.")

        # Detail table
        st.divider()
        st.subheader("Course Details")

        display_cols = [
            "course_code", "course_name", "credits",
            "avg_difficulty", "avg_workload",
            "avg_clarity", "avg_satisfaction", "review_count"
        ]
        display_cols = [c for c in display_cols if c in df.columns]

        st.dataframe(
            df[display_cols].rename(columns={
                "course_code": "Code",
                "course_name": "Name",
                "credits": "Credits",
                "avg_difficulty": "Difficulty",
                "avg_workload": "Workload",
                "avg_clarity": "Clarity",
                "avg_satisfaction": "Satisfaction",
                "review_count": "# Reviews"
            }),
            use_container_width=True,
            hide_index=True
        )

        # Charts
        if not reviewed_df.empty:
            st.divider()
            st.subheader("Difficulty vs Workload")
            chart_df = reviewed_df[["course_code", "avg_difficulty", "avg_workload"]].set_index("course_code")
            st.bar_chart(chart_df)

            st.subheader("Satisfaction by Course")
            sat_df = reviewed_df[["course_code", "avg_satisfaction"]].set_index("course_code")
            st.bar_chart(sat_df)
    else:
        st.info(f"No courses found in {selected_dept}.")

else:
    st.error("No departments found.")