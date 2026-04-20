import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

SideBarLinks()

API_BASE_URL = "http://web-api:4000"

# ========================================================
# Course Comparison Page
# Covers Muhammad's User Stories 1 & 4:
# 1. Compare multiple courses across departments
# 4. Know difficulty trends of different courses recent semesters
# ========================================================
st.title('📊 Course Comparison')
st.write(
    "Compare courses within a department based on student review data. "
    "Find the best electives for your students by looking at difficulty, "
    "workload, and satisfaction scores."
)

st.divider()

# ---- Load departments for dropdown ----
@st.cache_data(ttl=60)
def load_departments():
    try:
        r = requests.get(f"{API_BASE_URL}/departments")
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

departments = load_departments()

if not departments:
    st.error("Could not load departments. Please check API connection.")
    st.stop()

# ---- Select department ----
dept_map = {d['department_name']: d['department_id'] for d in departments}
selected_dept_name = st.selectbox(
    "Select a department:",
    options=list(dept_map.keys()),
    help="Pick a department to see all its courses and their review metrics."
)
selected_dept_id = dept_map[selected_dept_name]

# ---- Fetch courses in that department ----
try:
    resp = requests.get(f"{API_BASE_URL}/departments/{selected_dept_id}/courses")

    if resp.status_code == 200:
        courses = resp.json()

        if courses:
            st.success(f"Found {len(courses)} courses in {selected_dept_name}")

            # Convert to DataFrame
            df = pd.DataFrame(courses)

            # ---- Summary metrics ----
            st.subheader("📈 Department Summary")
            reviewed_df = df[df['review_count'].fillna(0) > 0]

            if not reviewed_df.empty:
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Courses with Reviews", len(reviewed_df))
                m2.metric("Avg Difficulty", f"{reviewed_df['avg_difficulty'].mean():.2f}/5")
                m3.metric("Avg Workload", f"{reviewed_df['avg_workload'].mean():.2f}/5")
                m4.metric("Avg Satisfaction", f"{reviewed_df['avg_satisfaction'].mean():.2f}/5")

            st.divider()

            # ---- Detail table ----
            st.subheader("📋 Course Details")
            display_cols = [
                'course_code', 'course_name', 'credits',
                'avg_difficulty', 'avg_workload',
                'avg_clarity', 'avg_satisfaction', 'review_count'
            ]
            display_cols = [c for c in display_cols if c in df.columns]
            st.dataframe(
                df[display_cols].rename(columns={
                    'course_code': 'Code',
                    'course_name': 'Name',
                    'credits': 'Credits',
                    'avg_difficulty': 'Difficulty',
                    'avg_workload': 'Workload',
                    'avg_clarity': 'Clarity',
                    'avg_satisfaction': 'Satisfaction',
                    'review_count': '# Reviews'
                }),
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            # ---- Difficulty comparison chart ----
            if not reviewed_df.empty:
                st.subheader("📊 Difficulty vs Workload")
                chart_df = reviewed_df[['course_code', 'avg_difficulty', 'avg_workload']].copy()
                chart_df = chart_df.set_index('course_code')
                st.bar_chart(chart_df)

                st.subheader("⭐ Satisfaction by Course")
                sat_df = reviewed_df[['course_code', 'avg_satisfaction']].copy()
                sat_df = sat_df.set_index('course_code')
                st.bar_chart(sat_df)

        else:
            st.info(f"No courses found in {selected_dept_name}.")

    elif resp.status_code == 404:
        st.warning(f"{selected_dept_name} has no courses yet.")
    else:
        st.error(f"Error loading courses: {resp.status_code}")

except requests.exceptions.RequestException as e:
    st.error(f"Connection error: {e}")