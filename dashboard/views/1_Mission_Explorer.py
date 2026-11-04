"""Mission Explorer: satellites and missions relevant to burnt-area monitoring (dataset B)."""
import re

import altair as alt
import pandas as pd
import streamlit as st

import common as c

PATH = c.RESEARCH / 'dataset_B_satellite_missions.csv'
missions = c.csv(PATH)
if missions is None:
    c.page_header('Mission Explorer')
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
dated = missions.assign(launched=pd.to_datetime(missions['launch_date'], errors='coerce')).dropna(subset=['launched'])

c.page_header('Mission Explorer',
              f'{len(missions)} satellites and missions that could serve a burnt-area product, each with the page it '
              'came from and the date that page was read. Fields no source stated are left blank. [Reported]',
              eyebrow='Research · dataset B')

# ---- The key numbers up front ------------------------------------------------------------------------------------
key = [c.tile('satellite', f'{len(missions)}', '', 'Satellites and missions',
              f"{dated['launched'].dt.year.min()}–{dated['launched'].dt.year.max()}" if len(dated) else ''),
       c.tile('map-pin', f"{int(missions['Indian'].sum())}", '', 'Indian, with NISAR', glow='ember',
              help='ISRO satellites, NASA-ISRO\'s NISAR and the Indian commercial constellations.'),
       c.tile('layers', f"{missions['kind of data'].nunique()}", '', 'Kinds of data',
              help='Our grouping of the sensor column.')]
if len(dated):
    newest = dated.sort_values('launched').iloc[-1]
    key.append(c.tile('rocket', f"{newest['launched']:%b %Y}", '', f"Latest launch: {c.esc(newest['satellite'])}"))
c.tiles(key, columns=len(key), note='Counted from the dataset; the kinds of data are our grouping.')

# ---- The rest, one tab at a time ----------------------------------------------------------------------------------
with c.panel('missions'):
    t_all, t_one, t_when, t_status = st.tabs(['All missions', 'One in full', 'Launch timeline', 'Status notes'])

    with t_all:
        left, mid, right = st.columns([2, 2, 1])
        query = left.text_input('Search any field', placeholder='e.g. SWIR, Sentinel, ISRO, daily')
        kinds = mid.multiselect('Kind of data', sorted(missions['kind of data'].unique()),
                                help='Our grouping of the sensor column.')
        indian = right.toggle('Indian only', help='ISRO satellites, NISAR and the Indian commercial constellations.')
        shown = missions
        if query:
            hit = missions.astype(str).apply(lambda col: col.str.contains(query, case=False, regex=False)).any(axis=1)
            shown = shown[hit]
        if kinds:
            shown = shown[shown['kind of data'].isin(kinds)]
        if indian:
            shown = shown[shown['Indian']]
        c.html(f'<div class="mc-small">{len(shown)} of {len(missions)} shown.</div>')
        st.dataframe(
            shown[['satellite', 'operator', 'kind of data', 'sensor', 'spatial_resolution',
                   'temporal_resolution_revisit', 'mission_status', 'launch_date', 'source_url', 'access_date']],
            hide_index=True,
            column_config={
                'satellite': 'Satellite', 'operator': 'Operator', 'kind of data': 'Kind of data', 'sensor': 'Sensor',
                'spatial_resolution': 'Detail (resolution)', 'temporal_resolution_revisit': 'How often',
                'mission_status': 'Status', 'launch_date': 'Launched',
                'source_url': st.column_config.LinkColumn('Source', display_text='open'),
                'access_date': 'Read on',
            })

    with t_one:
        pick = st.selectbox('Satellite', shown['satellite'] if len(shown) else missions['satellite'],
                            help='The list follows the search and filters on the first tab.')
        row = missions[missions['satellite'] == pick].iloc[0]
        fields = [('Operator', 'operator'), ('Mission', 'mission'), ('Sensor', 'sensor'), ('Orbit', 'orbit'),
                  ('Applications', 'application'), ('Launch vehicle', 'launch_vehicle'), ('Launched', 'launch_date'),
                  ('Status', 'mission_status'), ('Data product', 'data_product'), ('Detail', 'spatial_resolution'),
                  ('How often', 'temporal_resolution_revisit'), ('Bands', 'spectral_information'),
                  ('Coverage', 'coverage'), ('Notes', 'notes')]
        lines = [f'- **{label}:** {row[col]}' for label, col in fields if pd.notna(row[col]) and str(row[col]).strip()]
        # Some records cite more than one page, separated by semicolons: each gets its own link.
        urls = [u.strip() for u in str(row['source_url']).split(';') if u.strip()]
        lines.append('- **Source:** ' + '; '.join(f'[{u}]({u})' for u in urls) + f', read on {row["access_date"]}')
        with c.card('mission'):
            c.eyebrow(f"{c.esc(row['kind of data'])}{' · Indian' if row['Indian'] else ''}", 'satellite')
            st.markdown(f"### {row['satellite']}")
            st.markdown('\n'.join(lines))

    with t_when:
        c.eyebrow('When they were launched')
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

    with t_status:
        noted = missions.dropna(subset=['mission_status'])
        c.eyebrow(f'What the sources said about each mission\'s status ({len(noted)} of {len(missions)})')
        c.html('<div class="mc-card" style="margin-top:.7rem">'
               + ''.join(f'<div class="mc-pipe"><i class="mc-dot plain"></i><div><strong>{c.esc(r.satellite)}</strong>'
                         f'<em>{c.esc(r.mission_status)}</em></div><span class="mc-chip">read '
                         f'{c.esc(r.access_date)}</span></div>' for r in noted.itertuples())
               + '</div><div class="mc-small">As each source stated it on the date it was read. [Reported]</div>')

c.footer('Source: `data/raw/research/dataset_B_satellite_missions.csv`, spot-checked and corrected on '
         '25–26 Oct 2026.')
