"""EO Analysis: the burnt-area map, what fire counts missed, 2021 against 2025, the ML classifier and the forecast."""
import altair as alt
import branca.colormap as bcm
import folium
from folium.plugins import HeatMap
import numpy as np
import pandas as pd
import streamlit as st

import common as c

st.title('EO Analysis')
st.markdown(f'**{c.AREA_LABEL}**: burnt area mapped from Sentinel-2 five-day composites, set against VIIRS fire '
            'detections. Every number is [Ours] unless marked otherwise.')

P = c.PROCESSED
LAYERS = {
    'Burnt area, confirmed': ('burnt_ha', 'ha', ['#fff5eb', '#fd8d3c', '#a63603']),
    'Burnt, with no VIIRS detection within 375 m': ('burnt_missed_ha', 'ha', ['#fee5d9', '#fb6a4a', '#99000d']),
    'Harvested and not seen burnt': ('harvested_not_burnt_ha', 'ha', ['#f7fcf5', '#74c476', '#00441b']),
    'When burning was first seen (average)': ('mean_burn_window_start', 'date', ['#ffffcc', '#fd8d3c', '#800026']),
    'When harvest was first seen (average)': ('mean_harvest_window_start', 'date', ['#ffffcc', '#41b6c4', '#253494']),
}
UNCONFIRMED = 'first seen from 19 Nov (unconfirmed)'
# Line colours with at least 3:1 contrast on both the light and the dark theme (backgrounds #ffffff and #0e1117),
# so a line never disappears into the page, whichever theme the viewer uses.
BLUE, ORANGE, GREY = '#2a78d6', '#e6550d', '#898781'


def district_bounds(boundary):
    xs, ys = [], []

    def walk(coords):
        if isinstance(coords[0], (int, float)):
            xs.append(coords[0])
            ys.append(coords[1])
        else:
            for part in coords:
                walk(part)
    for feature in boundary['features']:
        walk(feature['geometry']['coordinates'])
    return [[min(ys), min(xs)], [max(ys), max(xs)]]


def grid_map(grid, layer, boundary, fires):
    key, kind, colours = LAYERS[layer]
    for f in grid['features']:
        p = f['properties']
        value = p.get(key)
        if kind == 'date':
            p['_v'] = pd.Timestamp(value).dayofyear if value else None
        else:
            p['_v'] = float(value) if value else None
        for name in ('burnt_ha', 'burnt_missed_ha', 'harvested_not_burnt_ha'):
            p[f'_{name}'] = f"{p.get(name) or 0:,.0f} ha"
        for name in ('mean_harvest_window_start', 'mean_burn_window_start'):
            p[f'_{name}'] = pd.Timestamp(p[name]).strftime('%d %b') if p.get(name) else '–'
    values = np.array([f['properties']['_v'] for f in grid['features'] if f['properties']['_v']], float)
    if kind == 'date':
        low, high = values.min(), values.max()
        year = pd.Timestamp(next(f['properties'][key] for f in grid['features'] if f['properties'][key])).year
        start = pd.Timestamp(year=year, month=1, day=1)
        ends = tuple(f'{start + pd.Timedelta(day - 1, unit="D"):%d %b}' for day in (low, high))
        caption = 'average 5-day window in which it was first seen, in each 1 km square'
    else:
        low, high = 0.0, max(float(np.quantile(values, 0.98)), 1.0)
        ends = ('0 ha', f'{high:,.0f} ha or more')
        caption = 'hectares in each 1 km square (a whole square is 100 ha)'
    cmap = bcm.LinearColormap(colours, vmin=low, vmax=high)

    m = folium.Map(tiles='OpenStreetMap')
    folium.GeoJson(
        grid, name=layer,
        style_function=lambda f: {'fillColor': cmap(min(f['properties']['_v'], high)) if f['properties']['_v']
                                  else 'transparent', 'fillOpacity': 0.8 if f['properties']['_v'] else 0,
                                  'weight': 0},
        tooltip=folium.GeoJsonTooltip(
            fields=['_burnt_ha', '_burnt_missed_ha', '_harvested_not_burnt_ha', '_mean_harvest_window_start',
                    '_mean_burn_window_start'],
            aliases=['Burnt (confirmed)', 'No VIIRS detection within 375 m', 'Harvested, not seen burnt',
                     'Harvest first seen (average window)', 'Burning first seen (average window)']),
    ).add_to(m)
    folium.GeoJson(boundary, name='District', style_function=lambda f: {'color': '#222222', 'weight': 1.5,
                                                                         'fillOpacity': 0}).add_to(m)
    if fires is not None and len(fires):
        if len(fires) <= 3000:
            layer_group = folium.FeatureGroup(name='VIIRS detections')
            for lat, lon in zip(fires['latitude'], fires['longitude']):
                folium.CircleMarker((lat, lon), radius=2, color='#3b0f70', fill=True, fill_opacity=0.9,
                                    weight=0).add_to(layer_group)
            layer_group.add_to(m)
        else:
            HeatMap(fires[['latitude', 'longitude']].to_numpy().tolist(), name='VIIRS detections', radius=7,
                    blur=5, min_opacity=0.3).add_to(m)
    m.fit_bounds(district_bounds(boundary))
    return m, (colours, ends, caption)


def legend(colours, ends, caption):
    # Drawn by the page, not inside the map, so it needs no extra scripts from the web.
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;font-size:0.85rem">'
        f'<span>{ends[0]}</span><div style="flex:0 0 220px;height:12px;border-radius:2px;'
        f'background:linear-gradient(to right,{",".join(colours)})"></div><span>{ends[1]}</span>'
        f'<span style="opacity:0.7">· {caption}</span></div>', unsafe_allow_html=True)


def by_window_chart(bw):
    rows = []
    for _, r in bw.iterrows():
        label = pd.Timestamp(r['window_start']).strftime('%d %b')
        if r['burns_confirmed']:
            rows += [(label, 'flagged by VIIRS within 375 m', r['burnt_flagged_ha']),
                     (label, 'no VIIRS detection within 375 m', r['burnt_missed_ha'])]
        else:
            rows.append((label, UNCONFIRMED, r['burnt_ha']))
    long = pd.DataFrame(rows, columns=['window', 'burns', 'hectares'])
    order = [pd.Timestamp(d).strftime('%d %b') for d in bw['window_start']]
    bars = alt.Chart(long).mark_bar().encode(
        x=alt.X('window:O', sort=order, title='5-day window starting'),
        y=alt.Y('hectares:Q', title='burnt area first seen (ha)'),
        color=alt.Color('burns:N', title=None, legend=alt.Legend(orient='bottom', labelLimit=400),
                        scale=alt.Scale(domain=['flagged by VIIRS within 375 m', 'no VIIRS detection within 375 m',
                                                UNCONFIRMED], range=['#fdae6b', '#cb181d', '#9e9ac8'])),
        tooltip=['window', 'burns', alt.Tooltip('hectares:Q', format=',.0f')])
    fires = bw.assign(window=order)
    line = alt.Chart(fires).mark_line(color=BLUE, strokeWidth=2,
                                      point=alt.OverlayMarkDef(color=BLUE, filled=True, size=40)).encode(
        x=alt.X('window:O', sort=order), y=alt.Y('viirs_detections_inside:Q', title='VIIRS detections (line)'),
        tooltip=['window', alt.Tooltip('viirs_detections_inside:Q', title='VIIRS detections')])
    return alt.layer(bars, line).resolve_scale(y='independent').properties(height=360, width='container')


tab_map, tab_missed, tab_change, tab_ml, tab_forecast = st.tabs(
    ['Burnt-area map', 'What fire counts missed', '2021 against 2025', 'ML classifier', '2026 forecast'])

# --- The map -----------------------------------------------------------------------------------------------------
with tab_map:
    season = st.radio('Season', c.SEASONS, horizontal=True, key='map_season')
    s = c.summary(season)
    grid = c.geojson(P / f's2_burn_grid_1km_sangrur_{season}.geojson')
    boundary = c.geojson(P / 'boundary_sangrur_pre2021.geojson')
    if s is None or grid is None or boundary is None:
        c.missing(P / f's2_burn_grid_1km_sangrur_{season}.geojson')
    else:
        cols = st.columns(5)
        cols[0].metric('Harvested in the season', c.ha(s['harvested_ha']))
        cols[1].metric('Burnt, confirmed', c.ha(s['burnt_ha']))
        cols[2].metric('Share of the harvest burnt', c.pct(s['burnt_share_of_harvested']))
        cols[3].metric('Late burns, from 19 Nov', c.ha(s['burnt_unconfirmed_ha']),
                       help='Mapped but unconfirmed: late in the season, damp soil under a young crop can look '
                            'like a burn (decision log, 30 Oct 2026).')
        cols[4].metric('Harvest to burn, median', f"{float(s['median_days_harvest_to_burn']):.0f} days")
        left, right = st.columns([2, 1])
        layer = left.selectbox('Colour the 1 km squares by', list(LAYERS))
        show_fires = right.checkbox('Show VIIRS fire detections', value=season == 2025,
                                    help='Detections inside the district from every VIIRS satellite flying that '
                                         'season. Shown as a heat map when there are more than 3,000.')
        fires = None
        if show_fires:
            det = c.csv(P / f'firms_detections_sangrur_{season}.csv')
            if det is not None:
                fires = det[det['inside'] & det['sensor'].str.startswith('VIIRS')]
        m, key_info = grid_map(grid, layer, boundary, fires)
        legend(*key_info)
        c.show_map(m, key=f'map_{season}_{layer}_{show_fires}')
        st.caption('For the straw buyer, the green layer is the harvested area not seen burnt, and the timing layers '
                   'show when harvest and burning moved through the district. For the department, the red layers '
                   'show where burning was, and where fire counts missed it. Hover over a square for its numbers.')
        with st.expander('The 20 m map'):
            figure = (c.MAPS / 'qgis' / '01_burnt_area_2025.png' if season == 2025
                      else c.MAPS / 'notebook02' / '2021' / '04_burnt_area_map.png')
            c.image(figure, caption=f'{c.AREA_LABEL}, {season}: every 20 m pixel')

# --- What fire counts missed ---------------------------------------------------------------------------------------
with tab_missed:
    season = st.radio('Season', c.SEASONS, horizontal=True, key='missed_season')
    s = c.summary(season)
    bw = c.csv(P / f's2_burn_by_window_sangrur_{season}.csv')
    if s is None or bw is None:
        c.missing(P / f's2_burn_by_window_sangrur_{season}.csv')
    else:
        st.markdown('A burnt pixel counts as **flagged** when a fire detection lies near it at the right time: between '
                    'its last clear view before the burn and the 5-day window in which the burn shows. The share of '
                    'confirmed burnt area left unflagged is the **missed share**, under three rules for "near":')
        cols = st.columns(4)
        cols[0].metric('VIIRS within 375 m (strict)', c.pct(s['missed_share_viirs_375m']))
        cols[1].metric('VIIRS within 750 m', c.pct(s['missed_share_viirs_750m']))
        cols[2].metric('VIIRS within 750 m or MODIS within 1 km', c.pct(s['missed_share_viirs_750m_or_modis_1000m']))
        cols[3].metric('Strict, with the late burns', c.pct(s['missed_share_viirs_375m_including_unconfirmed']))
        st.altair_chart(by_window_chart(bw))
        satellites = 'Suomi NPP, NOAA-20 and NOAA-21' if 'NOAA21' in str(s['firms_products']) else \
            'Suomi NPP and NOAA-20 (NOAA-21 was launched in November 2022)'
        st.caption(f'VIIRS satellites in {season}: {satellites}. Burnt area is counted in the window in which a '
                   'burn is first seen; fire detections in the window in which they were made. The two seasons are '
                   'compared on the same two satellites in the next tab.')

# --- 2021 against 2025 ---------------------------------------------------------------------------------------------
with tab_change:
    comp = c.comparison()
    if comp is None:
        c.missing(P / 'season_comparison_sangrur.csv')
    else:
        def pair(measure):
            return comp.loc[measure, '2021'], comp.loc[measure, '2025']

        burnt21, burnt25 = pair('burnt area, confirmed (ha)')
        fires21, fires25 = pair('Suomi NPP detections inside')
        miss21, miss25 = pair('missed share, Suomi NPP and NOAA-20 only (375 m)')
        cols = st.columns(4)
        cols[0].metric('Burnt area, confirmed, 2025', c.ha(burnt25), c.change(burnt25 / burnt21 - 1) + ' since 2021',
                       delta_color='off')
        cols[1].metric('Suomi NPP detections, 2025', f'{fires25:,.0f}', c.change(fires25 / fires21 - 1) + ' since 2021',
                       delta_color='off')
        cols[2].metric('No fire seen nearby, 2025', c.pct(miss25),
                       f'{(miss25 - miss21) * 100:+.0f} points since 2021', delta_color='off',
                       help='Suomi NPP and NOAA-20 only, the two VIIRS satellites flying in both seasons; 375 m.')
        if 'burnt share of land harvested in both seasons' in comp.index:
            same21, same25 = pair('burnt share of land harvested in both seasons')
            cols[3].metric('Burnt share, same fields, 2025', c.pct(same25),
                           f'{(same25 - same21) * 100:+.0f} points since 2021', delta_color='off',
                           help='Burnt share of the land harvested in both seasons, so the same fields are compared.')
        st.markdown(f'Burning fell by about {1 - burnt25 / burnt21:.0%} while fire detections fell '
                    f'{1 - fires25 / fires21:.0%}, so fire counts overstate the fall in burning. In 2025 they missed '
                    f'most of it. The 2021 map has no labels of its own, and the cause of the gap (later burning, '
                    'smaller or shorter fires, partial burns) cannot be told from these data.')
        left, right = st.columns(2)
        with left:
            c.image(c.MAPS / 'notebook02c' / '01_change_2021_2025.png')
            c.image(c.MAPS / 'notebook02c' / '02_timing.png')
        with right:
            c.image(c.MAPS / 'notebook02c' / '03_change_map.png')
            bands = c.csv(P / 'season_comparison_by_band_sangrur.csv')
            if bands is not None:
                st.markdown('**South to north** (four bands with equal numbers of 1 km squares)')
                st.dataframe(bands, hide_index=True, column_config={
                    col: st.column_config.NumberColumn(format='%.0f' if '(ha)' in col else '%.2f')
                    for col in bands.columns if col != 'band'})
        with st.expander('Every measure, both seasons'):
            st.dataframe(comp.reset_index())

# --- ML classifier -------------------------------------------------------------------------------------------------
with tab_ml:
    acc = c.csv(P / 'ml_accuracy_sangrur_2025.csv')
    if acc is None:
        c.missing(P / 'ml_accuracy_sangrur_2025.csv')
    else:
        st.markdown('Does a classifier trained on the 2025 validation labels map burnt fields better than the '
                    'three-threshold rule? A Random Forest learned from 147 labelled points on harvested fields '
                    '(Notebook 03).')
        cols = st.columns(3)
        rule = acc[(acc['method'] == 'rule: map as reported') & (acc['scored_on'] == 'all labelled points')]
        forest = acc[acc['scored_on'].str.contains('mean of')]
        if len(rule):
            cols[0].metric('Burn rule, F1 on all labelled points', f"{rule['f1'].iloc[0]:.2f}")
        if len(forest):
            cols[1].metric('Random Forest, F1 (cross-validated)', f"{forest['f1'].iloc[0]:.2f}")
        mapcomp = c.csv(P / 'ml_map_comparison_sangrur_2025.csv')
        if mapcomp is not None:
            area = mapcomp.set_index('measure')['value']
            cols[2].metric('Burnt area: forest map / rule map', f"{area['burnt in the forest map (ha)']:,.0f} / "
                           f"{area['burnt in the rule map, as reported (ha)']:,.0f} ha")
        models = c.csv(P / 'ml_model_comparison_sangrur_2025.csv')
        if models is not None:
            st.markdown('**Other classifiers under the same cross-validation** (default settings, nothing tuned):')
            st.dataframe(models[['method', 'f1_mean', 'f1_min', 'f1_max', 'precision_mean', 'recall_mean',
                                 'mcnemar_p_min', 'mcnemar_p_max']], hide_index=True, column_config={
                'method': 'Method', 'f1_mean': st.column_config.NumberColumn('F1, mean', format='%.2f'),
                'f1_min': st.column_config.NumberColumn('F1, lowest run', format='%.2f'),
                'f1_max': st.column_config.NumberColumn('F1, highest run', format='%.2f'),
                'precision_mean': st.column_config.NumberColumn('Precision', format='%.2f'),
                'recall_mean': st.column_config.NumberColumn('Recall', format='%.2f'),
                'mcnemar_p_min': st.column_config.NumberColumn('McNemar p, lowest', format='%.2f'),
                'mcnemar_p_max': st.column_config.NumberColumn('McNemar p, highest', format='%.2f')})
        left, right = st.columns(2)
        with left:
            importance = c.csv(P / 'ml_feature_importance_sangrur_2025.csv')
            if importance is not None:
                groups = importance[importance['kind'] == 'group']
                st.altair_chart(alt.Chart(groups).mark_bar(color='#e15759').encode(
                    x=alt.X('f1_drop_mean:Q', title='drop in F1 when the group is shuffled'),
                    y=alt.Y('name:N', sort='-x', title=None, axis=alt.Axis(labelLimit=320)),
                    tooltip=['name', alt.Tooltip('f1_drop_mean:Q', format='.3f'), 'features']).properties(
                    title='What the forest relies on', width='container'))
            st.markdown('**Decision:** the rule\'s map stays. No model beats it at the labelled points, and the rule '
                        'needs no labels to train, is easier to explain and carries to another season unchanged '
                        '(decision log, 31 Oct 2026). [Recommendation]')
        with right:
            c.image(c.MAPS / 'notebook03' / '04_agreement_map.png', caption='Where the forest\'s map and the rule\'s '
                    'agree')

# --- 2026 forecast -------------------------------------------------------------------------------------------------
with tab_forecast:
    fc, summ = c.csv(P / 'fire_forecast_2026.csv'), c.csv(P / 'fire_forecast_2026_summary.csv')
    check = c.csv(P / 'fire_forecast_check_2026.csv')
    if fc is None or summ is None:
        c.missing(P / 'fire_forecast_2026.csv')
    else:
        area = st.radio('Area', ['Punjab', 'Sangrur'], horizontal=True, key='forecast_area')
        head = summ[(summ['area'] == area) & summ['headline']].iloc[0]
        cols = st.columns(4)
        cols[0].metric(f"Suomi NPP detections to {pd.Timestamp(head['data_through']):%d %b}",
                       f"{head['seen_so_far']:,.0f}")
        cols[1].metric('Forecast for the rest of the season', f"{head['forecast_rest']:,.0f}",
                       help=f"80% range {head['rest_low']:,.0f}–{head['rest_high']:,.0f}")
        cols[2].metric('Season forecast / last season', f"{head['forecast_season']:,.0f} / {head['last_season']:,.0f}")
        dates = str(head['peak_week_dates'])
        cols[3].metric('Busiest week, most likely', f"Week {int(head['peak_week'])}",
                       help=f"{dates}, in {head['peak_week_share']:.0%} of the scenarios")
        rows = fc[fc['area'] == area]
        happened = rows[rows['headline'] & rows['seen'].notna()][['week', 'seen']].rename(
            columns={'seen': 'detections'})
        done = pd.DataFrame()
        if check is not None:
            done = check[(check['area'] == area) & check['actual'].notna()]
            happened = pd.concat([happened, done[['week']].assign(detections=done['actual'])], ignore_index=True)
        happened['series'] = '2026, what happened'
        lines = rows[rows['forecast'].notna()][['week', 'method', 'forecast', 'headline']].rename(
            columns={'forecast': 'detections'})
        lines['series'] = 'forecast: ' + lines['method'] + np.where(lines['headline'], ' (headline)', '')
        data = pd.concat([happened, lines[['week', 'detections', 'series']]], ignore_index=True)
        series = list(dict.fromkeys(data['series']))
        # What happened in blue and the headline forecast in orange; the other forecasts in grey, told apart by dashes.
        dashes = iter([[6, 4], [2, 3]])
        looks = [(BLUE, [1, 0], 3) if s.startswith('2026') else (ORANGE, [1, 0], 2) if '(headline)' in s
                 else (GREY, next(dashes, [6, 4]), 1.5) for s in series]
        colours, strokes, widths = (list(v) for v in zip(*looks))
        legend = alt.Legend(orient='bottom', labelLimit=400, columns=2, symbolType='stroke', symbolStrokeWidth=2.5)
        chart = alt.Chart(data).mark_line(point=alt.OverlayMarkDef(filled=True, size=30)).encode(
            x=alt.X('week:O', title='week of the season (week 1 starts 15 Sep)', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('detections:Q', title='Suomi NPP detections per week'),
            color=alt.Color('series:N', title=None, scale=alt.Scale(domain=series, range=colours), legend=legend),
            strokeDash=alt.StrokeDash('series:N', title=None, scale=alt.Scale(domain=series, range=strokes),
                                      legend=legend),
            strokeWidth=alt.StrokeWidth('series:N', scale=alt.Scale(domain=series, range=widths), legend=None),
            tooltip=['series', 'week', alt.Tooltip('detections:Q', format=',.0f')],
        ).properties(height=380, width='container')
        st.altair_chart(chart)
        st.caption(f"Forecast issued on {pd.Timestamp(head['issued_on']):%d %b %Y} from the weeks to "
                   f"{pd.Timestamp(head['data_through']):%d %b} (week {int(head['issue_week'])}), with the method "
                   f"that did best in backtests over 2021–2025 ({head['method']}). It is never changed afterwards. "
                   "The last-season forecast repeats 2025's weeks.")
        if done.empty:
            st.info('No week after the forecast has been checked in the committed data yet.')
        else:
            name = head['method']
            ratio = np.where(done['actual'] > 0, done[name] / done['actual'].where(done['actual'] > 0), np.nan)
            st.markdown(f"**Weeks checked so far** (to week {int(done['week'].max())}, from the last committed run of "
                        'Notebook 04; the check is committed after each weekly run)')
            st.dataframe(pd.DataFrame({
                'week': done['week'],
                'dates': [f'{pd.Timestamp(a):%d %b}–{pd.Timestamp(b):%d %b}'
                          for a, b in zip(done['week_start'], done['week_end'])],
                'what happened': done['actual'], 'counted from': done['actual_source'],
                'headline forecast': done[name], 'forecast ÷ what happened': ratio,
            }), hide_index=True, column_config={
                'what happened': st.column_config.NumberColumn(format='%.0f'),
                'headline forecast': st.column_config.NumberColumn(format='%.0f'),
                'forecast ÷ what happened': st.column_config.NumberColumn(format='%.2f'),
            })
            st.caption('After 2 Nov, Suomi NPP data stopped, so later weeks are counted from NOAA-20 and converted to '
                       'Suomi NPP terms with the two sensors\' 2026 ratio. A ratio above 1 means the forecast was too '
                       'high.')

c.footer()
