"""Paddy Burnt-Area Intelligence: the dashboard.

Run from the project folder:  streamlit run dashboard/app.py
"""
import streamlit as st

st.set_page_config(page_title='Paddy Burnt-Area Intelligence', page_icon='🛰️', layout='wide')
st.navigation([
    st.Page('overview.py', title='Overview', icon='🏠', default=True),
    st.Page('views/1_Mission_Explorer.py', title='Mission Explorer', icon='🛰️'),
    st.Page('views/2_Indian_Startup_Landscape.py', title='Indian Startup Landscape', icon='🚀'),
    st.Page('views/3_EO_Analysis.py', title='EO Analysis', icon='🔥'),
    st.Page('views/4_Mission_Trade-offs.py', title='Mission Trade-offs', icon='⚖️'),
    st.Page('views/5_Commercial_Opportunity.py', title='Commercial Opportunity', icon='💼'),
]).run()
