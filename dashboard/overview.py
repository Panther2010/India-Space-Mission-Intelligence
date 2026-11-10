"""The dashboard's front page: the finding and the map up front, four key numbers, and the rest in tabs."""
import math
import re

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

import common as c

MAP_HEIGHT = 440
EMBERS = ['#3a1607', '#9c330b', '#ff7b39', '#ffd2a6']       # burnt hectares, low to high, glowing on the dark page
SATELLITE = {'VIIRS_SNPP': 'Suomi NPP', 'VIIRS_NOAA20': 'NOAA-20', 'VIIRS_NOAA21': 'NOAA-21'}
EO, BUYER = 'views/3_EO_Analysis.py', 'views/5_Commercial_Opportunity.py'


def burnt_cells(grid):
    """Centre and burnt hectares of each 1 km square with any confirmed burning."""
    lons, lats, burnt = [], [], []
    for f in grid['features']:
        value = f['properties'].get('burnt_ha') or 0
        if value > 0:
            ring = f['geometry']['coordinates'][0][:-1]
            lons.append(sum(p[0] for p in ring) / len(ring))
            lats.append(sum(p[1] for p in ring) / len(ring))
            burnt.append(round(value, 1))
    return pd.DataFrame({'lon': np.round(lons, 4), 'lat': np.round(lats, 4), 'burnt': burnt})


def night_map(grid, boundary, fires, top, height=MAP_HEIGHT):
    """Burnt hectares in each 1 km square (embers) and the VIIRS fire detections (blue dots), on one colour scale
    for both seasons."""
    cells = burnt_cells(grid)
    # The district is taller than it is wide, so the map fills its height: a 1 km square is drawn height / (the
    # district's north-south extent in km) pixels across, a touch larger to close the seams.
    (south, _), (north, _) = c.district_bounds(boundary)
    px_per_km = height / ((north - south) * math.pi / 180 * 6371)
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
    dots = alt.Chart(fires).mark_circle(size=math.pi / 4 * (0.75 * px_per_km) ** 2, color=c.SKY, opacity=1).encode(
        longitude='longitude:Q', latitude='latitude:Q',
        tooltip=[alt.Tooltip('acq_date:N', title='VIIRS fire detection'), alt.Tooltip('satellite:N')])
    chart = alt.layer(squares, outline, dots).project(type='mercator').properties(height=height, width='container')
    return chart.configure_view(stroke=None).configure(background='transparent')


def map_key(top, fires, year=None):
    ramp = (f'<i style="display:inline-block;width:90px;height:8px;border-radius:2px;vertical-align:middle;'
            f'background:linear-gradient(to right,{",".join(EMBERS)})"></i>')
    c.html(f'<div class="mc-small" style="text-align:center">Burnt per 1 km square{", " + str(year) if year else ""}: '
           f'0 {ramp} {top:,.0f}+ ha · <span style="color:{c.SKY}">●</span> {len(fires):,} VIIRS detections</div>')


def viirs(detections):
    """VIIRS detections inside the district, with the satellite's name."""
    return detections[detections['inside'] & detections['sensor'].str.startswith('VIIRS')].assign(
        satellite=lambda d: d['sensor'].map(SATELLITE))[['longitude', 'latitude', 'acq_date', 'satellite']]


def window_chart(win):
    """Each 5-day window's share of the season's burnt area and of its VIIRS detections."""
    w = win.assign(date=pd.to_datetime(win['window_start']))
    w = w[w['date'] >= '2025-09-30']
    names = ['Burnt area', 'VIIRS detections']
    long = pd.concat([
        pd.DataFrame({'date': w['date'], 'series': names[0], 'share': w['burnt_ha'] / win['burnt_ha'].sum()}),
        pd.DataFrame({'date': w['date'], 'series': names[1],
                      'share': w['viirs_detections_inside'] / win['viirs_detections_inside'].sum()})])
    base = alt.Chart(long).encode(
        x=alt.X('date:T', title=None, axis=alt.Axis(format='%d %b', labelAngle=0, tickCount=6)),
        y=alt.Y('share:Q', title=None, axis=alt.Axis(format='.0%', tickCount=4)),
        color=alt.Color('series:N', scale=alt.Scale(domain=names, range=[c.EMBER, c.SKY]),
                        legend=alt.Legend(orient='bottom', title=None, symbolType='circle', symbolSize=60)),
        tooltip=[alt.Tooltip('series:N', title=' '), alt.Tooltip('date:T', title='5-day window from', format='%d %b'),
                 alt.Tooltip('share:Q', title='share of the season', format='.1%')])
    chart = (base.mark_line(interpolate='monotone', strokeWidth=2.2)
             + base.mark_circle(size=46, opacity=1, stroke=c.PANEL, strokeWidth=1.5))
    return chart.properties(height=290, width='container').configure_view(stroke=c.RULE).configure(
        background='transparent')


def forecast_row(area, head, checked, last_week, update=None):
    """One area's 2026 forecast check: the latest week, and the season so far against the season forecast.
    With `update` (a row of the updated forecasts' summary), also the updated forecast for the week ahead."""
    ahead = ''
    if update is not None:
        start, end, issued = (pd.Timestamp(update[k]) for k in ('next_week_start', 'next_week_end', 'issued_on'))
        ahead = (f'<div class="mc-small">Week {int(update["next_week"])} ({start.day} {start:%b}–{end.day} {end:%b}): '
                 f'about <b>{update["next_week_forecast"]:,.0f}</b> forecast, 80% range '
                 f'{update["next_week_low"]:,.0f}–{update["next_week_high"]:,.0f} '
                 f'(updated forecast, {issued.day} {issued:%b})</div>')
    h = head.loc[area]
    method = h['method']
    weeks = checked[checked['area'] == area]
    seen = float(h['seen_so_far']) + weeks['actual'].sum()
    season = float(h['forecast_season'])
    wk = weeks[weeks['week'] == last_week].iloc[0]
    share = seen / season
    colour = c.AMBER if seen > season else c.GREEN
    return (f'<div class="mc-row"><div class="mc-row-head"><span class="mc-ic">{c.icon("radar")}</span>'
            f'<div><strong>{area}</strong><em class="{"mc-warn" if seen > season else "mc-ok"}">Week {last_week}: '
            f'{wk["actual"]:,.0f} seen, {wk[method]:,.0f} forecast</em></div>'
            f'<span class="mc-chip {"up" if wk["actual"] > 1.5 * wk[method] else ""}">seen '
            f'{wk["actual"] / wk[method]:.2g}×</span></div>'
            f'<div class="mc-cells"><div><b>{seen:,.0f}</b><span>seen so far</span></div>'
            f'<div class="mc-prog"><span><span>of the season forecast</span><span style="color:{colour}">'
            f'{share * 100:.0f}%</span></span><i><u style="width:{min(share, 1) * 100:.0f}%;background:{colour};'
            f'box-shadow:0 0 8px {colour}"></u></i></div>'
            f'<div><b>{season:,.0f}</b><span>season forecast</span></div></div>{ahead}</div>')


P = c.PROCESSED
s25, comp = c.summary(2025), c.comparison()
win = c.csv(P / 's2_burn_by_window_sangrur_2025.csv')
grid = c.geojson(P / 's2_burn_grid_1km_sangrur_2025.geojson')
boundary = c.geojson(P / 'boundary_sangrur_pre2021.geojson')
detections = c.csv(P / 'firms_detections_sangrur_2025.csv')

if s25 is None or comp is None or win is None:
    c.page_header('Paddy Burnt-Area Intelligence')
    c.missing(P / 's2_burn_summary_sangrur_2025.csv')
    st.stop()

harvested = float(s25['harvested_ha'])
confirmed = win[win['burns_confirmed']]
flagged, missed = confirmed['burnt_flagged_ha'].sum(), confirmed['burnt_missed_ha'].sum()
late, not_burnt = float(s25['burnt_unconfirmed_ha']), float(s25['harvested_not_burnt_ha'])
m375, m750, mmod = (float(s25[k]) for k in ('missed_share_viirs_375m', 'missed_share_viirs_750m',
                                              'missed_share_viirs_750m_or_modis_1000m'))
grid21 = c.geojson(P / 's2_burn_grid_1km_sangrur_2021.geojson')
maps_ready = grid is not None and boundary is not None and detections is not None
top = max(float(np.quantile(burnt_cells(g)['burnt'], 0.98)) for g in (grid, grid21) if g is not None) \
    if maps_ready else 1.0

fsum, check = c.csv(P / 'fire_forecast_2026_summary.csv'), c.csv(P / 'fire_forecast_check_2026.csv')
checked = check.dropna(subset=['actual']) if check is not None else None
last_week = int(checked['week'].max()) if checked is not None and len(checked) else None
head = fsum[fsum['headline']].set_index('area') if fsum is not None else None
upd = c.csv(P / 'fire_forecast_2026_updates_summary.csv')        # Notebook 04, section 7: one update per week
latest_update = (upd[upd['issue_week'] == upd['issue_week'].max()].set_index('area')
                 if upd is not None and len(upd) else None)

# ---- The finding and the map --------------------------------------------------------------------------------------
with c.keyed('hero_overview'):
    words, picture = st.columns([1.1, 1], gap='large', vertical_alignment='center')
    with words:
        pill = f'<span class="mc-pill">2026 forecast · <b>week {last_week} checked</b></span>' if last_week else ''
        c.html(
            f'<div class="mc-hero-top"><span class="mc-eyebrow"><i class="mc-dot"></i>Pilot district · Punjab</span>'
            f'{pill}</div><h1 class="mc-title-xl">Sangrur · 2025</h1>'
            '<p class="mc-lede" style="max-width:33rem">Paddy stubble burning mapped field by field from Sentinel-2, '
            'and set against what satellite fire counts saw.</p>'
            f'<div class="mc-big"><b>{m375 * 100:.1f}%</b><p>of the burnt area had no VIIRS fire detection within '
            f'375 m. [Ours]</p>{c.ring(1 - m375, "CAUGHT")}</div>')
        c.cta_row([(EO, 'Explore the analysis', 'analysis', 'ember'),
                   (BUYER, "Open the buyer's map", 'buyer', 'green')], key='hero')
    with picture:
        if maps_ready:
            fires25 = viirs(detections)
            st.altair_chart(night_map(grid, boundary, fires25, top))
            map_key(top, fires25)
        else:
            c.missing(P / 's2_burn_grid_1km_sangrur_2025.geojson')

# ---- Four key numbers ---------------------------------------------------------------------------------------------
straw = c.csv(P / 'straw_by_window_sangrur_2025.csv')
w30 = straw[straw['window_start'] == '2025-10-30'] if straw is not None else None
burnt_change = comp.loc['burnt area, confirmed (ha)', 'relative change']
npp_change = comp.loc['Suomi NPP detections inside', 'relative change']
share_diff = comp.loc['burnt share of harvested area', 'difference']
key = [
    c.tile('flame', f'{float(s25["burnt_ha"]):,.0f}', 'ha', 'Burnt in 2025, confirmed',
           f'▽ {abs(burnt_change) * 100:.0f}%<span class="mc-vs"> vs 2021</span>', 'down', 'ember',
           help='Burns first seen before 19 Nov; later ones are mapped as unconfirmed. Notebook 02.'),
    c.tile('wheat', f'{float(s25["burnt_share_of_harvested"]) * 100:.1f}', '%', 'Share of the harvest burnt',
           f'▽ {abs(share_diff) * 100:.0f} pts<span class="mc-vs"> vs 2021</span>', 'down',
           help='Confirmed burnt area as a share of the area harvested in the season. Notebook 02.'),
    c.tile('satellite', f'{int(comp.loc["Suomi NPP detections inside", "2025"]):,}', '', 'Suomi NPP fire detections',
           f'▽ {abs(npp_change) * 100:.0f}%<span class="mc-vs"> vs 2021</span>', 'up',
           help='Suomi NPP VIIRS detections inside the district, the one satellite counted the same way in both '
                'seasons. Notebook 02c.'),
]
if w30 is not None and len(w30):
    key.append(c.tile('tractor', f'{w30["fresh_straw_ha"].sum():,.0f}', 'ha', 'Fresh straw on the ground, 30 Oct – 3 Nov',
                      "buyer's map", '', 'green',
                      help='Harvested in the 10 days to 3 Nov and not yet seen burnt: straw a buyer could still '
                           'collect. From the buyer\'s map.'))
c.tiles(key, columns=len(key), note='Changes are against 2021 (Notebook 02c). Fresh straw: harvested in the last 10 days '
                                    'and not yet seen burnt. [Ours]')

# ---- The rest, one tab at a time ------------------------------------------------------------------------------
with c.panel('overview'):
    t_what, t_when, t_fc, t_2021, t_data = st.tabs(
        ['What burned', 'When it burned', '2026 forecast', '2021 vs 2025', 'Data'])

    with t_what:
        a, b = st.columns([1.45, 1], gap='large')
        with a:
            c.html(
                f'<div class="mc-eyebrow">Where the {harvested:,.0f} ha harvested in 2025 went</div>'
                '<div class="mc-grid mc-cols-2" style="margin-top:.8rem">'
                + c.tile('wheat', f'{not_burnt / harvested * 100:.1f}', '%', 'Harvested, not seen burnt',
                         f'{not_burnt:,.0f} ha', '', 'green')
                + c.tile('eye-off', f'{missed / harvested * 100:.1f}', '%', 'Burnt, no fire detected',
                         f'{missed:,.0f} ha', '', 'red')
                + c.tile('scan-eye', f'{flagged / harvested * 100:.1f}', '%', 'Burnt, fire detected',
                         f'{flagged:,.0f} ha', '', 'amber')
                + c.tile('timer', f'{late / harvested * 100:.1f}', '%', 'Burnt late, unconfirmed', f'{late:,.0f} ha',
                         help='First seen from 19 Nov, when damp soil under a young crop can look like a burn.')
                + '</div><div class="mc-small">Notebook 02. [Ours]</div>')
        with b:
            rules = [('VIIRS within 375 m', m375, c.RED), ('VIIRS within 750 m', m750, c.AMBER),
                     ('VIIRS within 750 m, or MODIS within 1 km', mmod, c.AMBER)]
            c.html('<div class="mc-eyebrow">Burnt area missed, by how near a detection must be</div>'
                   + ''.join(f'<div class="mc-rule"><span>{name}</span><b>{v * 100:.1f}%</b><i><u style="width:'
                             f'{v * 100:.1f}%;background:{colour}"></u></i></div>' for name, v, colour in rules)
                   + '<div class="mc-small" style="margin-top:.9rem">Even the loosest rule misses most of it. '
                     '[Ours]</div>')
            c.cta(EO, 'Open the burnt-area map', 'map')

    with t_when:
        a, b = st.columns([1.45, 1], gap='large')
        with a:
            c.eyebrow('Burning by 5-day window · share of the season')
            st.altair_chart(window_chart(win))
        with b:
            c.html(
                c.tile('timer', f'{float(s25["median_days_harvest_to_burn"]):.0f}', 'days', 'Median, harvest to burn',
                       'same as 2021' if comp.loc['median days from harvest to burn', 'difference'] == 0 else '')
                + f'<div class="mc-insight" style="margin-top:12px"><div class="mc-eyebrow"><span class="mc-badge">'
                  f'{c.icon("sparkles", 16, "#c4b5fd")}</span>Why fire counts may miss it</div>'
                  '<p>The satellites pass in the early afternoon and at night [Ours]; most large Punjab farm fires in '
                  '2024 and 2025 occurred after 3 pm, iFOREST reports [Reported].</p></div>')
            c.cta(EO, 'Open the EO analysis', 'eo', 'violet')

    with t_fc:
        if head is None or last_week is None:
            st.info('No week after the 2026 forecast has been checked in the committed data yet.')
        else:
            issued = pd.Timestamp(head['issued_on'].iloc[0])
            c.eyebrow(f'Suomi NPP fire detections against the forecast issued {issued.day} {issued:%b %Y}',
                      'triangle-alert', c.AMBER)
            a, b = st.columns(2, gap='large')
            for col, area in ((a, 'Punjab'), (b, 'Sangrur')):
                with col:
                    update = (latest_update.loc[area] if latest_update is not None and area in latest_update.index
                              else None)
                    c.html(forecast_row(area, head, checked, last_week, update))
            c.html(f'<div class="mc-small">Headline method: {head.loc["Punjab", "method"]}. "Seen" counts the season '
                   'to date; weeks are checked as each weekly run of Notebook 04 is committed.'
                   + (' The week ahead comes from the updated forecast, remade at each weekly run; the forecast of '
                      '1 Nov stays fixed as the test.' if latest_update is not None else '') + ' [Ours]</div>')
            c.cta(EO, 'Open the forecast', 'forecast')

    with t_2021:
        a, b = st.columns([1, 1.25], gap='large')
        with a:
            fires21 = c.csv(P / 'firms_detections_sangrur_2021.csv')
            if grid21 is not None and fires21 is not None and boundary is not None:
                fires21 = viirs(fires21)
                st.altair_chart(night_map(grid21, boundary, fires21, top, height=360))
                map_key(top, fires21, 2021)
            else:
                c.missing(P / 's2_burn_grid_1km_sangrur_2021.geojson')
        with b:
            rows = [('Burnt area, confirmed', 'burnt area, confirmed (ha)', lambda v: f'{v:,.0f} ha'),
                    ('Share of harvest burnt', 'burnt share of harvested area', lambda v: f'{v * 100:.1f}%'),
                    ('Suomi NPP detections', 'Suomi NPP detections inside', lambda v: f'{v:,.0f}'),
                    ('Missed by VIIRS, 375 m',
                     'missed share as reported by Notebook 02 (VIIRS satellites flying that year, 375 m)',
                     lambda v: f'{v * 100:.1f}%')]
            body = ''.join(f'<tr><td>{n}</td><td>{f(comp.loc[k, "2021"])}</td><td>{f(comp.loc[k, "2025"])}</td></tr>'
                           for n, k, f in rows)
            c.html('<div class="mc-eyebrow">2021 against 2025</div>'
                   f'<table class="mc-table"><tr><th></th><th>2021</th><th>2025</th></tr>{body}</table>'
                   f'<div class="mc-small">Burning fell by about {abs(burnt_change):.0%}; Suomi NPP fire detections '
                   f'fell by {abs(npp_change):.0%}. Notebook 02c. [Ours]</div>')
            c.cta(EO, 'Compare the seasons', 'compare')

    with t_data:
        a, b = st.columns([1.2, 1], gap='large')
        with a:
            acc = c.csv(P / 'validation_accuracy_sangrur_2025.csv')
            pipe = [('Sentinel-2 L2A', '18 five-day composites, 20 m',
                     f'{float(s25["mean_clear_share"]) * 100:.0f}% clear'),
                    ('NASA FIRMS', 'VIIRS on 3 satellites, and MODIS',
                     'no gaps' if s25['firms_gaps'] == 'none' else 'gaps')]
            if acc is not None:
                mapped = acc[acc['rule'].str.startswith('map as reported') & (acc['scored_on'] == 'all labelled points')]
                if len(mapped):
                    when = re.search(r'\((\d+ \w+ \d{4})\)', str(s25['rule_status']))
                    pipe.append(('Validation', f'{int(mapped["points"].iloc[0])} labelled points'
                                 + (f' · checked {when.group(1)}' if when else ''), f'F1 {mapped["f1"].iloc[0]:.2f}'))
            c.html('<div class="mc-card"><div class="mc-eyebrow">Data pipeline · 2025</div>'
                   + ''.join(f'<div class="mc-pipe"><i class="mc-dot"></i><div><strong>{x}</strong><em>{y}</em>'
                             f'</div><span class="mc-chip">{z}</span></div>' for x, y, z in pipe)
                   + '</div>')
        with b:
            c.html('<div class="mc-eyebrow">Sources</div>'
                   '<ul class="mc-src"><li>Sentinel-2 L2A (Copernicus), 20 m, 5-day composites</li>'
                   '<li>NASA FIRMS: VIIRS (Suomi NPP, NOAA-20, NOAA-21) and MODIS</li>'
                   '<li>District outline: geoBoundaries (ODbL 1.0)</li>'
                   '<li>Fire timing: iFOREST, as cited on the EO Analysis page</li></ul>')
            if grid is not None:
                cells = pd.DataFrame([f['properties'] for f in grid['features']])
                st.download_button('Download the 1 km grid (CSV)', cells.to_csv(index=False),
                                   'burnt_area_1km_sangrur_2025.csv', 'text/csv', icon=':material/download:')

c.labels_note()
c.footer('Every number on these pages is read from files the project\'s notebooks and scripts wrote.')
