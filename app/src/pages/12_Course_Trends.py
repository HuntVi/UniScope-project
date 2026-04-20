import streamlit as st
import requests
import pandas as pd
import altair as alt
from modules.nav import SideBarLinks

# Load shared sidebar navigation
SideBarLinks()

API_BASE_URL = "http://web-api:4000"

# Page header
st.title("Course Trends")
st.write("View how course ratings change across semesters and spot patterns over time.")


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
# Fetch trend data for one course
# Each row represents one semester
# ---------------------------------
def get_course_trends(course_id):
    try:
        r = requests.get(f"{API_BASE_URL}/courses/{course_id}/trends")
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []


# ---------------------------------
# Safe numeric conversion
# Returns None if value is missing
# ---------------------------------
def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

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

    trends = get_course_trends(selected_course_id)

    if not trends:
        st.warning("No trend data found for this course.")
    else:
        df = pd.DataFrame(trends)

        # Convert semester names into a sortable order
        # so Spring comes before Summer, and Summer before Fall
        semester_order = {"Spring": 1, "Summer": 2, "Fall": 3}
        df["semester_order"] = df["semester"].map(semester_order)

        # Sort by year first, then semester within each year
        df = df.sort_values(by=["year", "semester_order"]).reset_index(drop=True)

        # Create a display label and numeric sort key for the chart
        df["Term"] = df["semester"] + " " + df["year"].astype(str)
        df["sort_key"] = df["year"] * 10 + df["semester_order"]
        # Check whether this course has any usable numeric trend data
        has_any_trend_data = any(
            to_float(value) is not None
            for value in (
                df["avg_difficulty"].tolist()
                + df["avg_satisfaction"].tolist()
                + df["avg_workload"].tolist()
            )
        )
        
        # Count how many semester rows have at least one usable metric
        metric_cols = ["avg_difficulty", "avg_satisfaction", "avg_workload"]

        valid_trend_rows = df[
            df[metric_cols].apply(
                lambda col: col.map(lambda value: to_float(value) is not None)
            ).any(axis=1)
        ]

        has_enough_trend_points = len(valid_trend_rows) >= 2

        # Show a warning right away if the course has little or no trend data
        if not has_any_trend_data:
            st.warning("⚠️ This course does not have enough trend data yet.")
        elif not has_enough_trend_points:
            st.warning("⚠️ Only one semester of data is available, trends require at least two semesters.")

        # Reshape data so Altair can plot all 3 metrics on one chart
        chart_df = pd.DataFrame({
            "Term": list(df["Term"]) * 3,
            "sort_key": list(df["sort_key"]) * 3,
            "Metric": ["Difficulty"] * len(df) + ["Satisfaction"] * len(df) + ["Workload"] * len(df),
            "Value": (
                df["avg_difficulty"].apply(to_float).tolist()
                + df["avg_satisfaction"].apply(to_float).tolist()
                + df["avg_workload"].apply(to_float).tolist()
            )
        })

        st.subheader("Ratings Over Time")

        # Line chart showing how each metric changes by semester
        chart = (
            alt.Chart(chart_df)
            .mark_line(point=True)
            .encode(
                x=alt.X(
                    "Term:N",
                    sort=alt.SortField(field="sort_key", order="ascending"),
                    title="Semester"
                ),
                y=alt.Y("Value:Q", title="Average Rating"),
                color="Metric:N",
                tooltip=["Term", "Metric", "Value"]
            )
            .properties(height=400)
        )

        st.altair_chart(chart, use_container_width=True)

        # Optional raw data view for debugging or inspection
        with st.expander("Show raw trend data"):
            st.dataframe(
                df[["semester", "year", "avg_difficulty", "avg_satisfaction", "avg_workload"]],
                use_container_width=True
            )

        # Use the most recent row as the latest snapshot
        latest_row = df.iloc[-1]

        st.subheader("Latest Snapshot")
        col1, col2, col3 = st.columns(3)
        col1.metric("Difficulty", format_metric(latest_row["avg_difficulty"]))
        col2.metric("Workload", format_metric(latest_row["avg_workload"]))
        col3.metric("Satisfaction", format_metric(latest_row["avg_satisfaction"]))

        st.divider()
        st.subheader("Quick Take")

        # Compare the earliest and latest valid semesters
        # to describe the overall direction of change
        if not has_any_trend_data:
            st.info("This course does not have enough trend data yet.")
        elif not has_enough_trend_points:
            st.info("At least 2 semesters with review data are needed to identify a trend.")
        else:
            first_row = valid_trend_rows.iloc[0]
            last_row = valid_trend_rows.iloc[-1]
            insights = []

            first_sat = to_float(first_row["avg_satisfaction"])
            last_sat = to_float(last_row["avg_satisfaction"])
            if first_sat is not None and last_sat is not None:
                if last_sat > first_sat:
                    insights.append("Student satisfaction has improved over time.")
                elif last_sat < first_sat:
                    insights.append("Student satisfaction has declined over time.")

            first_diff = to_float(first_row["avg_difficulty"])
            last_diff = to_float(last_row["avg_difficulty"])
            if first_diff is not None and last_diff is not None:
                if last_diff > first_diff:
                    insights.append("Difficulty appears to be increasing.")
                elif last_diff < first_diff:
                    insights.append("Difficulty appears to be decreasing.")

            first_workload = to_float(first_row["avg_workload"])
            last_workload = to_float(last_row["avg_workload"])
            if first_workload is not None and last_workload is not None:
                if last_workload > first_workload:
                    insights.append("Workload appears to be increasing.")
                elif last_workload < first_workload:
                    insights.append("Workload appears to be decreasing.")

            if insights:
                for insight in insights:
                    st.info(insight)
            else:
                st.success("The ratings look fairly stable over time.")