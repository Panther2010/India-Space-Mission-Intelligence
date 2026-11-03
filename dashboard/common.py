"""Shared paths, cached loaders and small helpers for the dashboard pages.

The dashboard only reads what the notebooks and scripts have already written: tables in data/processed/, the
research datasets in data/raw/research/, the figures in maps/ and the drafts in report/ and methodology/. Nothing
heavy is computed while it runs.
"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / 'data' / 'processed'
RESEARCH = ROOT / 'data' / 'raw' / 'research'
MAPS = ROOT / 'maps'
REPORT = ROOT / 'report'
METHODOLOGY = ROOT / 'methodology'
STATIC = Path(__file__).resolve().parent / 'static'

AREA_LABEL = 'Sangrur (pre-2021 boundary)'
SEASONS = (2025, 2021)
CREDIT = ('Contains modified Copernicus Sentinel data 2021 and 2025. Fire detections: NASA FIRMS (VIIRS and MODIS). '
          'District outline: geoBoundaries (ODbL 1.0). Basemap: © OpenStreetMap contributors.')

# The palette, as in .streamlit/config.toml: night navy, the raised deck, rules, starlight and haze text, ember
# orange for burning and sky blue for satellite fire detections.
NIGHT, DECK, RULE, STAR, HAZE, EMBER, SKY = '#0b1322', '#121d31', '#22324c', '#e8eef7', '#93a5bf', '#ff7b39', '#4dabf7'

CSS = f"""<style>
[data-testid="stMetric"] {{ container-type: inline-size; }}
div[data-testid="stMetricValue"] {{ font-family: Rajdhani, sans-serif; letter-spacing: 0.01em;
  font-size: clamp(1.35rem, 14.5cqi, 2.3rem); }}
[data-testid="stMetricLabel"] [data-testid="stMarkdownContainer"], [data-testid="stMetricLabel"] p {{
  white-space: normal; overflow: visible; text-overflow: clip; line-height: 1.35; }}
[data-testid="stImage"] img {{ border-radius: 8px; }}
p.pbi-sub {{ color: {HAZE}; font-size: 1.06rem; line-height: 1.55; max-width: 46rem; margin: -0.6rem 0 1rem; }}
.st-key-hero {{ background: #0f1a2c; border: 1px solid {RULE}; border-radius: 16px; padding: 1.9rem 2.1rem 1.2rem; }}
.st-key-hero h1.pbi-headline {{ font-family: Rajdhani, sans-serif; font-weight: 700; color: {STAR};
  font-size: clamp(2.3rem, 3.7vw, 3.3rem); line-height: 1.0; letter-spacing: -0.005em; margin: 0.3rem 0 1.1rem;
  padding: 0; text-wrap: balance; }}
.st-key-hero p.pbi-lede {{ font-size: 1.1rem; line-height: 1.6; color: #c6d2e2; max-width: 31rem; }}
.st-key-hero p.pbi-where {{ color: {HAZE}; font-size: 0.95rem; margin: 0; }}
.pbi-key {{ display: flex; flex-wrap: wrap; gap: 0.35rem 1rem; align-items: center; color: {HAZE};
  font-size: 0.85rem; }}
.pbi-key span {{ display: inline-flex; align-items: center; gap: 0.45rem; }}
@media (max-width: 640px) {{ .st-key-hero {{ padding: 1.2rem 1rem 1.3rem; }} }}
</style>"""

# Inside the folium maps: OpenStreetMap tiles turned dark to sit on the navy page, and dark controls.
MAP_CSS = f"""<style>
.leaflet-container {{ background: {NIGHT}; }}
.leaflet-tile-pane {{ filter: invert(1) hue-rotate(180deg) brightness(0.82) contrast(0.92) saturate(0.35); }}
.leaflet-bar a, .leaflet-bar a:hover {{ background: {DECK}; color: {STAR}; border-bottom-color: {RULE}; }}
.leaflet-control-attribution {{ background: rgba(11, 19, 34, 0.82) !important; color: {HAZE}; font-size: 11px; }}
.leaflet-control-attribution a {{ color: #8cc8ff; }}
.leaflet-tooltip, .leaflet-popup-content-wrapper, .leaflet-popup-tip {{ background: {DECK} !important;
  color: {STAR} !important; border: 1px solid {RULE} !important; box-shadow: none !important; }}
.leaflet-popup-content a {{ color: #8cc8ff; }}
.leaflet-tooltip-top:before {{ border-top-color: {RULE}; }}
.leaflet-tooltip-bottom:before {{ border-bottom-color: {RULE}; }}
.leaflet-tooltip-left:before {{ border-left-color: {RULE}; }}
.leaflet-tooltip-right:before {{ border-right-color: {RULE}; }}
.marker-cluster-small, .marker-cluster-medium, .marker-cluster-large {{ background-color: rgba(255, 123, 57, 0.3); }}
.marker-cluster-small div, .marker-cluster-medium div, .marker-cluster-large div {{ background-color: {EMBER};
  color: {NIGHT}; font-weight: 600; }}
</style>"""


@st.cache_data(show_spinner=False)
def _read_csv(path, mtime):
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def _read_json(path, mtime):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def csv(path):
    """A CSV as a DataFrame, or None while the file doesn't exist. Re-read whenever the file changes."""
    path = Path(path)
    return _read_csv(str(path), path.stat().st_mtime) if path.exists() else None


def geojson(path):
    path = Path(path)
    return _read_json(str(path), path.stat().st_mtime) if path.exists() else None


def text(path):
    path = Path(path)
    return path.read_text(encoding='utf-8') if path.exists() else None


def summary(year):
    """Notebook 02's headline numbers for the whole district in one season, as metric -> value."""
    table = csv(PROCESSED / f's2_burn_summary_sangrur_{year}.csv')
    return None if table is None else table.set_index('metric')['value']


def comparison():
    """Notebook 02c's 2021 against 2025 table, indexed by measure."""
    table = csv(PROCESSED / 'season_comparison_sangrur.csv')
    return None if table is None else table.set_index('measure')


def ha(value):
    return f'{float(value):,.0f} ha'


def pct(value, digits=0):
    return f'{float(value) * 100:.{digits}f}%'


def change(value, digits=0):
    return f'{float(value) * 100:+.{digits}f}%'


def missing(path):
    st.info(f'`{Path(path).relative_to(ROOT).as_posix()}` is not there yet: run the notebook that writes it.')


def image(path, caption=None):
    path = Path(path)
    if path.exists():
        st.image(str(path), caption=caption)
    else:
        missing(path)


def style():
    """The page-wide styles: metric numbers in the heading face, and the front-page banner."""
    if hasattr(st, 'html'):
        st.html(CSS)
    else:                      # older Streamlit
        st.markdown(CSS, unsafe_allow_html=True)


def page_header(icon, title, subtitle=None):
    st.title(f':material/{icon}: {title}', anchor=False)
    if subtitle:
        st.markdown(f'<p class="pbi-sub">{subtitle}</p>', unsafe_allow_html=True)


def metric(where, label, value, delta=None, **kwargs):
    """A number card. Older Streamlit versions have no card border, so the number is shown without one."""
    try:
        where.metric(label, value, delta, border=True, **kwargs)
    except TypeError:
        where.metric(label, value, delta, **kwargs)


def district_bounds(boundary):
    """[[south, west], [north, east]] of a GeoJSON FeatureCollection."""
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


def dark_map(m):
    import folium
    m.get_root().header.add_child(folium.Element(MAP_CSS))
    return m


def show_map(m, height=560, key=None):
    from streamlit_folium import st_folium
    try:
        st_folium(m, height=height, use_container_width=True, returned_objects=[], key=key)
    except TypeError:          # older streamlit-folium, before use_container_width existed
        st_folium(m, height=height, width=None, returned_objects=[], key=key)


def labels_note():
    st.caption('Labels: **[Reported]** comes from a cited source, **[Ours]** was measured in this project, '
               '**[Recommendation]** is our judgement.')


def footer(extra=None):
    st.divider()
    st.caption(CREDIT if not extra else f'{extra} {CREDIT}')
