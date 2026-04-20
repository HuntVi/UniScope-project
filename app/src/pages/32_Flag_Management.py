import streamlit as st
import requests
from modules.nav import SideBarLinks

SideBarLinks()

API_BASE_URL = "http://web-api:4000/"

st.title('Flag Management')
st.write("View and resolve flagged course reviews.")

# TODO: implement (Barry user stories 3 & 5)
# - View unresolved flags/reports
# - Resolve flagged items
def safe_get(path):
    try:
        r = requests.get(f"{API_BASE_URL}{path}", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"GET {path} failed: {e}")
        return None
 
 
def resolve_flag(flag_id):
    try:
        r = requests.put(
            f"{API_BASE_URL}/flags/{flag_id}",
            json={
                "resolved_by_admin_id": st.session_state.get("user_id", 1),
            },
            timeout=5,
        )
        r.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Could not resolve flag {flag_id}: {e}")
        return False
 
 
show_resolved = st.checkbox("Show resolved flags", value=False)
 
flags = safe_get("/flags")
 
if flags is None:
    st.warning("Could not reach the API.")
    st.stop()
 
if not flags:
    st.info("No flags found.")
    st.stop()
 
if not show_resolved:
    flags = [f for f in flags if not f.get("resolved_at")]
 
st.write(f"Showing {len(flags)} flag(s).")
 
for flag in flags:
    fid = flag.get("flag_id")
    resolved = flag.get("resolved_at")
 
    with st.container(border=True):
        st.write(
            f"Flag #{fid} | Review: {flag.get('review_id')} | "
            f"Reported by: {flag.get('reporter_id')} | "
            f"Created: {flag.get('created_at', 'N/A')}"
        )
 
        st.write(f"Reason: {flag.get('reason', 'No reason provided')}")
 
        if resolved:
            st.write(
                f"Resolved by admin {flag.get('resolved_by_admin_id')} "
                f"at {resolved}"
            )
        else:
            if st.button("Resolve", key=f"resolve_{fid}"):
                if resolve_flag(fid):
                    st.success(f"Flag #{fid} marked as resolved.")
                    st.rerun()