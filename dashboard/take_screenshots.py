"""Retake the dashboard screenshots in dashboard/screenshots/.

Run from the project folder:  D:/conda-envs/eo/python.exe dashboard/take_screenshots.py
Retake only some of them:     D:/conda-envs/eo/python.exe dashboard/take_screenshots.py 08 09

It starts the dashboard on a free port, opens each view in the Microsoft Edge already on the computer, and stops the
dashboard at the end. It needs Playwright and Pillow, which the dashboard itself doesn't, so neither is in
requirements.txt. No browser is downloaded: don't run "playwright install".
"""
import io
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from collections import namedtuple
from pathlib import Path

from PIL import Image
from playwright.sync_api import Error as PlaywrightError, sync_playwright

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
OUT = HERE / 'screenshots'

WINDOW = {'width': 1440, 'height': 900}
SCALE = 2
QUALITY = 90
QUIET_S = 2.0                  # the page must stay finished for this long
TIMEOUT_S = 180                # give up waiting for a view after this long
MAP_EXTRA_MS = 4000            # the maps sit in iframes, so allow a few more seconds once their tiles are in
TOP_GAP = 10                   # px between the top navigation bar and whatever is scrolled up to it
BOTTOM_GAP = 5                 # px between the bottom of the window and a view placed by its bottom edge

# view is 'top' (the top of the page), 'tab' (the tab bar just below the top navigation bar) or a CSS selector for the
# element to bring up to the same place. 'bottom:' before a selector puts that element's bottom edge at the bottom of
# the window instead.
Shot = namedtuple('Shot', 'name page tab option view', defaults=(None, None, 'top'))
SHOTS = [
    Shot('01_overview', 'Overview'),
    Shot('02_missions', 'Missions', 'All missions', view='tab'),
    Shot('03_startups_map', 'Startups', 'Map', view='tab'),
    Shot('04_eo_burnt_area_map', 'EO Analysis', 'Burnt-area map', '2025', '[data-testid="stSelectbox"]'),
    Shot('05_eo_missed', 'EO Analysis', 'What fire counts missed', view='tab'),
    Shot('06_eo_2021_vs_2025', 'EO Analysis', '2021 against 2025', view='tab'),
    Shot('07_eo_ml_classifier', 'EO Analysis', 'ML classifier', view='tab'),
    Shot('08_eo_forecast_punjab', 'EO Analysis', '2026 forecast', 'Punjab', 'tab'),
    Shot('09_eo_forecast_sangrur', 'EO Analysis', '2026 forecast', 'Sangrur', 'tab'),
    Shot('10_tradeoffs', 'Trade-offs', 'What 2025 showed', view='bottom:.st-key-card_option_6'),
    Shot('11_opportunity', 'Opportunity', view='[data-testid="stSlider"]'),
]

# Only in the screenshot browser: controls a visitor to the live app never sees.
DEVELOPER_ONLY = '[data-testid="stAppDeployButton"] { display: none !important; }'

# What is still unfinished in the part of the page on screen.
BUSY = """() => {
  const onScreen = e => { const r = e.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && r.bottom > 0 && r.top < innerHeight; };
  const all = s => Array.from(document.querySelectorAll(s)).filter(onScreen);
  const busy = [];
  if (!document.querySelector('[data-testid="stApp"][data-test-script-state="notRunning"]')) busy.push('script running');
  if (all('[data-testid="stSkeleton"], [data-testid="stSpinner"], [data-testid="stStatusWidget"]').length) busy.push('spinner');
  if (all('[data-testid="stVegaLiteChart"]').some(e => { const g = e.querySelector('svg, canvas');
    return !g || g.getBoundingClientRect().height < 20; })) busy.push('chart not drawn');
  if (all('[data-testid="stDataFrame"]').some(e => !e.querySelector('canvas'))) busy.push('table not drawn');
  if (all('img').some(e => !e.complete)) busy.push('image loading');
  if (document.fonts.status !== 'loaded') busy.push('fonts loading');
  return busy;
}"""

# True when a folium map in an iframe has drawn and has no tile still loading.
MAP_READY = """() => {
  const map = document.querySelector('.leaflet-container');
  if (!map || map.getBoundingClientRect().height < 20) return false;
  if (map.querySelector('.leaflet-tile-loading')) return false;
  return !map.querySelector('.leaflet-tile-pane .leaflet-layer') || map.querySelectorAll('.leaflet-tile-loaded').length > 0;
}"""

# Error messages on screen, and the note the dashboard shows when a data file is missing.
PROBLEMS = """() => {
  const seen = e => e.getBoundingClientRect().width > 0;
  const found = Array.from(document.querySelectorAll('[data-testid="stException"], [data-testid="stAlertContentError"]'))
    .filter(seen).map(e => e.innerText.slice(0, 120));
  const notes = Array.from(document.querySelectorAll('[data-testid="stAlert"]'))
    .filter(e => seen(e) && e.innerText.includes('is not there yet')).map(e => e.innerText.slice(0, 120));
  return found.concat(notes);
}"""

# Scroll the page so an element sits just below the top navigation bar, or just above the bottom of the window if its
# selector starts with 'bottom:'; no selector means the top of the page.
PLACE = """([selector, topGap, bottomGap]) => {
  const main = document.querySelector('[data-testid="stMain"]');
  if (!selector) { main.scrollTop = 0; return true; }
  const css = selector.replace(/^bottom:/, '');
  const target = Array.from(document.querySelectorAll(css)).find(e => e.getBoundingClientRect().width > 0);
  if (!target) return false;
  const box = target.getBoundingClientRect();
  if (css !== selector) { main.scrollTop += box.bottom - (innerHeight - bottomGap); return true; }
  const bar = document.querySelector('[data-testid="stHeader"]').getBoundingClientRect().bottom;
  main.scrollTop += box.top - bar - topGap;
  return true;
}"""


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def start_dashboard(port):
    process = subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', 'dashboard/app.py', '--server.headless', 'true',
                                '--server.port', str(port), '--server.address', '127.0.0.1',
                                '--browser.gatherUsageStats', 'false'],
                               cwd=PROJECT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.time() + TIMEOUT_S
    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError('The dashboard stopped while starting. Run it by hand to see why.')
        try:
            urllib.request.urlopen(f'http://127.0.0.1:{port}/_stcore/health', timeout=2)
            return process
        except OSError:
            time.sleep(0.5)
    process.terminate()
    raise RuntimeError('The dashboard did not respond in time.')


def visible_maps(page):
    # The content of each folium iframe on screen.
    frames = []
    for iframe in page.query_selector_all('iframe[title="streamlit_folium.st_folium"]'):
        box = iframe.bounding_box()
        if box and box['width'] > 0 and box['height'] > 0 and box['y'] < WINDOW['height'] and box['y'] + box['height'] > 0:
            frames.append(iframe.content_frame())
    return [f for f in frames if f]


def unfinished(page):
    # What the page is still doing, as a list of short reasons; an empty list means it has finished.
    try:
        busy = page.evaluate(BUSY)
        for frame in visible_maps(page):
            if not frame.evaluate(MAP_READY):
                busy.append('map tiles loading')
        return busy
    except PlaywrightError:    # a frame was replaced while Streamlit redrew the page
        return ['page redrawing']


def settle(page):
    # Wait until the view has finished and stayed finished. Returns what was still unfinished if it never did.
    page.wait_for_timeout(800)
    deadline, quiet_since = time.time() + TIMEOUT_S, None
    busy = []
    while time.time() < deadline:
        busy = unfinished(page)
        if busy:
            quiet_since = None
        elif quiet_since is None:
            quiet_since = time.time()
        elif time.time() - quiet_since >= QUIET_S:
            if visible_maps(page):
                page.wait_for_timeout(MAP_EXTRA_MS)
            return []
        page.wait_for_timeout(250)
    return busy


def park_mouse(page):
    # No tooltip, hover or focus state in the picture.
    page.mouse.move(0, WINDOW['height'] - 1)
    page.evaluate('() => document.activeElement && document.activeElement.blur()')


def pick_option(page, label):
    button = page.locator('[data-testid="stButtonGroup"] button:visible', has_text=re.compile(f'^{re.escape(label)}$')).first
    if 'true' not in (button.get_attribute('aria-checked'), button.get_attribute('aria-pressed')):
        button.click()


def take(page, shot, on_page):
    # Open one view, wait for it, save it. Returns a list of what is wrong with the picture.
    if shot.page != on_page:
        page.locator('[data-testid="stTopNavLink"]', has_text=shot.page).click()
        settle(page)
    if shot.tab:
        page.get_by_role('tab', name=shot.tab, exact=True).click()
    if shot.option:
        pick_option(page, shot.option)
    park_mouse(page)
    selector = {'top': None, 'tab': '[role="tablist"]'}.get(shot.view, shot.view)
    problems = []
    for _ in range(2):         # again after the wait, in case drawing the view moved the page
        if not page.evaluate(PLACE, [selector, TOP_GAP, BOTTOM_GAP]):
            problems.append(f'nothing on the page matches {selector}')
        busy = settle(page)
    problems += [f'still unfinished: {reason}' for reason in busy] + page.evaluate(PROBLEMS)
    picture = Image.open(io.BytesIO(page.screenshot())).convert('RGB')
    picture.save(OUT / f'{shot.name}.webp', 'WEBP', quality=QUALITY, method=6)
    return problems


def main():
    wanted = sys.argv[1:]
    shots = [s for s in SHOTS if not wanted or any(s.name.startswith(w) for w in wanted)]
    if not shots:
        raise SystemExit(f'No screenshot starts with {", ".join(wanted)}.')
    OUT.mkdir(exist_ok=True)
    failed = 0
    port = free_port()
    dashboard = start_dashboard(port)
    try:
        # Edge's temporary profile goes on the project's drive, not the system drive.
        with tempfile.TemporaryDirectory(prefix='dashboard-screenshots-', dir=PROJECT.parent,
                                         ignore_cleanup_errors=True) as scratch:
            os.environ['TMP'] = os.environ['TEMP'] = scratch
            with sync_playwright() as p:
                browser = p.chromium.launch(channel='msedge')
                page = browser.new_context(viewport=WINDOW, device_scale_factor=SCALE).new_page()
                page.set_default_timeout(TIMEOUT_S * 1000)
                page.goto(f'http://127.0.0.1:{port}')
                page.wait_for_selector('[data-testid="stTopNavLink"]')
                page.add_style_tag(content=DEVELOPER_ONLY)
                settle(page)
                on_page = None
                for shot in shots:
                    problems = take(page, shot, on_page)
                    on_page = shot.page
                    size = (OUT / f'{shot.name}.webp').stat().st_size
                    print(f'{shot.name}.webp  {size / 1024:,.0f} KB' + ('' if not problems else '  PROBLEM: ' + '; '.join(problems)))
                    failed += bool(problems)
                browser.close()
    finally:
        dashboard.terminate()
        try:
            dashboard.wait(timeout=20)
        except subprocess.TimeoutExpired:
            dashboard.kill()
    if failed:
        raise SystemExit(f'{failed} screenshot(s) need another look.')


if __name__ == '__main__':
    main()
