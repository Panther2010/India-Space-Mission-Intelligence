"""Paddy Burnt-Area Intelligence: the dashboard.

Run from the project folder:  streamlit run dashboard/app.py
The look (colours, fonts) is set in .streamlit/config.toml; the fonts and the logo are in dashboard/static/.
"""
import streamlit as st

import common as c

st.set_page_config(page_title='Paddy Burnt-Area Intelligence', page_icon=str(c.STATIC / 'mark.svg'), layout='wide')
try:
    st.logo(str(c.STATIC / 'logo.svg'), size='medium')
except TypeError:              # older Streamlit, before the logo had sizes
    st.logo(str(c.STATIC / 'logo.svg'))
c.style()
# Short names, so the logo and all six fit in the top bar; each page's header gives its full name.
PAGES = [
    st.Page('overview.py', title='Overview', icon=':material/space_dashboard:', default=True),
    st.Page('views/1_Mission_Explorer.py', title='Missions', icon=':material/satellite_alt:'),
    st.Page('views/2_Indian_Startup_Landscape.py', title='Startups', icon=':material/rocket_launch:'),
    st.Page('views/3_EO_Analysis.py', title='EO Analysis', icon=':material/local_fire_department:'),
    st.Page('views/4_Mission_Trade-offs.py', title='Trade-offs', icon=':material/balance:'),
    st.Page('views/5_Commercial_Opportunity.py', title='Opportunity', icon=':material/agriculture:'),
]
try:
    page = st.navigation(PAGES, position='top')
except TypeError:              # older Streamlit: navigation in the sidebar
    page = st.navigation(PAGES)
page.run()
