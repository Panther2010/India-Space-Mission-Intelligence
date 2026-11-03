"""The dashboard's front page: what the project found, and what each page shows."""
import common as c
import streamlit as st

st.title('Paddy Burnt-Area Intelligence')
st.markdown(f'**{c.AREA_LABEL}, Punjab** · Sentinel-2 burnt-area maps set against VIIRS and MODIS fire detections')
st.markdown(
    'Official stubble-burning monitoring counts fires that satellites see as they pass over. This project maps the '
    'area that actually burned, field by field, from Sentinel-2 images, and measures how much of it the fire counts '
    'missed. It is built for two users: a buyer of paddy straw deciding where to send balers before the straw is '
    'burnt, and the district agriculture department deciding where to send residue-management machinery.')

s25, comp = c.summary(2025), c.comparison()
if s25 is not None:
    cols = st.columns(4)
    cols[0].metric('Burnt in 2025, confirmed', c.ha(s25['burnt_ha']),
                   help='Burns first seen before 19 Nov; later ones are mapped as unconfirmed. Notebook 02. [Ours]')
    cols[1].metric('Share of the harvest burnt', c.pct(s25['burnt_share_of_harvested']),
                   help='Confirmed burnt area as a share of the area harvested in the season. Notebook 02. [Ours]')
    cols[2].metric('Burnt, no fire seen nearby', c.pct(s25['missed_share_viirs_375m']),
                   help='No VIIRS detection within 375 m between the last clear view and the burn. Notebook 02. [Ours]')
    if comp is not None:
        burnt = comp.loc['burnt area, confirmed (ha)', 'relative change']
        fires = comp.loc['Suomi NPP detections inside', 'relative change']
        cols[3].metric('2021→2025: burnt / fires seen', f'{c.change(burnt)} / {c.change(fires)}',
                       help='Notebook 02c: Sentinel-2 burnt area against Suomi NPP detections inside the district. '
                            '[Ours]')
else:
    c.missing(c.PROCESSED / 's2_burn_summary_sangrur_2025.csv')

st.subheader('What fire counts miss')
points = []
if comp is not None:
    points.append(f'From 2021 to 2025, Suomi NPP fire detections in the district fell '
                  f'{-comp.loc["Suomi NPP detections inside", "relative change"]:.0%}, while the burnt area '
                  f'Sentinel-2 maps fell {-comp.loc["burnt area, confirmed (ha)", "relative change"]:.0%}. [Ours]')
if s25 is not None:
    points.append(f'In 2025, {float(s25["missed_share_viirs_375m"]):.0%} of the confirmed burnt area had no VIIRS '
                  'detection within 375 m between its last clear view and the burn. [Ours]')
points.append('A December 2025 iFOREST report, as reported by The Tribune, says most large Punjab farm fires in 2024 '
              'and 2025 occurred after 3 pm; the VIIRS satellites pass in the early afternoon and at night. '
              '[Reported]')
st.markdown('\n'.join(f'- {p}' for p in points))

st.subheader('Pages')
pages = [
    ('views/1_Mission_Explorer.py', 'Mission Explorer', '🛰️',
     'Satellites and missions relevant to burnt-area monitoring, with their sources (dataset B).'),
    ('views/2_Indian_Startup_Landscape.py', 'Indian Startup Landscape', '🚀',
     'Indian space companies across the value chain (dataset A).'),
    ('views/3_EO_Analysis.py', 'EO Analysis', '🔥',
     'The burnt-area map, what fire counts missed, 2021 against 2025, the ML classifier and the 2026 forecast.'),
    ('views/4_Mission_Trade-offs.py', 'Mission Trade-offs', '⚖️',
     'Which satellite data fits the straw buyer, compared on the brief\'s six factors.'),
    ('views/5_Commercial_Opportunity.py', 'Commercial Opportunity', '💼',
     'The user, the decision, the pain point and how the product would be tested.'),
]
for path, label, icon, what in pages:
    left, right = st.columns([1, 3])
    with left:
        st.page_link(path, label=label, icon=icon)
    right.markdown(what)

c.labels_note()
c.footer('Every number on these pages is read from files the project\'s notebooks and scripts wrote.')
