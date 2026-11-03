"""Commercial Opportunity: the straw buyer's map, the two users, the problem and how the product would be tested."""
import branca.colormap as bcm
import folium
import numpy as np
import pandas as pd
import streamlit as st

import common as c

# Fresh straw, low to high: the same greens as 'harvested and not seen burnt' on the EO Analysis map.
STRAW = ['#0b2e1f', '#1f7a3f', '#4cd07a', '#d3f9d8']
FIRST, LAST, DEFAULT = '2025-09-30', '2025-11-14', '2025-10-30'

c.page_header('agriculture', 'Commercial Opportunity',
              'The 2025 season as a straw buyer would have seen it, the two users, the problem, and how the product '
              'would be tested.')


def straw_map(now, boundary):
    """Fresh straw per 1 km square for one window (green), with that window's burning as ember dots."""
    grid = c.slim_grid(2025)
    fresh = dict(zip(now['cell'], now['fresh_straw_ha']))
    burnt = dict(zip(now['cell'], now['burnt_ha'] + now['late_burnt_ha']))
    values = np.array([v for v in fresh.values() if v > 0], float)
    top = max(float(np.quantile(values, 0.98)), 1.0) if len(values) else 1.0
    cmap = bcm.LinearColormap(STRAW, vmin=0, vmax=top)
    for f in grid['features']:
        p = f['properties']
        p['_fresh'] = fresh.get(p['cell'], 0.0)
        p['_label'] = (f"{p['_fresh']:,.0f} ha of fresh straw; {burnt.get(p['cell'], 0.0):,.0f} ha first seen burnt "
                       'in this window')
    m = c.dark_map(folium.Map(tiles='OpenStreetMap', zoom_snap=0.25, prefer_canvas=True))
    folium.GeoJson(
        grid, name='Fresh straw',
        style_function=lambda f: {'fillColor': cmap(min(f['properties']['_fresh'], top)),
                                  'fillOpacity': 0.85 if f['properties']['_fresh'] > 0 else 0, 'weight': 0},
        tooltip=folium.GeoJsonTooltip(fields=['_label'], labels=False)).add_to(m)
    centres = c.grid_centres(2025)
    dots = folium.FeatureGroup(name='Burnt in this window')
    for cell, hectares in burnt.items():
        if hectares >= 5 and cell in centres:
            # A whole square burnt (100 ha) gets a dot of radius 6 px; dots grow with the square root of the area.
            folium.CircleMarker(centres[cell], radius=max(1.5, 6 * (hectares / 100) ** 0.5), color=c.NIGHT,
                                weight=0.6, fill=True, fill_color=c.EMBER, fill_opacity=0.95).add_to(dots)
    dots.add_to(m)
    folium.GeoJson(boundary, style_function=lambda f: {'color': '#c5d3e6', 'weight': 1.4, 'fillOpacity': 0}).add_to(m)
    m.fit_bounds(c.district_bounds(boundary))
    return m, top


s25 = c.summary(2025)
by_window = c.csv(c.PROCESSED / 's2_burn_by_window_sangrur_2025.csv')
straw = c.csv(c.PROCESSED / 'straw_by_window_sangrur_2025.csv')
boundary = c.geojson(c.PROCESSED / 'boundary_sangrur_pre2021.geojson')

st.subheader("The buyer's map")
if straw is None or by_window is None or boundary is None or c.slim_grid(2025) is None:
    c.missing(c.PROCESSED / 'straw_by_window_sangrur_2025.csv')
else:
    st.markdown('Pick a 5-day window of the 2025 season. **Green** squares hold fields harvested in the 10 days to the '
                'end of that window and not yet seen burnt: straw a buyer could still collect. **Ember** dots show '
                'burning first seen in that window. Each view uses only the images up to the end of its window, so it '
                'shows what a buyer could have seen then. [Ours]')
    windows = [w for w in sorted(straw['window_start'].unique()) if FIRST <= w <= LAST]
    pick = st.select_slider('5-day window starting', windows, value=DEFAULT if DEFAULT in windows else windows[0],
                            format_func=lambda d: f'{pd.Timestamp(d):%d %b}', key='straw_window')
    now = straw[straw['window_start'] == pick]
    detections = by_window.loc[by_window['window_start'] == pick, 'viirs_detections_inside']
    cols = st.columns(3)
    c.metric(cols[0], 'Fresh straw on the ground', c.ha(now['fresh_straw_ha'].sum()),
             help='Harvested in this window or the one before, and not seen burnt by the end of this window. [Ours]')
    c.metric(cols[1], 'Burnt in this window', c.ha(now['burnt_ha'].sum() + now['late_burnt_ha'].sum()),
             help='First seen burnt in this window. From 19 Nov these burns are unconfirmed. [Ours]')
    c.metric(cols[2], 'VIIRS fire detections in this window',
             f'{int(detections.iloc[0]):,}' if len(detections) else '–',
             help='Inside the district, from every VIIRS satellite flying in 2025. [Ours]')
    map_col, list_col = st.columns([3, 2], gap='large')
    with map_col:
        m, top = straw_map(now, boundary)
        c.show_map(m, height=520, key=f'straw_{pick}')
        c.legend(STRAW, ('0 ha', f'{top:,.0f} ha or more'),
                 'fresh straw in each 1 km square. Ember dots: burnt in this window (5 ha or more), larger for '
                 'more area.')
    with list_col:
        st.markdown('**Where to send balers first**')
        centres = c.grid_centres(2025)
        best = now.nlargest(10, 'fresh_straw_ha')[['cell', 'fresh_straw_ha']].copy()
        best['latitude'] = [round(centres[cell][0], 4) for cell in best['cell']]
        best['longitude'] = [round(centres[cell][1], 4) for cell in best['cell']]
        best['map'] = [f'https://www.google.com/maps/search/?api=1&query={lat},{lon}'
                       for lat, lon in zip(best['latitude'], best['longitude'])]
        try:
            bar = st.column_config.ProgressColumn('Fresh straw (ha)', format='%.0f', min_value=0, max_value=100,
                                                  color=STRAW[2])
        except TypeError:                      # older Streamlit: bars in the theme colour
            bar = st.column_config.ProgressColumn('Fresh straw (ha)', format='%.0f', min_value=0, max_value=100)
        st.dataframe(best[['fresh_straw_ha', 'latitude', 'longitude', 'map']], hide_index=True, column_config={
            'fresh_straw_ha': bar,
            'latitude': st.column_config.NumberColumn('Latitude', format='%.4f'),
            'longitude': st.column_config.NumberColumn('Longitude', format='%.4f'),
            'map': st.column_config.LinkColumn('Map', display_text='open')})
        st.caption('The 1 km squares with the most fresh straw in this window, at their centres. A whole square is '
                   '100 ha.')
    st.caption('Not seen burnt doesn\'t mean the straw is still there: it may have been baled, ploughed in or removed, '
               'which the map can\'t see. [Recommendation]')

st.subheader('What the map gives each user')
buyer, department = st.columns(2, gap='large')
with buyer:
    with st.container(border=True):
        st.markdown('**Straw buyer** (lead user): the biomass procurement manager of a compressed-biogas plant that '
                    'runs on paddy straw, such as Verbio\'s plant at Lehragaga in Sangrur [Reported].')
        if s25 is not None and by_window is not None:
            half = by_window.loc[by_window['harvested_ha'].cumsum() >= by_window['harvested_ha'].sum() / 2,
                                 'window_start'].iloc[0]
            st.markdown(
                f"- In 2025, {c.ha(s25['harvested_not_burnt_ha'])} of the harvest was not seen burnt [Ours]. That is "
                'the area where straw could still have been baled, though some of it will have been ploughed in or '
                'removed.\n'
                f"- Half the season's harvest was first seen by the 5-day window starting "
                f"{pd.Timestamp(half):%d %b}, and fields that burnt did so a median "
                f"{float(s25['median_days_harvest_to_burn']):.0f} days after harvest [Ours]. That is roughly the time "
                'a buyer has to reach a field. [Recommendation]')
with department:
    with st.container(border=True):
        st.markdown('**District agriculture officer** (second user): decides where to send residue-management '
                    'machinery and farmer outreach, and needs to know whether burning is really falling.')
        comp = c.comparison()
        if s25 is not None and comp is not None:
            st.markdown(
                f"- In 2025, {c.ha(s25['burnt_ha'])} burnt (confirmed), and {c.pct(s25['missed_share_viirs_375m'])} "
                'of it had no VIIRS detection within 375 m [Ours].\n'
                f"- From 2021 to 2025 the burnt area fell "
                f"{-comp.loc['burnt area, confirmed (ha)', 'relative change']:.0%}, but Suomi NPP detections fell "
                f"{-comp.loc['Suomi NPP detections inside', 'relative change']:.0%} [Ours]. Fire counts alone "
                'overstate the fall in burning.')

statement = c.text(c.METHODOLOGY / 'problem_statement.md')
with st.expander('The problem, as set out for the project'):
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
c.footer('The buyer\'s map comes from `data/processed/straw_by_window_sangrur_2025.csv`, written from Notebook 02\'s '
         '20 m map by `dashboard/make_straw_table.py`.')
