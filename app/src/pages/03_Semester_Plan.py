import streamlit as st
import requests
from modules.nav import SideBarLinks
from datetime import datetime


SideBarLinks()


st.title('My Semester Plans')


# TODO: implement (Jason user story 6)
# - Create, adjust, delete semester plans
# - View course difficulty/workload/satisfaction while planning
API_BASE_URL = "http://web-api:4000"


# Getter
def get_data(endpoint):
   try:
       r = requests.get(f"{API_BASE_URL}/{endpoint}")
       if r.status_code == 200:
           return r.json()
       else:
           return []
   except:
       return []
  
courses = get_data("courses")
reviews = get_data("reviews")


# Initialize editing smester plan id
if 'editing_plan_id' not in st.session_state:
    st.session_state['editing_plan_id'] = None

# 1.6 Create semester plan
if len(courses) > 0:
    course_options = {f"{c['course_code']} - {c['course_name']}": c for c in courses}
    
    with st.expander("Create New Semester Plan", expanded=True):
        with st.form("plan_form"):
            plan_name = st.text_input("Plan Name:", placeholder="e.g., My Freshman Fall")
            col_1, col_2 = st.columns(2)
            plan_sem = col_1.selectbox("Target Semester:", ["Fall", "Spring", "Summer"])
            plan_yr = col_2.number_input("Target Year:", 2024, 2030, value=datetime.now().year)

            selected_labels = st.multiselect(
                "Select Courses to Add:",
                options=list(course_options.keys()),
                help="View the calculated impact below before submitting."
            )

            # 1.6 Dynamic feedback for student to view of their selected courses
            if selected_labels:
                selected_courses = [course_options[label] for label in selected_labels]
                selected_codes = [c['course_code'] for c in selected_courses]
                
                # Get rid of 'rejected' course reviews
                relevant_reviews = [
                    r for r in reviews 
                    if r.get('course_code') in selected_codes and r.get('status') != 'rejected'
                ]

                if relevant_reviews:
                    course_stats = {}
                    for r in relevant_reviews:
                        code = r.get('course_code')
                        if code not in course_stats:
                            course_stats[code] = {'diff': [], 'work': [], 'sat': []}
                        course_stats[code]['diff'].append(r.get('difficulty_score', 0))
                        course_stats[code]['work'].append(r.get('workload_score', 0))
                        course_stats[code]['sat'].append(r.get('satisfaction_score', 0))

                    course_diff_avgs = [round(sum(s['diff'])/len(s['diff']), 2) for s in course_stats.values() if s['diff']]
                    course_work_avgs = [round(sum(s['work'])/len(s['work']), 2) for s in course_stats.values() if s['work']]
                    course_sat_avgs  = [round(sum(s['sat'])/len(s['sat']), 2) for s in course_stats.values() if s['sat']]

                    avg_diff = sum(course_diff_avgs) / len(course_diff_avgs) if course_diff_avgs else 0
                    avg_work = sum(course_work_avgs) / len(course_work_avgs) if course_work_avgs else 0
                    avg_sat  = sum(course_sat_avgs) / len(course_sat_avgs) if course_sat_avgs else 0

                    st.write("Plan Overview (Strict Estimation)")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Avg. Difficulty", f"{avg_diff:.1f}")
                    m2.metric("Avg. Workload", f"{avg_work:.1f}")
                    m3.metric("Avg. Satisfaction", f"{avg_sat:.1f}")
                else:
                    st.info("No approved review data found for these courses.")
                
                st.write(f"You have selected {len(selected_courses)} courses.")

            submit_plan = st.form_submit_button("Save Semester Plan")

            if submit_plan:
                if not plan_name or not selected_labels:
                    st.warning("Please provide a plan name and select at least one course.")
                else:
                    # Creating plan
                    payload = {
                        "student_id": 1, 
                        "plan_name": plan_name,
                        "advisor_id": 1 # Test purpose
                    }

                    res = requests.post(f"{API_BASE_URL}/semesterplans", json=payload)

                    if res.status_code in [200, 201]:
                        new_plan = res.json()
                        new_plan_id = new_plan['plan_id']
                        
                        # Adding selected course one by one
                        selected_course_ids = [course_options[l]['course_id'] for l in selected_labels]
                        
                        success_count = 0
                        for c_id in selected_course_ids:
                            add_res = requests.post(f"{API_BASE_URL}/semesterplans/{new_plan_id}/courses/{c_id}")
                            if add_res.status_code in [200, 201]:
                                success_count += 1
                        
                        if success_count == len(selected_course_ids):
                            st.success(f"Plan '{plan_name}' created with {success_count} courses!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.warning(f"Plan created, but only {success_count}/{len(selected_course_ids)} courses were added.")
                    else:
                        st.error(f"Failed to create plan: {res.text}")


st.divider()
st.subheader("Saved Plans")

student_id = 1
all_plans_basic = get_data(f"students/{student_id}/semesterplans")

st.write(f"Found {len(all_plans_basic)} plans for Student {student_id}")

if all_plans_basic:
    for p_basic in all_plans_basic:
        # Get selected courses info
        p = get_data(f"semesterplans/{p_basic['plan_id']}")
        
        if not p:
            continue

        is_editing = (st.session_state['editing_plan_id'] == p['plan_id'])
          
        with st.container(border=True):
            if is_editing:
                # 1.6 Edit
                st.write(f"Editing: {p['plan_name']}")
                new_n = st.text_input("New Name:", value=p['plan_name'], key=f"en_{p['plan_id']}")
                  
                cur_labels = [f"{c['course_code']} - {c['course_name']}" for c in p.get('courses', [])]
                new_l = st.multiselect("Adjust Courses:", options=list(course_options.keys()), default=cur_labels, key=f"ms_{p['plan_id']}")
                  
                save_col, cancel_col, _ = st.columns([1, 1, 4])
                
                if save_col.button("Save", key=f"sv_{p['plan_id']}"):
                    with st.spinner("Updating courses..."):
                        # --- Step 1: Clear existing courses (清空当前课程) ---
                        # 路径: DELETE /semesterplans/{planID}/courses/{courseID}
                        if 'courses' in p and p['courses']:
                            for old_c in p['courses']:
                                delete_url = f"{API_BASE_URL}/semesterplans/{p['plan_id']}/courses/{old_c['course_id']}"
                                requests.delete(delete_url)

                        # --- Step 2: Add new selection (添加新选中的课程) ---
                        # 路径: POST /semesterplans/{planID}/courses/{courseID}
                        new_course_ids = [course_options[l]['course_id'] for l in new_l]
                        
                        success_count = 0
                        for c_id in new_course_ids:
                            add_url = f"{API_BASE_URL}/semesterplans/{p['plan_id']}/courses/{c_id}"
                            add_res = requests.post(add_url)
                            if add_res.status_code in [200, 201]:
                                success_count += 1

                        # --- Step 3: Final Check & Rerun (最终检查与刷新) ---
                        if success_count == len(new_course_ids):
                            st.toast(f"Plan updated! {success_count} courses synced.")
                            # 必须重置 editing_plan_id 才能退出编辑界面
                            st.session_state['editing_plan_id'] = None
                            st.rerun()
                        else:
                            st.error(f"Sync issue: only {success_count}/{len(new_course_ids)} courses saved.")

                if cancel_col.button("Cancel", key=f"cl_{p['plan_id']}"):
                    st.session_state['editing_plan_id'] = None
                    st.rerun()
          
            else:
                st.write(f"{p['plan_name']}")
                
                # Display course number and toal credit hours
                st.caption(f"Total Courses: {p.get('total_courses', 0)} | Total Credits: {p.get('total_credits', 0)}")
                st.divider()

                # Average score
                m1, m2, m3 = st.columns(3)
                m1.metric("Avg. Difficulty", f"{(p.get('avg_difficulty') or 0):.1f}")
                m2.metric("Avg. Workload", f"{(p.get('avg_workload') or 0):.1f}")
                m3.metric("Avg. Satisfaction", f"{(p.get('avg_satisfaction') or 0):.1f}")

                # Show courses lists
                if 'courses' in p and p['courses']:
                    st.write("**Included Courses:**")
                    for c_item in p['courses']:
                        st.markdown(f"- **{c_item.get('course_code', 'N/A')}**: {c_item.get('course_name', 'N/A')}")

                st.write("")
                edit_col, del_col, _ = st.columns([1, 1, 4])
                
                if edit_col.button("Edit", key=f"ed_{p['plan_id']}"):
                    st.session_state['editing_plan_id'] = p['plan_id']
                    st.rerun()

                if del_col.button("Delete", key=f"dl_{p['plan_id']}"):
                    del_res = requests.delete(f"{API_BASE_URL}/semesterplans/{p['plan_id']}")
                    if del_res.status_code == 200:
                        st.toast(f"Plan deleted!")
                        st.rerun()
                      
else:
    st.info("You haven't created any plans yet.")