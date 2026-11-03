"""Mission Explorer: satellites and missions relevant to burnt-area monitoring (dataset B)."""
import re

import altair as alt
import pandas as pd
import streamlit as st

import common as c

st.title('Mission Explorer')

PATH = c.RESEARCH / 'dataset_B_satellite_missions.csv'
missions = c.csv(PATH)
if missions is None:
    c.missing(PATH)
    st.stop()
missions = missions.copy()


def kind(sensor):
    # Our grouping of the sensor column into the kinds of data a burnt-area product could use.
    s = str(sensor).lower()
    if 'optosar' in s or ('electro-optical' in s and re.search(r'\bsar\b', s)):
        return 'Optical and radar'
    if re.search(r'\bsar\b', s):
        return 'Radar (SAR)'
    if 'viirs' in s or 'modis' in s:
        return 'Active fires and thermal'
    if 'hyperspectral' in s:
        return 'Hyperspectral'
    if 'tropomi' in s:
        return 'Atmosphere'
    if 'seviri' in s or 'sounder' in s:
        return 'Geostationary weather'
    return 'Optical'


missions['kind of data'] = missions['sensor'].map(kind)
# Our flag: ISRO satellites, NASA-ISRO's NISAR and the Indian commercial constellations in the dataset.
missions['Indian'] = missions['operator'].str.contains('ISRO', na=False) | \
    missions['satellite'].str.contains('Pixxel|GalaxEye', na=False)

st.markdown(f'{len(missions)} satellites and missions that could serve a burnt-area product, each with the page it '
            'came from and the date that page was read. Fields no source stated are left blank. [Reported]')

left, mid, right = st.columns([2, 2, 1])
query = left.text_input('Search any field', placeholder='e.g. SWIR, Sentinel, ISRO, daily')
kinds = mid.multiselect('Kind of data', sorted(missions['kind of data'].unique()),
                        help='Our grouping of the sensor column.')
indian = right.checkbox('Indian only', help='ISRO satellites, NISAR and the Indian commercial constellations.')

shown = missions
if query:
    hit = missions.astype(str).apply(lambda col: col.str.contains(query, case=False, regex=False)).any(axis=1)
    shown = shown[hit]
if kinds:
    shown = shown[shown['kind of data'].isin(kinds)]
if indian:
    shown = shown[shown['Indian']]

st.caption(f'{len(shown)} of {len(missions)} shown.')
st.dataframe(
    shown[['satellite', 'operator', 'kind of data', 'sensor', 'spatial_resolution', 'temporal_resolution_revisit',
           'mission_status', 'launch_date', 'source_url', 'access_date']],
    hide_index=True,
    column_config={
        'satellite': 'Satellite', 'operator': 'Operator', 'kind of data': 'Kind of data', 'sensor': 'Sensor',
        'spatial_resolution': 'Detail (resolution)', 'temporal_resolution_revisit': 'How often',
        'mission_status': 'Status', 'launch_date': 'Launched',
        'source_url': st.column_config.LinkColumn('Source', display_text='open'),
        'access_date': 'Read on',
    })

st.subheader('One satellite in full')
pick = st.selectbox('Satellite', shown['satellite'] if len(shown) else missions['satellite'])
row = missions[missions['satellite'] == pick].iloc[0]
fields = [('Operator', 'operator'), ('Mission', 'mission'), ('Sensor', 'sensor'), ('Orbit', 'orbit'),
          ('Applications', 'application'), ('Launch vehicle', 'launch_vehicle'), ('Launched', 'launch_date'),
          ('Status', 'mission_status'), ('Data product', 'data_product'), ('Detail', 'spatial_resolution'),
          ('How often', 'temporal_resolution_revisit'), ('Bands', 'spectral_information'), ('Coverage', 'coverage'),
          ('Notes', 'notes')]
lines = [f'- **{label}:** {row[col]}' for label, col in fields if pd.notna(row[col]) and str(row[col]).strip()]
lines.append(f'- **Source:** [{row["source_url"]}]({row["source_url"]}), read on {row["access_date"]}')
st.markdown('\n'.join(lines))

st.subheader('When they were launched')
dated = missions.assign(launched=pd.to_datetime(missions['launch_date'], errors='coerce')).dropna(subset=['launched'])
chart = alt.Chart(dated).mark_circle(size=120).encode(
    x=alt.X('launched:T', title='launch date'),
    y=alt.Y('satellite:N', sort=alt.EncodingSortField('launched', order='ascending'), title=None),
    color=alt.Color('kind of data:N', title='Kind of data'),
    tooltip=['satellite', 'operator', alt.Tooltip('launch_date:N', title='launched'), 'mission_status'],
).properties(height=28 * len(dated), width='container')
st.altair_chart(chart)
undated = missions.loc[~missions.index.isin(dated.index), 'satellite'].tolist()
if undated:
    st.caption('No launch date in the dataset: ' + ', '.join(undated) + '.')

c.footer('Source: `data/raw/research/dataset_B_satellite_missions.csv`, spot-checked and corrected on '
         '25–26 Oct 2026.')
