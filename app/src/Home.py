import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

st.session_state['authenticated'] = False

SideBarLinks(show_home=True)

logger.info('Loading UniScope Home page')

st.title('UniScope')
st.write('#### A data-driven course review platform for Northeastern students.')
st.write('---')
st.write('### Who are you?')

if st.button('Act as Jason (Student)', type='primary', use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'student'
    st.session_state['first_name'] = 'Jason'
    logger.info('Logging in as Student')
    st.switch_page('pages/00_Student_Home.py')

if st.button('Act as Josh (Professor)', type='primary', use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'professor'
    st.session_state['first_name'] = 'Josh'
    logger.info('Logging in as Professor')
    st.switch_page('pages/10_Professor_Home.py')

if st.button('Act as Muhammad (Academic Advisor)', type='primary', use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'advisor'
    st.session_state['first_name'] = 'Muhammad'
    logger.info('Logging in as Academic Advisor')
    st.switch_page('pages/20_Advisor_Home.py')

if st.button('Act as Barry (System Admin)', type='primary', use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'admin'
    st.session_state['first_name'] = 'Barry'
    logger.info('Logging in as System Admin')
    st.switch_page('pages/30_Admin_Home.py')
