"""Paddy Burnt-Area Intelligence: the dashboard.

Run from the project folder:  streamlit run dashboard/app.py
The look (colours, fonts) is set in .streamlit/config.toml; the fonts and the logo are in dashboard/static/.
"""
import streamlit as st

import common as c

st.set_page_config(page_title='Paddy Burnt-Area Intelligence', page_icon=str(c.STATIC / 'mark.svg'), layout='wide')
try:
    st.logo(str(c.STATIC / 'logo.svg'), size='large', icon_image=str(c.STATIC / 'mark.svg'))
except TypeError:              # older Streamlit, before the logo had sizes
    st.logo(str(c.STATIC / 'logo.svg'), icon_image=str(c.STATIC / 'mark.svg'))
c.style()
st.navigation([
    st.Page('overview.py', title='Overview', icon=':material/space_dashboard:', default=True),
    st.Page('views/1_Mission_Explorer.py', title='Mission Explorer', icon=':material/satellite_alt:'),
    st.Page('views/2_Indian_Startup_Landscape.py', title='Indian Startup Landscape', icon=':material/rocket_launch:'),
    st.Page('views/3_EO_Analysis.py', title='EO Analysis', icon=':material/local_fire_department:'),
    st.Page('views/4_Mission_Trade-offs.py', title='Mission Trade-offs', icon=':material/balance:'),
    st.Page('views/5_Commercial_Opportunity.py', title='Commercial Opportunity', icon=':material/agriculture:'),
]).run()
