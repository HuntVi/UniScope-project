import streamlit as st
import requests
from modules.nav import SideBarLinks

SideBarLinks()

API_BASE_URL = "http://api:4000"
st.title('Review Moderation')
st.write("Approve or reject student course reviews.")

# TODO: implement (Barry user stories 1 & 4)
# - Approve or reject review entries
# - Detect and flag inconsistent review data

def safe_get(path):
    try:
        r = requests.get(f"{API_BASE_URL}{path}", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"GET {path} failed: {e}")
        return None
 
 
def update_review_status(review_id, new_status):
    try:
        r = requests.put(
            f"{API_BASE_URL}/reviews/{review_id}",
            json={"status": new_status},
            timeout=5,
        )
        r.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Could not update review {review_id}: {e}")
        return False
 
 
def post_flag(review_id, reason):
    try:
        r = requests.post(
            f"{API_BASE_URL}/flags",
            json={
                "review_id": review_id,
                "reporter_id": st.session_state.get("user_id", 1),
                "reason": reason,
            },
            timeout=5,
        )
        r.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Could not create flag for review {review_id}: {e}")
        return False
 
 
def is_inconsistent(review):
    score_fields = [
        "difficulty_score", "workload_score", "clarity_score",
        "satisfaction_score", "fairness_score",
    ]
    for field in score_fields:
        val = review.get(field)
        if val is not None and not (1 <= int(val) <= 5):
            return f"{field} = {val} is out of range (1-5)"
    hours = review.get("weekly_hours")
    if hours is not None and float(hours) < 0:
        return f"weekly_hours = {hours} is negative"
    return None
 
 
status_filter = st.selectbox(
    "Filter by status",
    options=["all", "approved", "pending", "rejected"],
)
 
show_inconsistent_only = st.checkbox("Show inconsistent data only", value=False)
 
reviews = safe_get("/reviews")
 
if reviews is None:
    st.warning("Could not reach the API.")
    st.stop()
 
if not reviews:
    st.info("No reviews found.")
    st.stop()
 
if status_filter != "all":
    reviews = [r for r in reviews if r.get("status", "approved") == status_filter]
 
if show_inconsistent_only:
    reviews = [r for r in reviews if is_inconsistent(r)]
 
st.write(f"Showing {len(reviews)} review(s).")
 
for review in reviews:
    rid = review.get("review_id")
    status = review.get("status", "approved")
    bad_reason = is_inconsistent(review)
 
    with st.container(border=True):
        st.write(
            f"Review #{rid} | Student: {review.get('student_id')} | "
            f"Offering: {review.get('offering_id')} | "
            f"Date: {review.get('review_date', 'N/A')} | "
            f"Status: {status}"
        )
 
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("Difficulty",   review.get("difficulty_score",  "-"))
        col2.metric("Workload",     review.get("workload_score",     "-"))
        col3.metric("Clarity",      review.get("clarity_score",      "-"))
        col4.metric("Satisfaction", review.get("satisfaction_score", "-"))
        col5.metric("Fairness",     review.get("fairness_score",     "-"))
        col6.metric("Hrs/week",     review.get("weekly_hours",       "-"))
 
        if review.get("comment_text"):
            st.write(review["comment_text"])
 
        if bad_reason:
            st.warning(f"Inconsistent data: {bad_reason}")
 
        bcol1, bcol2, bcol3 = st.columns([1, 1, 1])
 
        with bcol1:
            if st.button("Approve", key=f"approve_{rid}"):
                if update_review_status(rid, "approved"):
                    st.success(f"Review #{rid} approved.")
                    st.rerun()
 
        with bcol2:
            if st.button("Reject", key=f"reject_{rid}"):
                if update_review_status(rid, "rejected"):
                    st.success(f"Review #{rid} rejected.")
                    st.rerun()
 
        with bcol3:
            if st.button("Flag", key=f"flag_{rid}"):
                reason = bad_reason or "Manually flagged by admin"
                if post_flag(rid, reason):
                    st.success(f"Review #{rid} flagged.")
                    st.rerun()