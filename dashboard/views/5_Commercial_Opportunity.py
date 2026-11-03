"""Commercial Opportunity: the user, the decision, the pain point and how the product would be tested."""
import pandas as pd
import streamlit as st

import common as c

st.title('Commercial Opportunity')

s25 = c.summary(2025)
by_window = c.csv(c.PROCESSED / 's2_burn_by_window_sangrur_2025.csv')

st.subheader('What the map gives each user')
buyer, department = st.columns(2)
with buyer:
    st.markdown('**Straw buyer** (lead user): the biomass procurement manager of a compressed-biogas plant that runs '
                'on paddy straw, such as Verbio\'s plant at Lehragaga in Sangrur [Reported].')
    if s25 is not None and by_window is not None:
        half = by_window.loc[by_window['harvested_ha'].cumsum() >= by_window['harvested_ha'].sum() / 2,
                             'window_start'].iloc[0]
        st.markdown(
            f"- In 2025, {c.ha(s25['harvested_not_burnt_ha'])} of the harvest was not seen burnt [Ours]. That is the "
            'area where straw could still have been baled, though some of it will have been ploughed in or removed.\n'
            f"- Half the season's harvest was first seen by the 5-day window starting "
            f"{pd.Timestamp(half):%d %b}, and fields that burnt did so a median "
            f"{float(s25['median_days_harvest_to_burn']):.0f} days after harvest [Ours]. That is roughly the time a "
            'buyer has to reach a field. [Recommendation]\n'
            '- The 1 km map shows where harvest is under way and where fields are still unburnt.')
with department:
    st.markdown('**District agriculture officer** (second user): decides where to send residue-management machinery '
                'and farmer outreach, and needs to know whether burning is really falling.')
    comp = c.comparison()
    if s25 is not None and comp is not None:
        st.markdown(
            f"- In 2025, {c.ha(s25['burnt_ha'])} burnt (confirmed), and {c.pct(s25['missed_share_viirs_375m'])} "
            'of it had no VIIRS detection within 375 m [Ours].\n'
            f"- From 2021 to 2025 the burnt area fell {-comp.loc['burnt area, confirmed (ha)', 'relative change']:.0%}"
            f", but Suomi NPP detections fell {-comp.loc['Suomi NPP detections inside', 'relative change']:.0%} "
            '[Ours]. Fire counts alone overstate the fall in burning.')

st.subheader('The problem, as set out for the project')
statement = c.text(c.METHODOLOGY / 'problem_statement.md')
if statement is None:
    c.missing(c.METHODOLOGY / 'problem_statement.md')
else:
    body = statement.split('## Open questions')[0]
    st.markdown(body[body.find('| Element'):] if '| Element' in body else body)
    st.caption('From `methodology/problem_statement.md`.')

st.subheader('Next steps')
st.markdown(
    '- **Product concept, risks and the business case:** being written for the report in Week 4 (12–18 Nov 2026).\n'
    '- **Next validation step:** a pilot with a straw buyer, measuring the tonnes of straw collected from areas the '
    'map flagged before they burned (the success metric in the problem statement). [Recommendation]\n'
    '- **Untested:** whether buyers would pay for the map. [Recommendation]')

c.labels_note()
c.footer()
