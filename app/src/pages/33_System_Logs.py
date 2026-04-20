import streamlit as st
import requests
from modules.nav import SideBarLinks

SideBarLinks()

API_BASE_URL = "http://web-api:4000/"

st.title('System Logs')
st.write("Monitor platform performance and system activity.")

# TODO: implement (Barry user stories 2 & 6)
# - Monitor system performance logs
# - View platform metrics by severity

def safe_get(path):
    try:
        r = requests.get(f"{API_BASE_URL}{path}", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"GET {path} failed: {e}")
        return None
 
 
logs = safe_get("/systemlogs")
 
if logs is None:
    st.warning("Could not reach the API.")
    st.stop()
 
if not logs:
    st.info("No system logs found.")
    st.stop()
 
severities = ["INFO", "WARNING", "ERROR"]
cols = st.columns(len(severities))
for col, level in zip(cols, severities):
    count = sum(1 for l in logs if l.get("severity", "").upper() == level)
    col.metric(level, count)
 
severity_filter = st.selectbox(
    "Filter by severity",
    options=["all"] + severities,
)
 
if severity_filter != "all":
    logs = [l for l in logs if l.get("severity", "").upper() == severity_filter]
 
logs = sorted(logs, key=lambda l: l.get("timestamp", ""), reverse=True)
 
st.write(f"Showing {len(logs)} log(s).")
 
for log in logs:
    with st.container(border=True):
        st.write(
            f"Log #{log.get('log_id')} | "
            f"Admin: {log.get('admin_id')} | "
            f"Severity: {log.get('severity', 'N/A')} | "
            f"Time: {log.get('timestamp', 'N/A')}"
        )
        st.write(log.get("message", "No message."))