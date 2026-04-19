import streamlit as st
from modules.nav import SideBarLinks

SideBarLinks()

st.title(f'Welcome, {st.session_state.get("first_name", "Advisor")}!')
st.write('What would you like to do today?')

# TODO: add navigation cards or buttons to advisor feature pages
