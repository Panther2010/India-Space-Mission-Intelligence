"""The dashboard's front page: what the project found, and what each page shows."""
import math

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

import common as c

MAP_HEIGHT = 470
EMBERS = ['#3a1607', '#9c330b', '#ff7b39', '#ffd2a6']       # burnt hectares, low to high, glowing on navy
SATELLITE = {'VIIRS_SNPP': 'Suomi NPP', 'VIIRS_NOAA20': 'NOAA-20', 'VIIRS_NOAA21': 'NOAA-21'}


def night_map(grid, boundary, fires):
    """Burnt hectares in each 1 km square (embers) and the VIIRS fire detections (blue dots), on the navy banner."""
    lons, lats, burnt = [], [], []
    for f in grid['features']:
        value = f['properties'].get('burnt_ha') or 0
        if value > 0:
            ring = f['geometry']['coordinates'][0][:-1]
            lons.append(sum(p[0] for p in ring) / len(ring))
            lats.append(sum(p[1] for p in ring) / len(ring))
            burnt.append(round(value, 1))
    cells = pd.DataFrame({'lon': np.round(lons, 4), 'lat': np.round(lats, 4), 'burnt': burnt})
    top = max(float(np.quantile(cells['burnt'], 0.98)), 1.0)
    # The map fills the banner's height on all but very narrow screens, so a 1 km square is drawn
    # MAP_HEIGHT / (the district's north-south extent in km) pixels across, a touch larger to close the seams.
    (south, _), (north, _) = c.district_bounds(boundary)
    px_per_km = MAP_HEIGHT / ((north - south) * math.pi / 180 * 6371)
    squares = alt.Chart(cells).mark_square(size=(px_per_km * 1.06) ** 2, opacity=1).encode(
        longitude='lon:Q', latitude='lat:Q',
        color=alt.Color('burnt:Q', scale=alt.Scale(domain=[0, top], range=EMBERS, clamp=True), legend=None),
        tooltip=[alt.Tooltip('burnt:Q', title='burnt in this 1 km square (ha)', format=',.0f')])
    # The outline is drawn as lines through its rings: as a shape, the map library could read a ring wound the
    # other way as the whole globe outside the district, and zoom out to fit it.
    points, ring_id = [], 0
    for f in boundary['features']:
        geometry = f['geometry']
        polygons = geometry['coordinates'] if geometry['type'] == 'MultiPolygon' else [geometry['coordinates']]
        for polygon in polygons:
            for ring in polygon:
                points += [(str(ring_id), i, p[0], p[1]) for i, p in enumerate(ring)]
                ring_id += 1
    rings = pd.DataFrame(points, columns=['ring', 'i', 'lon', 'lat'])
    outline = alt.Chart(rings).mark_line(color=c.HAZE, strokeWidth=1.1, opacity=0.8).encode(
        longitude='lon:Q', latitude='lat:Q', detail='ring:N', order='i:Q')
    # Each detection is drawn 750 m across: the 375 m around it that the missed-share rule counts as flagged.
    dot = math.pi / 4 * (0.75 * px_per_km) ** 2
    dots = alt.Chart(fires).mark_circle(size=dot, color=c.SKY, opacity=1, stroke=c.NIGHT, strokeWidth=0.4).encode(
        longitude='longitude:Q', latitude='latitude:Q',
        tooltip=[alt.Tooltip('acq_date:N', title='VIIRS fire detection'), alt.Tooltip('satellite:N')])
    chart = alt.layer(squares, outline, dots).project(type='mercator').properties(height=MAP_HEIGHT, width='container')
    return chart.configure_view(stroke=None).configure(background='transparent'), top


def key(top, fires):
    ramp = (f'<i style="display:inline-block;width:110px;height:10px;border-radius:2px;'
            f'background:linear-gradient(to right,{",".join(EMBERS)})"></i>')
    dot = f'<i style="display:inline-block;width:9px;height:9px;border-radius:50%;background:{c.SKY}"></i>'
    st.markdown(
        f'<div class="pbi-key"><span>Burnt in each 1&nbsp;km square</span><span>0&nbsp;ha {ramp} {top:,.0f}&nbsp;ha '
        f'or more</span><span>{dot} {fires:,} VIIRS fire detections, each drawn 750&nbsp;m across</span></div>',
        unsafe_allow_html=True)


s25, comp = c.summary(2025), c.comparison()
grid = c.geojson(c.PROCESSED / 's2_burn_grid_1km_sangrur_2025.geojson')
boundary = c.geojson(c.PROCESSED / 'boundary_sangrur_pre2021.geojson')
detections = c.csv(c.PROCESSED / 'firms_detections_sangrur_2025.csv')

if s25 is None:
    c.page_header('space_dashboard', 'Paddy Burnt-Area Intelligence')
    c.missing(c.PROCESSED / 's2_burn_summary_sangrur_2025.csv')
    st.stop()

try:
    hero = st.container(key='hero')
except TypeError:                      # older Streamlit: no keyed containers, so the banner is unstyled
    hero = st.container()
with hero:
    words, picture = st.columns([6, 5], gap='large')
    with words:
        st.markdown('<p class="pbi-where">Sangrur (pre-2021 boundary), Punjab, 2025 season</p>'
                    f'<h1 class="pbi-headline">Fire counts missed {c.pct(s25["missed_share_viirs_375m"])} of the '
                    'burnt area.</h1>', unsafe_allow_html=True)
        st.markdown(
            f'<p class="pbi-lede">Sentinel-2 images show {float(s25["burnt_ha"]):,.0f} ha of paddy fields burnt in '
            f'the 2025 season. For {float(s25["missed_share_viirs_375m"]) * 100:.1f}% of that area, no VIIRS fire '
            'detection fell within 375 m between its last clear view and the burn. [Ours]</p>'
            '<p class="pbi-lede">This prototype maps the area that actually burned, field by field, for a buyer of '
            'paddy straw deciding where to send balers, and for the district agriculture department.</p>',
            unsafe_allow_html=True)
    with picture:
        if grid is not None and boundary is not None and detections is not None:
            fires = detections[detections['inside'] & detections['sensor'].str.startswith('VIIRS')].assign(
                satellite=lambda d: d['sensor'].map(SATELLITE))[['longitude', 'latitude', 'acq_date', 'satellite']]
            chart, top = night_map(grid, boundary, fires)
            st.altair_chart(chart)
            key(top, len(fires))
        else:
            c.missing(c.PROCESSED / 's2_burn_grid_1km_sangrur_2025.geojson')

cols = st.columns(4)
c.metric(cols[0], 'Burnt in 2025, confirmed', c.ha(s25['burnt_ha']),
         help='Burns first seen before 19 Nov; later ones are mapped as unconfirmed. Notebook 02. [Ours]')
c.metric(cols[1], 'Share of the harvest burnt', c.pct(s25['burnt_share_of_harvested']),
         help='Confirmed burnt area as a share of the area harvested in the season. Notebook 02. [Ours]')
if comp is not None:
    minus = str.maketrans({'-': '−'})            # a true minus sign in the big numbers
    c.metric(cols[2], 'Burnt area, 2021 to 2025',
             c.change(comp.loc['burnt area, confirmed (ha)', 'relative change']).translate(minus),
             help='Sentinel-2 confirmed burnt area in the district, 2021 against 2025. Notebook 02c. [Ours]')
    c.metric(cols[3], 'Fire detections, 2021 to 2025',
             c.change(comp.loc['Suomi NPP detections inside', 'relative change']).translate(minus),
             help='Suomi NPP VIIRS detections inside the district, the one satellite counted the same way in both '
                  'seasons. Notebook 02c. [Ours]')

st.subheader('The story in three steps')
steps = [
    ('Map what burned', 'views/3_EO_Analysis.py', 'EO Analysis', 'local_fire_department',
     f"{c.ha(s25['burnt_ha'])} burnt in 2025, {c.pct(s25['burnt_share_of_harvested'])} of the harvest, mapped from "
     'Sentinel-2 at 20 m and checked against 187 labelled points [Ours].'),
    ('Measure what fire counts miss', 'views/3_EO_Analysis.py', 'EO Analysis', 'local_fire_department',
     f"No VIIRS detection fell near {c.pct(s25['missed_share_viirs_375m'])} of it. The satellites pass in the early "
     'afternoon and at night [Ours]; most large Punjab farm fires in 2024 and 2025 occurred after 3 pm, iFOREST '
     'reports [Reported].'),
    ('Put it to work', 'views/5_Commercial_Opportunity.py', 'Commercial Opportunity', 'agriculture',
     'Every 5 days, a straw buyer sees where fresh straw lies before it burns, and the agriculture department sees '
     'the burning that fire counts miss [Recommendation].'),
]
for col, (n, (title, path, page, icon, words)) in zip(st.columns(3, gap='medium'), enumerate(steps, start=1)):
    with col:
        with st.container(border=True):
            st.markdown(f'#### {n}. {title}')
            st.markdown(words)
            st.page_link(path, label=page, icon=f':material/{icon}:')

c.labels_note()
c.footer('Every number on these pages is read from files the project\'s notebooks and scripts wrote.')
