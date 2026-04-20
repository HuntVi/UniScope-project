import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

SideBarLinks()

st.title("Semester Plan Evaluator")

# TODO: implement (Muhammad user stories 3 & 6)
# - Evaluate if a semester plan is balanced and sustainable
# - Dashboard of difficulty/workload across courses and student levels
# - Uses POST /semesterplans, DELETE /semesterplans/{id},
#   POST /semesterplans/{id}/courses/{cid}, DELETE /semesterplans/{id}/courses/{cid}

API_BASE_URL = "http://web-api:4000"

# Getter for a single plan
def get_plan(plan_id):
    try:
        r = requests.get(f"{API_BASE_URL}/semesterplans/{plan_id}")
        if r.status_code == 200:
            return r.json()
        else:
            return None
    except:
        return None

# Getter for workload analytics
def get_workload():
    try:
        r = requests.get(f"{API_BASE_URL}/analytics/workload")
        if r.status_code == 200:
            return r.json()
        else:
            return []
    except:
        return []

tab1, tab2, tab3 = st.tabs(["Create New Plan", "Evaluate Existing Plan", "Workload Dashboard"])

# =============================================
# TAB 1 — Create New Plan (POST /semesterplans)
# =============================================
with tab1:
    st.subheader("Create a New Semester Plan")

    with st.expander("New Plan Form", expanded=True):
        with st.form("new_plan_form"):
            plan_name = st.text_input(
                "Plan Name:",
                placeholder="e.g. Fall 2026 - Junior CS"
            )

            col1, col2 = st.columns(2)
            s_id = col1.number_input(
                "Student ID (optional, 0 for template):",
                min_value=0, max_value=500, value=1
            )
            a_id = col2.number_input(
                "Advisor ID:",
                min_value=1, max_value=100, value=1
            )

            create_btn = st.form_submit_button("Create Plan")

            if create_btn:
                if not plan_name.strip():
                    st.warning("Please enter a plan name.")
                else:
                    # Packaging plan info
                    payload = {
                        "plan_name": plan_name,
                        "advisor_id": a_id
                    }
                    if s_id > 0:
                        payload["student_id"] = s_id

                    res = requests.post(f"{API_BASE_URL}/semesterplans", json=payload)
                    if res.status_code in [200, 201]:
                        data = res.json()
                        st.success(f"Plan created! New Plan ID: {data.get('plan_id')}")
                        st.balloons()
                    else:
                        st.error(f"Error from API: {res.text}")

# =============================================
# TAB 2 — Evaluate Existing Plan (GET / POST / DELETE)
# =============================================
with tab2:
    st.subheader("Evaluate an Existing Plan")

    with st.expander("Load a Plan", expanded=True):
        with st.form("load_plan_form"):
            pid_input = st.number_input(
                "Enter Plan ID:",
                min_value=1, max_value=500, value=1
            )
            load_btn = st.form_submit_button("Load Plan")

            if load_btn:
                st.session_state["loaded_plan_id"] = pid_input

    # Once a plan is loaded, show its details
    if "loaded_plan_id" in st.session_state:
        pid = st.session_state["loaded_plan_id"]
        plan = get_plan(pid)

        if plan:
            st.divider()

            with st.container(border=True):
                st.write(f"### {plan.get('plan_name')} (ID: {pid})")
                st.caption(
                    f"Student ID: {plan.get('student_id', 'N/A')} | "
                    f"Advisor ID: {plan.get('advisor_id', 'N/A')}"
                )

                st.divider()

                # Summary metrics
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total Courses", plan.get("total_courses", 0))
                m2.metric("Total Credits", plan.get("total_credits", 0))
                m3.metric("Avg Difficulty", f"{plan.get('avg_difficulty') or 0:.2f}/5")
                m4.metric("Weekly Hours", f"{plan.get('total_avg_weekly_hours') or 0:.1f}")

                # Balanced or not
                if plan.get("is_manageable"):
                    st.success("This plan looks manageable — workload is within a healthy range.")
                else:
                    warning_msg = plan.get("warning") or "Workload might be too high."
                    st.warning(f"Warning: {warning_msg}")

            # Courses in this plan
            st.divider()
            st.subheader("Courses in this Plan")

            plan_courses = plan.get("courses", [])

            if plan_courses:
                for c in plan_courses:
                    with st.container(border=True):
                        st.write(f"### {c.get('course_code')} - {c.get('course_name')}")
                        st.caption(f"📚 Credits: {c.get('credits', 0)}")

                        st.divider()

                        s1, s2, s3 = st.columns(3)
                        s1.metric("Difficulty", f"{c.get('avg_difficulty') or 'N/A'}")
                        s2.metric("Workload", f"{c.get('avg_workload') or 'N/A'}")
                        s3.metric("Weekly Hrs", f"{c.get('avg_weekly_hours') or 'N/A'}")

                        rm_col, _ = st.columns([1, 4])

                        # Delete course from plan (DELETE)
                        if rm_col.button("Remove", key=f"rm_{c.get('course_id')}_{pid}"):
                            del_res = requests.delete(
                                f"{API_BASE_URL}/semesterplans/{pid}/courses/{c.get('course_id')}"
                            )
                            if del_res.status_code == 200:
                                st.toast("Course removed!")
                                st.rerun()
                            else:
                                st.error(f"Error from API: {del_res.text}")
            else:
                st.info("No courses in this plan yet. Add one below.")

            # Add a course (POST)
            st.divider()
            st.subheader("Add a Course to this Plan")

            with st.form(f"add_course_form_{pid}"):
                course_id_to_add = st.number_input(
                    "Course ID to add:",
                    min_value=1, max_value=500, value=1
                )
                add_btn = st.form_submit_button("Add Course")

                if add_btn:
                    add_res = requests.post(
                        f"{API_BASE_URL}/semesterplans/{pid}/courses/{course_id_to_add}"
                    )
                    if add_res.status_code in [200, 201]:
                        st.success(f"Course {course_id_to_add} added!")
                        st.rerun()
                    elif add_res.status_code == 409:
                        st.warning("That course is already in this plan.")
                    else:
                        st.error(f"Error from API: {add_res.text}")

            # Delete the entire plan (DELETE)
            st.divider()
            st.subheader("Danger Zone")

            if st.button("Delete This Entire Plan", key=f"del_plan_{pid}"):
                del_plan_res = requests.delete(f"{API_BASE_URL}/semesterplans/{pid}")
                if del_plan_res.status_code == 200:
                    st.toast(f"Plan {pid} deleted!")
                    del st.session_state["loaded_plan_id"]
                    st.rerun()
                else:
                    st.error(f"Error from API: {del_plan_res.text}")
        else:
            st.error(f"Plan {pid} not found.")

# =============================================
# TAB 3 — Workload Dashboard (US 6)
# =============================================
with tab3:
    st.subheader("Workload Dashboard — All Courses")
    st.caption("See which courses are heaviest across the whole catalog.")

    workload = get_workload()

    if workload:
        df = pd.DataFrame(workload)

        st.write("### Top 10 Heaviest Workload Courses")
        top10 = df.head(10)
        st.dataframe(
            top10[["course_code", "course_name", "avg_difficulty",
                   "avg_workload", "avg_weekly_hours", "review_count"]].rename(columns={
                "course_code": "Code",
                "course_name": "Name",
                "avg_difficulty": "Difficulty",
                "avg_workload": "Workload",
                "avg_weekly_hours": "Weekly Hrs",
                "review_count": "# Reviews"
            }),
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.write("### Workload Distribution (Top 15)")
        top15 = df.head(15).set_index("course_code")[["avg_workload", "avg_difficulty"]]
        st.bar_chart(top15)
    else:
        st.info("No workload data available yet.")