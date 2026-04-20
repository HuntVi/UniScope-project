import streamlit as st
import requests
from modules.nav import SideBarLinks

SideBarLinks()

API_BASE_URL = "https://localhost:4000"

st.title(f'Welcome, {st.session_state.get("first_name", "Admin")}!')
st.write('What would you like to do today?')
st.divider()

def safe_get(path: str):
    """Return JSON list/dict on success, or None on any error."""
    try:
        r = requests.get(f"{API_BASE_URL}{path}", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None
    

reviews  = safe_get("/reviews")         
flags    = safe_get("/flags")            
syslogs  = safe_get("/systemlogs")


st.subheader("Platform Overview")
 
col1, col2, col3, col4 = st.columns(4)

if reviews is not None:
    pending_reviews = [r for r in reviews if r.get("status", "approved") != "approved"]
    col1.metric("Pending Reviews", len(pending_reviews))
else:
    col1.metric("Pending Reviews", "—")

if flags is not None:
    unresolved = [f for f in flags if not f.get("resolved_at")]
    col2.metric("Unresolved Flags", len(unresolved))
else:
    col2.metric("Unresolved Flags", "—")
 
# Total system log entries
if syslogs is not None:
    col3.metric("Total Log Entries", len(syslogs))
else:
    col3.metric("Total Log Entries", "—")
 
# Error-level log entries
if syslogs is not None:
    errors = [l for l in syslogs if l.get("severity", "").upper() == "ERROR"]
    col4.metric("Error Logs", len(errors))
else:
    col4.metric("Error Logs", "—")
 
st.divider()
 

st.subheader("Unresolved Flags")
 
if flags is None:
    st.warning("Could not reach the API. Check that the backend is running.")
elif not flags:
    st.info("No flags found.")
else:
    unresolved = [f for f in flags if not f.get("resolved_at")]
    if not unresolved:
        st.success("All flags have been resolved.")
    else:
        st.dataframe(
            unresolved,
            use_container_width=True,
            column_order=["flag_id", "review_id", "reporter_id", "reason", "created_at"],
        )
 
st.divider()
 
 
st.subheader(" Recent System Logs")
 
if syslogs is None:
    st.warning("Could not reach the API. Check that the backend is running.")
elif not syslogs:
    st.info("No system logs found.")
else:
    # Show the 10 most recent entries
    recent = sorted(syslogs, key=lambda l: l.get("timestamp", ""), reverse=True)[:10]
 
    for log in recent:
        severity = log.get("severity", "INFO").upper()
        icon = {"INFO": "info", "WARNING": "warning", "ERROR": "error "}.get(severity, "📋")
        with st.expander(
            f"{icon} [{severity}]  {log.get('timestamp', 'N/A')}  —  "
            f"{str(log.get('message', ''))[:80]}"
        ):
            st.json(log)
 
st.divider()


 
# ── Buttons ───────────────────────────────────────────────────────
st.subheader(" Quick Actions")
 
col_a, col_b, col_c = st.columns(3)
 
with col_a:
    if st.button("Review Moderation", use_container_width=True):
        st.switch_page("pages/31_Review_Moderation.py")
 
with col_b:
    if st.button(" Manage Flags", use_container_width=True):
        st.switch_page("pages/32_Manage_Flags.py")
 
with col_c:
    if st.button("System Logs", use_container_width=True):
        st.switch_page("pages/33_System_Logs.py")
 