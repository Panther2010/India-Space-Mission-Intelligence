"""Shared paths, cached loaders, the look and small helpers for the dashboard pages.

The dashboard only reads what the notebooks and scripts have already written: tables in data/processed/, the
research datasets in data/raw/research/, the figures in maps/ and the drafts in report/ and methodology/. Nothing
heavy is computed while it runs.
"""
import base64
import html as markup
import json
import math
import re
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / 'data' / 'processed'
RESEARCH = ROOT / 'data' / 'raw' / 'research'
MAPS = ROOT / 'maps'
REPORT = ROOT / 'report'
METHODOLOGY = ROOT / 'methodology'
STATIC = Path(__file__).resolve().parent / 'static'
ICONS = STATIC / 'icons'

AREA_LABEL = 'Sangrur (pre-2021 boundary)'
SEASONS = (2025, 2021)
CREDIT = ('Contains modified Copernicus Sentinel data 2021 and 2025. Fire detections: NASA FIRMS (VIIRS and MODIS). '
          'District outline: geoBoundaries (ODbL 1.0). Basemap: © OpenStreetMap contributors. '
          'Icons: Lucide (ISC licence).')

# The palette, as in .streamlit/config.toml: the near-black page, panels and tiles, the hairline rules, starlight,
# soft and haze text, ember orange for burning, sky blue for satellite fire detections, green for harvested land not
# seen burnt, amber and red for warnings and violet for explanations. The same values are in CSS below.
NIGHT, PANEL, DECK, RULE = '#090b0f', '#0f1217', '#151a22', '#242b36'
STAR, SOFT, HAZE = '#e9edf3', '#c9d1dc', '#9aa5b4'
EMBER, SKY, GREEN, AMBER, RED, VIOLET = '#ff7b39', '#4dabf7', '#3ecf74', '#f5a524', '#f0534a', '#a78bfa'

# Chart text in px, which doesn't follow the app's base size: set here to match the 18 px text. Charts have no
# background of their own, so they sit on whichever panel holds them.
CHART_FONTS = {'config': {
    'background': 'transparent',
    'view': {'continuousWidth': 300, 'continuousHeight': 300},     # Altair's default size, kept
    'axis': {'labelFontSize': 14, 'titleFontSize': 15},
    'legend': {'labelFontSize': 14, 'titleFontSize': 15},
    'title': {'fontSize': 17},
    'text': {'fontSize': 14},
}}
try:
    alt.theme.register('pbi', enable=True)(lambda: CHART_FONTS)
except AttributeError:                         # Altair before 5.5
    alt.themes.register('pbi', lambda: CHART_FONTS)
    alt.themes.enable('pbi')

# The page-wide styles. Streamlit's own parts are found by their data-testid names, which can change between
# Streamlit versions, so dashboard/requirements.txt pins the version these were checked with.
CSS = """<style>
:root { --night:#090b0f; --panel:#0f1217; --tile:#151a22; --line:#242b36; --text:#e9edf3; --soft:#c9d1dc;
  --muted:#9aa5b4; --ember:#ff7b39; --sky:#4dabf7; --green:#3ecf74; --amber:#f5a524; --red:#f0534a; --violet:#a78bfa;
  --mono:'JetBrains Mono', ui-monospace, monospace; }

/* The page: a black gradient, a little lighter at the top, under a glass top bar */
.stApp { background-color:var(--night);
  background-image:radial-gradient(1200px 640px at 50% -8%, rgba(148,163,184,.10), transparent 62%),
                   linear-gradient(180deg, #11151c 0%, #0a0c10 34%, #060709 72%, #040506 100%);
  background-attachment:fixed; }
[data-testid="stHeader"] { background:rgba(10,12,16,.72); backdrop-filter:blur(12px); -webkit-backdrop-filter:blur(12px);
  border-bottom:1px solid rgba(255,255,255,.05); }
[data-testid="stMainBlockContainer"] { padding:5.2rem 2.4rem 3rem; max-width:1480px; }
@media (max-width:640px) { [data-testid="stMainBlockContainer"] { padding:4.6rem 1rem 2.5rem; } }
[data-testid="stTopNavLink"] { font-size:14.5px; }
[data-testid="stImage"] img { border-radius:10px; }

/* Number cards drawn by Streamlit, made to match the tiles */
[data-testid="stMetric"] { container-type:inline-size; padding:.85rem 1rem .95rem; border:1px solid var(--line);
  border-radius:14px; background:linear-gradient(180deg, #151a22, #11151c); }
div[data-testid="stMetricValue"] { font-family:Rajdhani, sans-serif; letter-spacing:.01em;
  font-size:clamp(1.35rem, 14.5cqi, 2.3rem); }
[data-testid="stMetricLabel"] [data-testid="stMarkdownContainer"], [data-testid="stMetricLabel"] p {
  white-space:normal; overflow:visible; text-overflow:clip; line-height:1.35; }
[data-testid="stMetricLabel"] p { font-family:var(--mono); font-size:12.5px; letter-spacing:.05em;
  text-transform:uppercase; color:var(--muted); }

/* The header panel at the top of each page */
[class*="st-key-hero_"] { padding:1.8rem 2.1rem 1.5rem; border:1px solid var(--line); border-radius:22px;
  background:radial-gradient(60% 120% at 85% 0%, rgba(148,163,184,.07), transparent 70%),
             linear-gradient(180deg, rgba(17,21,28,.94), rgba(11,14,19,.94)); }
.st-key-hero_overview { background:radial-gradient(42% 75% at 76% 50%, rgba(255,123,57,.11), transparent 72%),
             linear-gradient(180deg, rgba(17,21,28,.94), rgba(11,14,19,.94)); }
.mc-hero-top { display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:.6rem 1rem; }
h1.mc-title-xl { margin:.8rem 0 .35rem; padding:0; font-family:Rajdhani, sans-serif; font-weight:700;
  font-size:clamp(40px, 4.2vw, 62px); line-height:.95; letter-spacing:.01em; text-transform:uppercase; color:var(--text); }
p.mc-lede { margin:0; max-width:48rem; font-size:18px; line-height:1.55; color:var(--soft); }
.mc-pill { padding:.3rem .8rem; border:1px solid var(--line); border-radius:999px; background:rgba(255,255,255,.02);
  font-family:var(--mono); font-size:12.5px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted);
  white-space:nowrap; }
.mc-pill b { color:var(--text); font-weight:500; }
.mc-big { display:flex; flex-wrap:wrap; align-items:center; gap:1rem 1.4rem; margin:1.7rem 0 1.2rem; }
.mc-big > b { font-family:Rajdhani, sans-serif; font-weight:700; font-size:clamp(64px, 6.6vw, 100px); line-height:.85;
  color:var(--red); text-shadow:0 0 30px rgba(240,83,74,.35); font-variant-numeric:tabular-nums; }
.mc-big p { margin:0; max-width:12.5rem; font-size:17px; line-height:1.45; color:var(--soft); }

/* Panels and cards */
[class*="st-key-panel_"] { padding:1.15rem 1.5rem 1.4rem; border:1px solid var(--line); border-radius:22px;
  background:linear-gradient(180deg, rgba(16,20,26,.94), rgba(11,14,19,.94)); }
[class*="st-key-card_"], .mc-card { padding:1rem 1.15rem 1.05rem; border:1px solid var(--line); border-radius:16px;
  background:#11151c; }
/* Cards side by side end level */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-card_"]) { flex:1 1 auto; }
@media (max-width:640px) { [class*="st-key-hero_"] { padding:1.2rem 1.1rem 1.1rem; }
  .st-key-hero_overview { background:linear-gradient(180deg, rgba(17,21,28,.94), rgba(11,14,19,.94)); }
  [class*="st-key-panel_"] { padding:1rem .9rem 1.1rem; } }

/* Small capital labels, chips and status dots */
.mc-eyebrow { display:block; font-family:var(--mono); font-size:13px; letter-spacing:.1em; text-transform:uppercase;
  color:var(--muted); }
.mc-eyebrow b { font-weight:600; }
.mc-eyebrow img { vertical-align:-3px; margin-right:.45rem; }
.mc-ok { color:var(--green); } .mc-warn { color:var(--amber); } .mc-alert { color:var(--red); }
.mc-small { margin-top:.45rem; font-family:var(--mono); font-size:12.5px; line-height:1.55; letter-spacing:.03em;
  color:var(--muted); }
.mc-dot { display:inline-block; width:8px; height:8px; margin-right:.55rem; vertical-align:1px; border-radius:50%;
  background:var(--green); box-shadow:0 0 10px var(--green); animation:mc-pulse 2.4s ease-in-out infinite; }
.mc-dot.amber { background:var(--amber); box-shadow:0 0 10px var(--amber); }
.mc-dot.plain { background:var(--muted); box-shadow:none; }
@keyframes mc-pulse { 50% { opacity:.35; } }
.mc-chip { padding:2px 8px; border-radius:999px; background:rgba(255,255,255,.06); font-family:var(--mono);
  font-size:12.5px; letter-spacing:.03em; white-space:nowrap; color:var(--soft); }
.mc-chip.down { color:var(--green); } .mc-chip.up { color:var(--amber); }

/* Tiles: an icon, a chip, a big number and what it is */
.mc-grid { display:grid; gap:14px; grid-template-columns:repeat(4, minmax(0,1fr)); }
.mc-grid.mc-cols-2 { grid-template-columns:repeat(2, minmax(0,1fr)); }
.mc-grid.mc-cols-3 { grid-template-columns:repeat(3, minmax(0,1fr)); }
.mc-grid.mc-cols-5 { grid-template-columns:repeat(5, minmax(0,1fr)); }
@media (max-width:1000px) { .mc-grid.mc-cols-3, .mc-grid.mc-cols-4, .mc-grid.mc-cols-5 {
  grid-template-columns:repeat(2, minmax(0,1fr)); } }
.mc-tile { container-type:inline-size; position:relative; overflow:hidden; display:flex; flex-direction:column;
  min-height:140px; padding:13px 15px 15px; border:1px solid var(--line); border-radius:14px; background:var(--tile);
  transition:transform .18s ease, border-color .18s ease; }
.mc-tile:hover { transform:translateY(-2px); border-color:rgba(255,255,255,.2); }
.mc-tile-top { display:flex; flex-wrap:wrap; justify-content:space-between; align-items:flex-start; gap:6px .5rem; }
.mc-ic { display:grid; place-items:center; flex:none; width:34px; height:34px; border-radius:50%;
  background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.09); }
.mc-num { margin-top:auto; padding-top:14px; font-family:Rajdhani, sans-serif; font-weight:700; font-size:44px;
  line-height:1; color:var(--text); font-variant-numeric:tabular-nums; }
.mc-tile .mc-num { font-size:clamp(28px, 24cqi, 44px); }
.mc-num small { margin-left:3px; font-size:20px; font-weight:600; color:var(--soft); }
.mc-label { margin-top:4px; font-size:15.5px; line-height:1.3; color:var(--soft); }
@container (max-width:210px) { .mc-vs { display:none; } .mc-chip { white-space:normal; } }
.mc-glow-ember { border-color:rgba(255,123,57,.55); box-shadow:0 0 26px rgba(255,123,57,.13);
  background:radial-gradient(125% 105% at 18% 0%, rgba(255,123,57,.55), rgba(255,123,57,.13) 52%, var(--tile) 82%); }
.mc-glow-red { border-color:rgba(240,83,74,.55); box-shadow:0 0 26px rgba(240,83,74,.13);
  background:radial-gradient(125% 105% at 18% 0%, rgba(240,83,74,.55), rgba(240,83,74,.13) 52%, var(--tile) 82%); }
.mc-glow-green { border-color:rgba(62,207,116,.45); box-shadow:0 0 26px rgba(62,207,116,.10);
  background:radial-gradient(125% 105% at 18% 0%, rgba(62,207,116,.42), rgba(62,207,116,.10) 52%, var(--tile) 82%); }
.mc-glow-amber { border-color:rgba(245,165,36,.5); box-shadow:0 0 26px rgba(245,165,36,.11);
  background:radial-gradient(125% 105% at 18% 0%, rgba(245,165,36,.48), rgba(245,165,36,.11) 52%, var(--tile) 82%); }
.mc-glow-sky { border-color:rgba(77,171,247,.5); box-shadow:0 0 26px rgba(77,171,247,.11);
  background:radial-gradient(125% 105% at 18% 0%, rgba(77,171,247,.42), rgba(77,171,247,.10) 52%, var(--tile) 82%); }
.mc-glow-violet { border-color:rgba(167,139,250,.5); box-shadow:0 0 26px rgba(167,139,250,.11);
  background:radial-gradient(125% 105% at 18% 0%, rgba(167,139,250,.42), rgba(167,139,250,.10) 52%, var(--tile) 82%); }

/* A ring gauge with its value inside */
.mc-ring { position:relative; flex:none; width:78px; text-align:center; }
.mc-ring img { display:block; }
.mc-ring b { position:absolute; top:0; left:0; display:grid; place-items:center; width:78px; height:78px;
  font-family:Rajdhani, sans-serif; font-weight:700; font-size:19px; color:var(--sky); }
.mc-ring span { display:block; margin-top:2px; font-family:var(--mono); font-size:12px; letter-spacing:.1em; color:var(--muted); }

/* Rows with a status, three cells and a progress bar */
.mc-row { margin-top:.7rem; padding:10px 12px 12px; border:1px solid var(--line); border-radius:14px; background:#11151c; }
.mc-row-head { display:flex; align-items:center; gap:.7rem; }
.mc-row-head div { flex:1; line-height:1.25; }
.mc-row-head strong { display:block; font-size:16px; font-weight:600; color:var(--text); }
.mc-row-head em { font-style:normal; font-family:var(--mono); font-size:12.5px; }
.mc-cells { display:grid; grid-template-columns:auto minmax(0,1fr) auto; gap:6px; margin-top:.6rem; }
.mc-cells > div { padding:7px 8px; border:1px solid var(--line); border-radius:10px; background:#0d1116; }
.mc-cells b { display:block; text-align:center; font-family:Rajdhani, sans-serif; font-weight:700; font-size:24px;
  line-height:1; color:var(--text); }
.mc-cells span { display:block; margin-top:3px; text-align:center; font-family:var(--mono); font-size:11.5px;
  letter-spacing:.04em; text-transform:uppercase; color:var(--muted); }
.mc-prog span { display:flex; justify-content:space-between; margin:0 0 9px; text-align:left; }
.mc-prog i { display:block; height:5px; overflow:hidden; border-radius:99px; background:#1d232d; }
.mc-prog i u { display:block; height:100%; border-radius:99px; text-decoration:none; }

/* Bars with a label and a value */
.mc-rule { display:grid; grid-template-columns:1fr auto; align-items:end; gap:.25rem .8rem; margin-top:1rem; }
.mc-rule span { font-size:15.5px; color:var(--soft); }
.mc-rule b { font-family:Rajdhani, sans-serif; font-weight:700; font-size:28px; line-height:1; color:var(--text); }
.mc-rule i { grid-column:1 / -1; display:block; height:6px; overflow:hidden; border-radius:99px; background:#1d232d; }
.mc-rule i u { display:block; height:100%; border-radius:99px; text-decoration:none; }

/* A note that explains, a list with status dots, a plain table and a source list */
.mc-insight { padding:14px 16px; border:1px solid rgba(167,139,250,.45); border-radius:16px; box-shadow:0 0 30px rgba(167,139,250,.10);
  background:radial-gradient(90% 140% at 0% 0%, rgba(167,139,250,.20), rgba(167,139,250,.04) 60%, transparent), #12141c; }
.mc-insight .mc-eyebrow { color:#c4b5fd; }
.mc-insight p { margin:.45rem 0 0; font-size:16px; line-height:1.5; color:var(--soft); }
.mc-badge { display:inline-grid; place-items:center; width:30px; height:30px; margin-right:.5rem; vertical-align:middle;
  border-radius:50%; background:rgba(167,139,250,.16); border:1px solid rgba(167,139,250,.45); }
.mc-badge img { margin:0; vertical-align:0; }
.mc-pipe { display:flex; align-items:center; gap:.7rem; padding:.55rem 0; border-bottom:1px solid #1a2029; }
.mc-pipe:last-child { border-bottom:none; }
.mc-pipe div { flex:1; line-height:1.3; }
.mc-pipe strong { display:block; font-size:15.5px; font-weight:600; color:var(--text); }
.mc-pipe em { font-style:normal; font-size:14px; color:var(--muted); }
.mc-pipe .mc-dot { margin:0; animation:none; }
.mc-table { width:100%; margin-top:.6rem; border-collapse:collapse; font-size:15px; }
.mc-table th { padding:.35rem .4rem; border-bottom:1px solid var(--line); text-align:right; font-family:var(--mono);
  font-size:12px; font-weight:500; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
.mc-table td { padding:.38rem .4rem; border-bottom:1px solid #1a2029; text-align:right; color:var(--soft);
  font-variant-numeric:tabular-nums; }
.mc-table td:not(:first-child) { white-space:nowrap; }
.mc-table th:first-child, .mc-table td:first-child { text-align:left; }
.mc-card-title { margin:.55rem 0 .3rem; font-family:Rajdhani, sans-serif; font-weight:600; font-size:25px;
  line-height:1.15; color:var(--text); }
.mc-src { margin:.6rem 0 0; padding-left:1.1rem; font-size:15px; line-height:1.55; color:var(--soft); }

/* Tabs as a pill switch */
[data-testid="stTabs"] [role="tablist"] { display:inline-flex; gap:4px; width:fit-content; max-width:100%;
  overflow-x:auto; padding:4px; border:1px solid var(--line); border-radius:999px; background:#0b0e13; }
[data-testid="stTabs"] [role="tablist"]::after, [data-testid="stTabs"] .react-aria-SelectionIndicator { display:none; }
[data-testid="stTab"] { height:auto; padding:.45rem 1.1rem; border-radius:999px; }
[data-testid="stTab"] p { font-family:var(--mono); font-size:13px; letter-spacing:.08em; text-transform:uppercase;
  white-space:nowrap; color:var(--muted); }
[data-testid="stTab"]:hover p { color:var(--text); }
[data-testid="stTab"][aria-selected="true"] { background:#232a35; box-shadow:inset 0 0 0 1px rgba(255,255,255,.07); }
[data-testid="stTab"][aria-selected="true"] p { color:var(--text); }
[data-testid="stTabPanel"] { padding-top:1.3rem; }

/* Rows of choice buttons, as pills */
[data-testid="stButtonGroup"] { width:fit-content; max-width:100%; padding:3px; border:1px solid var(--line);
  border-radius:999px; background:#0b0e13; }
[data-testid="stButtonGroup"] button { min-height:2rem; border:none !important; border-radius:999px !important;
  background:transparent; }
[data-testid="stButtonGroup"] button p { font-family:var(--mono); font-size:12.5px; letter-spacing:.08em;
  text-transform:uppercase; color:var(--muted); }
[data-testid="stButtonGroup"] [data-testid="stBaseButton-segmented_controlActive"] { background:#232a35 !important; }
[data-testid="stButtonGroup"] [data-testid="stBaseButton-segmented_controlActive"] p { color:var(--text); }

/* Links to other pages, as glowing pills: ember by default, violet and green by key */
[class*="st-key-cta_"] { align-items:flex-start; }
[class*="st-key-cta_"] a[data-testid="stPageLink-NavLink"] { justify-content:center; padding:.42rem 1.15rem;
  border-radius:999px; border:1px solid rgba(255,123,57,.7); background:rgba(255,123,57,.10);
  box-shadow:0 0 22px rgba(255,123,57,.28), inset 0 0 14px rgba(255,123,57,.12); }
[class*="st-key-cta_"] a[data-testid="stPageLink-NavLink"] p { font-family:var(--mono); font-size:13px;
  letter-spacing:.1em; text-transform:uppercase; color:#ffbf9c; }
[class*="st-key-cta_"] a[data-testid="stPageLink-NavLink"]:hover { background:rgba(255,123,57,.2); }
[class*="st-key-cta_violet_"] a[data-testid="stPageLink-NavLink"] { border-color:rgba(167,139,250,.7);
  background:rgba(167,139,250,.12); box-shadow:0 0 22px rgba(167,139,250,.28), inset 0 0 14px rgba(167,139,250,.12); }
[class*="st-key-cta_violet_"] a[data-testid="stPageLink-NavLink"] p { color:#d8ccff; }
[class*="st-key-cta_green_"] a[data-testid="stPageLink-NavLink"] { border-color:rgba(62,207,116,.7);
  background:rgba(62,207,116,.10); box-shadow:0 0 22px rgba(62,207,116,.25), inset 0 0 14px rgba(62,207,116,.10); }
[class*="st-key-cta_green_"] a[data-testid="stPageLink-NavLink"] p { color:#a6f0c1; }
[data-testid="stDownloadButton"] button { border-radius:999px; border:1px solid var(--line); background:#121720;
  padding:.4rem 1.1rem; }
[data-testid="stDownloadButton"] button p { font-family:var(--mono); font-size:13px; letter-spacing:.1em;
  text-transform:uppercase; }

/* Expanders and colour keys */
[data-testid="stExpander"] details { border:1px solid var(--line); border-radius:14px; background:rgba(15,18,23,.6); }
[data-testid="stExpander"] summary p { font-family:var(--mono); font-size:13px; letter-spacing:.08em;
  text-transform:uppercase; }
.pbi-key { display:flex; flex-wrap:wrap; gap:.35rem 1rem; align-items:center; font-family:var(--mono);
  font-size:12.5px; letter-spacing:.03em; color:var(--muted); }
.pbi-key span { display:inline-flex; align-items:center; gap:.45rem; }

@media (prefers-reduced-motion: reduce) { .mc-dot { animation:none; } .mc-tile { transition:none; } }
</style>"""

# Inside the folium maps: OpenStreetMap tiles turned dark to sit on the near-black page, and dark controls.
MAP_CSS = f"""<style>
.leaflet-container {{ background: {NIGHT}; }}
.leaflet-tile-pane {{ filter: invert(1) hue-rotate(180deg) brightness(0.82) contrast(0.92) saturate(0.35); }}
.leaflet-bar a, .leaflet-bar a:hover {{ background: {DECK}; color: {STAR}; border-bottom-color: {RULE}; }}
.leaflet-control-attribution {{ background: rgba(9, 11, 15, 0.82) !important; color: {HAZE}; font-size: 11px; }}
.leaflet-control-attribution a {{ color: #8cc8ff; }}
.leaflet-tooltip, .leaflet-popup-content-wrapper, .leaflet-popup-tip {{ background: {DECK} !important;
  color: {STAR} !important; border: 1px solid {RULE} !important; box-shadow: none !important; }}
.leaflet-tooltip, .leaflet-popup-content {{ font-size: 14px; }}
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


@st.cache_data(show_spinner=False)
def _slim_grid(path, mtime, fields):
    grid = json.loads(Path(path).read_text(encoding='utf-8'))
    features = []
    for f in grid['features']:
        geometry = f['geometry']
        if geometry['type'] == 'Polygon':      # 1 km squares: coordinates rounded to about 1 m, to send less
            geometry = {'type': 'Polygon',
                        'coordinates': [[[round(x, 5), round(y, 5)] for x, y, *_ in ring]
                                        for ring in geometry['coordinates']]}
        features.append({'type': 'Feature', 'geometry': geometry,
                         'properties': {k: f['properties'].get(k) for k in fields}})
    return {'type': 'FeatureCollection', 'features': features}


def slim_grid(year, fields=('cell',)):
    """Notebook 02's 1 km grid for a season with only the fields a map needs, or None while it doesn't exist."""
    path = PROCESSED / f's2_burn_grid_1km_sangrur_{year}.geojson'
    return _slim_grid(str(path), path.stat().st_mtime, tuple(fields)) if path.exists() else None


def grid_centres(year=2025):
    """Centre of each 1 km square, as cell id -> (latitude, longitude)."""
    grid = slim_grid(year)
    if grid is None:
        return {}
    centres = {}
    for f in grid['features']:
        ring = f['geometry']['coordinates'][0][:-1]
        centres[f['properties']['cell']] = (sum(p[1] for p in ring) / len(ring), sum(p[0] for p in ring) / len(ring))
    return centres


def choice(label, options, key, default=None, format_func=str, help=None):
    """Pick one of a few options from a row of buttons (a row of radio buttons on older Streamlit)."""
    options = list(options)
    default = options[0] if default is None else default
    if hasattr(st, 'segmented_control'):
        try:
            return st.segmented_control(label, options, default=default, required=True, key=key,
                                        format_func=format_func, help=help)
        except TypeError:                      # before `required` existed: deselecting returns None
            value = st.segmented_control(label, options, default=default, key=key, format_func=format_func,
                                         help=help)
            return default if value is None else value
    return st.radio(label, options, index=options.index(default), horizontal=True, key=key,
                    format_func=format_func, help=help)


def legend(colours, ends, caption):
    """A colour ramp key, drawn by the page rather than inside a map, so it needs no extra scripts from the web."""
    html(f'<div class="pbi-key"><span>{ends[0]}<i style="display:inline-block;width:150px;height:10px;'
         f'border-radius:2px;background:linear-gradient(to right,{",".join(colours)})"></i>{ends[1]}</span>'
         f'<span>{caption}</span></div>')


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


# ---- Drawing helpers --------------------------------------------------------------------------------------------

def html(text_):
    """Markup the page draws itself, kept as written (older Streamlit: drawn as Markdown)."""
    if hasattr(st, 'html'):
        st.html(text_)
    else:
        st.markdown(text_, unsafe_allow_html=True)


def esc(value):
    """Text from a data file, made safe to put inside markup."""
    return markup.escape(str(value))


def style():
    """The page-wide styles, drawn once per run by app.py."""
    html(CSS)


def keyed(key, **kwargs):
    """A container the styles can find by its key (older Streamlit: a plain container)."""
    try:
        return st.container(key=key, **kwargs)
    except TypeError:
        try:
            return st.container(key=key)
        except TypeError:
            return st.container()


def panel(name):
    """A dark panel with rounded corners."""
    return keyed(f'panel_{name}')


def card(name):
    """A smaller card, inside a panel or on its own."""
    return keyed(f'card_{name}')


@st.cache_data(show_spinner=False)
def _icon_uri(name, size, colour):
    svg = re.sub(r'<!--.*?-->', '', (ICONS / f'{name}.svg').read_text(encoding='utf-8'), flags=re.S)
    svg = ' '.join(svg.replace('currentColor', colour).split())
    svg = svg.replace('width="24"', f'width="{size}"', 1).replace('height="24"', f'height="{size}"', 1)
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode()


def icon(name, size=18, colour=STAR):
    """A Lucide icon (static/icons/, ISC licence) as an image: Streamlit removes inline SVG but keeps images."""
    return f'<img src="{_icon_uri(name, size, colour)}" width="{size}" height="{size}" alt="">'


def svg_image(svg, size):
    uri = 'data:image/svg+xml;base64,' + base64.b64encode(' '.join(svg.split()).encode()).decode()
    return f'<img src="{uri}" width="{size}" height="{size}" alt="">'


def tile(icon_name, value, unit, label, chip='', chip_tone='', glow='', help=None):
    """One tile: an icon, a chip (a change, a count), a big number with its unit, and what it is.

    glow is '', 'ember', 'red', 'green', 'amber', 'sky' or 'violet'; chip_tone is '', 'down' (green) or 'up' (amber).
    help is shown when the pointer rests on the tile.
    """
    tip = f' title="{esc(help)}"' if help else ''
    chip = f'<span class="mc-chip {chip_tone}">{chip}</span>' if chip else ''
    unit = f'<small>{unit}</small>' if unit else ''
    return (f'<div class="mc-tile{" mc-glow-" + glow if glow else ""}"{tip}><div class="mc-tile-top">'
            f'<span class="mc-ic">{icon(icon_name)}</span>{chip}</div>'
            f'<div class="mc-num">{value}{unit}</div><div class="mc-label">{label}</div></div>')


def tiles(items, columns=4, note=None):
    """A row of tiles, two to a row on narrow screens, with an optional note under them."""
    html(f'<div class="mc-grid mc-cols-{columns}">{"".join(items)}</div>'
         + (f'<div class="mc-small">{note}</div>' if note else ''))


def ring(share, label, colour=SKY, size=78, stroke=6):
    """A ring gauge filled to share (0 to 1), with the share inside and a label under it."""
    r = (size - stroke) / 2 - 3
    length = 2 * math.pi * r
    mid = size / 2
    arc = (f'<circle cx="{mid}" cy="{mid}" r="{r}" fill="none" stroke="{colour}" stroke-width="{stroke}" '
           f'stroke-linecap="round" stroke-dasharray="{length * share:.1f} {length:.1f}" '
           f'transform="rotate(-90 {mid} {mid})"')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
           '<defs><filter id="g" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2"/>'
           '</filter></defs>'
           f'<circle cx="{mid}" cy="{mid}" r="{r}" fill="none" stroke="{RULE}" stroke-width="{stroke}"/>'
           f'{arc} opacity="0.7" filter="url(#g)"/>{arc}/></svg>')
    return (f'<div class="mc-ring">{svg_image(svg, size)}<b style="color:{colour}">{share * 100:.1f}%</b>'
            f'<span>{label}</span></div>')


def eyebrow(text_, icon_name=None, colour=HAZE):
    html(f'<div class="mc-eyebrow">{icon(icon_name, 16, colour) if icon_name else ""}{text_}</div>')


def page_header(title, subtitle=None, eyebrow=None, pill=None):
    """The header panel at the top of a page: a small line with a status dot, the title in capitals and a lede."""
    top = f'<span class="mc-eyebrow"><i class="mc-dot"></i>{eyebrow}</span>' if eyebrow else ''
    if pill:
        top += f'<span class="mc-pill">{pill}</span>'
    with keyed('hero_page'):
        html((f'<div class="mc-hero-top">{top}</div>' if top else '')
             + f'<h1 class="mc-title-xl">{title}</h1>'
             + (f'<p class="mc-lede">{subtitle}</p>' if subtitle else ''))


def cta(page, label, key, tone='ember'):
    """A glowing link to another page: tone 'ember', 'violet' or 'green' (older Streamlit: a plain link)."""
    with keyed(f'cta_{tone}_{key}'):
        st.page_link(page, label=label)


def cta_row(links, key):
    """Links to other pages side by side: [(page, label, key, tone), ...]."""
    try:
        row = st.container(horizontal=True, key=f'ctarow_{key}')
    except TypeError:                          # older Streamlit: one under another
        row = st.container()
    with row:
        for page, label, k, tone in links:
            with keyed(f'cta_{tone}_{k}', width='content'):
                st.page_link(page, label=label)


def metric(where, label, value, delta=None, **kwargs):
    """A number card, drawn like a tile by the page's styles."""
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
