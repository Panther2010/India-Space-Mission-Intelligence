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

AREA_LABEL = 'Sangrur (pre-2021 boundary)'
SEASONS = (2025, 2021)
CREDIT = ('Contains modified Copernicus Sentinel data 2021 and 2025. Fire detections: NASA FIRMS (VIIRS and MODIS). '
          'District outline: geoBoundaries (ODbL 1.0). Basemap: © OpenStreetMap contributors.')


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
