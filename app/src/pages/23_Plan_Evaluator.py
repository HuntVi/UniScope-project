import streamlit as st
import requests
from modules.nav import SideBarLinks

SideBarLinks()

API_BASE_URL = "http://web-api:4000"

# ========================================================
# Semester Plan Evaluator Page
# Covers Muhammad's User Stories 3 & 6:
# 3. Evaluate whether a semester plan is balanced and sustainable
# 6. Dashboard of difficulty/workload across courses and levels
#
# Uses POST /semesterplans (create plan)
#      DELETE /semesterplans/{id} (delete plan)
#      POST /semesterplans/{id}/courses/{cid} (add course)
#      DELETE /semesterplans/{id}/courses/{cid} (remove course)
#      GET /semesterplans/{id} (view plan details)
#      GET /analytics/workload (workload dashboard)
# ========================================================
st.title('📋 Semester Plan Evaluator')
st.write(
    "Create and evaluate semester plans for your students. "
    "Check whether a plan is balanced based on difficulty, workload, and weekly hours."
)

# --- Tabs for different features ---
tab1, tab2, tab3 = st.tabs([
    "➕ Create New Plan",
    "🔍 Evaluate Existing Plan",
    "📊 Workload Dashboard"
])

# =============================================
# TAB 1 — Create New Plan (POST)
# =============================================
with tab1:
    st.subheader("Create a New Semester Plan")
    st.caption("Uses POST /semesterplans")

    with st.form("create_plan_form"):
        plan_name = st.text_input(
            "Plan name",
            placeholder="e.g. Fall 2026 - Junior CS"
        )
        student_id = st.number_input(
            "Student ID (optional)",
            min_value=0, max_value=500, value=1,
            help="Leave 0 if this is a generic template plan."
        )
        advisor_id = st.number_input(
            "Advisor ID",
            min_value=1, max_value=100, value=1,
            help="Your advisor ID (Muhammad)."
        )
        submit = st.form_submit_button("Create Plan", type="primary")

        if submit:
            if not plan_name.strip():
                st.warning("Please enter a plan name.")
            else:
                payload = {
                    "plan_name": plan_name,
                    "advisor_id": advisor_id
                }
                if student_id > 0:
                    payload["student_id"] = student_id

                try:
                    resp = requests.post(f"{API_BASE_URL}/semesterplans", json=payload)
                    if resp.status_code in (200, 201):
                        data = resp.json()
                        st.success(f"✅ Plan created! New Plan ID: **{data.get('plan_id')}**")
                        st.balloons()
                        st.info("Switch to the 'Evaluate Existing Plan' tab to add courses.")
                    else:
                        st.error(f"Error: {resp.status_code} — {resp.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

# =============================================
# TAB 2 — Evaluate Existing Plan (GET / POST / DELETE)
# =============================================
with tab2:
    st.subheader("Evaluate an Existing Plan")
    st.caption("Uses GET /semesterplans/{id}, POST and DELETE for courses")

    plan_id = st.number_input(
        "Enter Plan ID",
        min_value=1, max_value=500, value=1,
        key="eval_plan_id"
    )

    if st.button("Load Plan", key="load_plan_btn"):
        st.session_state['loaded_plan_id'] = plan_id

    if 'loaded_plan_id' in st.session_state:
        pid = st.session_state['loaded_plan_id']
        try:
            resp = requests.get(f"{API_BASE_URL}/semesterplans/{pid}")

            if resp.status_code == 200:
                plan = resp.json()

                # --- Plan header ---
                st.success(f"Loaded: **{plan.get('plan_name')}** (ID: {pid})")

                # --- Summary metrics ---
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total Courses", plan.get('total_courses', 0))
                m2.metric("Total Credits", plan.get('total_credits', 0))
                m3.metric("Avg Difficulty", f"{plan.get('avg_difficulty') or 0:.2f}/5")
                m4.metric("Weekly Hours", f"{plan.get('total_avg_weekly_hours') or 0:.1f}")

                # --- Manageable flag ---
                if plan.get('is_manageable'):
                    st.success("✅ This plan looks **manageable** — workload is within healthy range.")
                else:
                    warning_msg = plan.get('warning') or "Workload might be too high."
                    st.warning(f"⚠️ **Warning:** {warning_msg}")

                st.divider()

                # --- Courses in this plan ---
                st.subheader("📚 Courses in this Plan")
                courses = plan.get('courses', [])

                if courses:
                    for c in courses:
                        with st.container(border=True):
                            cc1, cc2 = st.columns([4, 1])
                            with cc1:
                                st.write(
                                    f"**{c.get('course_code')}** — {c.get('course_name')} "
                                    f"({c.get('credits', 0)} credits)"
                                )
                                st.caption(
                                    f"Difficulty: {c.get('avg_difficulty') or 'N/A'} | "
                                    f"Workload: {c.get('avg_workload') or 'N/A'} | "
                                    f"Weekly hrs: {c.get('avg_weekly_hours') or 'N/A'}"
                                )
                            with cc2:
                                # --- DELETE course from plan ---
                                if st.button(
                                    "🗑️ Remove",
                                    key=f"rm_{c.get('course_id')}_{pid}"
                                ):
                                    del_resp = requests.delete(
                                        f"{API_BASE_URL}/semesterplans/{pid}/courses/{c.get('course_id')}"
                                    )
                                    if del_resp.status_code == 200:
                                        st.toast("Course removed!")
                                        st.rerun()
                                    else:
                                        st.error(f"Error: {del_resp.text}")
                else:
                    st.info("No courses in this plan yet. Add one below!")

                st.divider()

                # --- Add course to plan (POST) ---
                st.subheader("➕ Add a Course to this Plan")
                with st.form(f"add_course_form_{pid}"):
                    course_id_to_add = st.number_input(
                        "Course ID to add",
                        min_value=1, max_value=500, value=1
                    )
                    add_btn = st.form_submit_button("Add Course")
                    if add_btn:
                        add_resp = requests.post(
                            f"{API_BASE_URL}/semesterplans/{pid}/courses/{course_id_to_add}"
                        )
                        if add_resp.status_code in (200, 201):
                            st.success(f"✅ Course {course_id_to_add} added!")
                            st.rerun()
                        elif add_resp.status_code == 409:
                            st.warning("That course is already in this plan.")
                        else:
                            st.error(f"Error: {add_resp.text}")

                st.divider()

                # --- DELETE entire plan ---
                st.subheader("🗑️ Danger Zone")
                if st.button("Delete This Entire Plan", type="secondary", key=f"del_plan_{pid}"):
                    del_plan_resp = requests.delete(f"{API_BASE_URL}/semesterplans/{pid}")
                    if del_plan_resp.status_code == 200:
                        st.success(f"Plan {pid} deleted.")
                        del st.session_state['loaded_plan_id']
                        st.rerun()
                    else:
                        st.error(f"Error: {del_plan_resp.text}")

            elif resp.status_code == 404:
                st.error(f"Plan {pid} not found.")
            else:
                st.error(f"Error loading plan: {resp.status_code}")

        except Exception as e:
            st.error(f"Connection error: {e}")

# =============================================
# TAB 3 — Workload Dashboard (US 6)
# =============================================
with tab3:
    st.subheader("📊 Workload Dashboard — All Courses")
    st.caption("User Story 6: Dashboard of difficulty/workload across courses")

    try:
        resp = requests.get(f"{API_BASE_URL}/analytics/workload")
        if resp.status_code == 200:
            data = resp.json()
            if data:
                import pandas as pd
                df = pd.DataFrame(data)

                # Top 10 heaviest courses
                st.write("### 🔥 Top 10 Heaviest Workload Courses")
                top10 = df.head(10)
                st.dataframe(
                    top10[['course_code', 'course_name', 'avg_difficulty',
                           'avg_workload', 'avg_weekly_hours', 'review_count']],
                    use_container_width=True, hide_index=True
                )

                st.divider()

                # Chart
                st.write("### 📈 Workload Distribution (Top 15)")
                top15 = df.head(15).set_index('course_code')[['avg_workload', 'avg_difficulty']]
                st.bar_chart(top15)
            else:
                st.info("No workload data available yet.")
        else:
            st.error(f"Error: {resp.status_code}")
    except Exception as e:
        st.error(f"Connection error: {e}")