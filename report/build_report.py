"""Build the report's PDF from report/report.md, and the one-pager's PDF and PNG from report/one_pager.html.

Run from the project folder:
    python report/build_report.py               the report and the one-pager
    python report/build_report.py report        the report only
    python report/build_report.py one-pager     the one-pager only

Writes report/report.pdf, report/one_pager.pdf and report/one_pager.png. It needs Playwright and Pillow, as
dashboard/take_screenshots.py does, plus markdown-it-py, a small Markdown parser in pure Python:
    pip install --no-cache-dir markdown-it-py
It prints with the Microsoft Edge already on the computer if there is one, and with Playwright's own Chromium
otherwise. No browser is downloaded: don't run "playwright install".

report.md stays plain Markdown, readable on GitHub. These markers, which GitHub doesn't show, shape the PDF:
    <!-- tiles -->          before a table: its columns become key-number tiles
    <!-- pair -->           before two images on consecutive lines: printed side by side
    map.png#qgis-panel      one of the A4 maps in maps/qgis/, cut down to the district with its north arrow, scale
                            bar and legend, so the legend stays readable at half the page width (#qgis-map: the
                            same without the legend, for a page that draws its own, as the one-pager does)
    chart.png#width=62      the image at 62% of the text width
    [Ours], [Reported...], [Recommendation...], and [R] and [O] in tables: printed as coloured labels
A paragraph in italics starting "Figure N." right after an image becomes its caption.
"""
import base64
import io
import re
import shutil
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote

from PIL import Image

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
STATIC = PROJECT / 'dashboard' / 'static'

FONTS = [('Hind', 400, 'hind-400'), ('Hind', 500, 'hind-500'), ('Hind', 600, 'hind-600'),
         ('Rajdhani', 500, 'rajdhani-500'), ('Rajdhani', 600, 'rajdhani-600'), ('Rajdhani', 700, 'rajdhani-700'),
         ('JetBrains Mono', 500, 'jetbrains-mono-500'), ('JetBrains Mono', 600, 'jetbrains-mono-600')]

MARGIN = {'top': '15mm', 'right': '16mm', 'bottom': '15mm', 'left': '16mm'}
FOOTER = ('<div style="width:100%;margin:0 16mm;display:flex;justify-content:space-between;'
          'font-family:Arial,Helvetica,sans-serif;font-size:7.5px;color:#5a6577;">'
          '<span>{left}</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>')

# The A4 layout of maps/build_qgis_project.py at 300 dpi, measured on 19 Nov 2026: boxes are (left, top, right, bottom)
# in pixels. If a map comes out at another size, the whole page is used instead.
QGIS_SIZE = (2480, 3507)
QGIS_MAP = (560, 400, 1910, 2550)          # the district, inside the map frame
QGIS_BLANK = [(1695, 400, 1910, 990),      # the part of the Punjab inset that falls inside QGIS_MAP
              (560, 2460, 690, 2550)]      # the end of the scale bar
QGIS_NORTH = (195, 438, 310, 582)
QGIS_SCALE = (185, 2462, 680, 2566)
QGIS_LEGEND = (140, 2790, 1520, 3095)
PANEL_WIDTH = 1100                         # px: about 330 dpi at half the text width


def font_faces():
    rules = []
    for family, weight, stem in FONTS:
        data = base64.b64encode((STATIC / f'{stem}.woff2').read_bytes()).decode()
        rules.append(f"@font-face {{ font-family: '{family}'; font-weight: {weight}; font-style: normal; "
                     f"src: url(data:font/woff2;base64,{data}) format('woff2'); }}")
    return '\n'.join(rules)


def mark_svg():
    # The project's mark, with its satellite drawn dark instead of light, for a white page.
    return (STATIC / 'mark.svg').read_text(encoding='utf-8').replace('#e8eef7', '#172030')


def data_uri(im, fmt):
    buf = io.BytesIO()
    if fmt == 'JPEG':
        im.convert('RGB').save(buf, 'JPEG', quality=90, optimize=True)
    else:
        im.save(buf, 'PNG', optimize=True)
    return f'data:image/{fmt.lower()};base64,' + base64.b64encode(buf.getvalue()).decode()


def qgis_panel(path, legend=True):
    # legend=False leaves the legend out, for a page that draws its own (the one-pager).
    im = Image.open(path).convert('RGB')
    if im.size != QGIS_SIZE:
        return im
    left, top = QGIS_MAP[:2]
    district = im.crop(QGIS_MAP)
    for l, t, r, b in QGIS_BLANK:
        district.paste((255, 255, 255), (l - left, t - top, r - left, b - top))
    district.paste(im.crop(QGIS_NORTH), (24, 24))
    scale = im.crop(QGIS_SCALE)
    key = im.crop(QGIS_LEGEND) if legend else Image.new('RGB', (1, 1), 'white')
    width = max(district.width, key.width)
    panel = Image.new('RGB', (width, district.height + scale.height + (key.height + 50 if legend else 10)), 'white')
    panel.paste(district, ((width - district.width) // 2, 0))
    panel.paste(scale, (40, district.height + 10))
    if legend:
        panel.paste(key, (0, district.height + scale.height + 50))
    return panel.resize((PANEL_WIDTH, round(panel.height * PANEL_WIDTH / width)), Image.LANCZOS)


def image_tag(match):
    src, alt = match.group(1), match.group(2)
    path, _, fragment = src.partition('#')
    file = (HERE / unquote(path)).resolve()
    style = ''
    if fragment == 'qgis-panel':
        uri = data_uri(qgis_panel(file), 'PNG')
    else:
        im = Image.open(file)
        if file.suffix.lower() in ('.webp', '.jpg', '.jpeg'):
            if im.width > 2100:
                im = im.resize((2100, round(im.height * 2100 / im.width)), Image.LANCZOS)
            uri = data_uri(im, 'JPEG')
        else:
            uri = data_uri(im, 'PNG')
        if fragment.startswith('width='):
            style = f' style="width:{int(fragment[6:])}%"'
    return f'<img src="{uri}" alt="{alt}"{style}>'


LABEL = re.compile(r'\[(Reported|Ours|Recommendation)([^\[\]]*)\]')
SHORT_LABEL = re.compile(r'\[(R|O)\]')
CAPTION = r'\s*<p><em>(Figure \d+\..*?)</em></p>'


def caption(text):
    return re.sub(r'^(Figure \d+\.)', r'<b>\1</b>', text)


def report_html():
    from markdown_it import MarkdownIt
    text = (HERE / 'report.md').read_text(encoding='utf-8')
    html = MarkdownIt('commonmark', {'html': True}).enable('table').render(text)

    html = LABEL.sub(lambda m: f'<span class="tag {m[1].lower()}"><b>{m[1]}</b>{m[2]}</span>', html)
    html = SHORT_LABEL.sub(lambda m: f'<span class="tag {"reported" if m[1] == "R" else "ours"}"><b>{m[1]}</b></span>',
                           html)
    html = re.sub(r'<!-- tiles -->\s*<table>', '<table class="tiles">', html)
    html = re.sub(r'<table>(\s*<thead>\s*<tr>\s*<th>[^<]*</th>\s*<th></th>\s*</tr>)', r'<table class="two-col">\1',
                  html)
    html = re.sub(r'<p><em>(<span class="tag reported"><b>R</b></span>.*?)</em></p>', r'<p class="table-note">\1</p>',
                  html, flags=re.S)
    html = re.sub(r'<!-- pair(?: (\d+))? -->\s*<p>(<img [^>]+>)\s*(<img [^>]+>)</p>' + CAPTION,
                  lambda m: f'<figure class="pair"><div class="imgs" style="width:{m[1] or 100}%">{m[2]}{m[3]}'
                            f'</div><figcaption>{caption(m[4])}</figcaption></figure>', html, flags=re.S)
    # A paragraph that introduces what follows ("Why this order:") stays on the same page as it.
    html = re.sub(r'<p>((?:(?!</p>).)*?:)</p>', r'<p class="lead">\1</p>', html, flags=re.S)
    def figure(m):
        kind = ' class="shot"' if 'screenshots/' in m[1] else ''
        return f'<figure{kind}>{m[1]}<figcaption>{caption(m[2])}</figcaption></figure>'
    html = re.sub(r'<p>(<img [^>]+>)</p>' + CAPTION, figure, html, flags=re.S)
    html = re.sub(r'<img src="([^"]+)" alt="([^"]*)" />', image_tag, html)

    # Everything before the first section is the front matter; the references get smaller type.
    front, _, rest = html.partition('<h2>')
    brand = (f'<div class="brand">{mark_svg()}<span>Paddy Burnt-Area Intelligence</span>'
             '<span class="right">Satellite Mission Intelligence for India</span></div>')
    body = f'<header class="front">{brand}{front}</header><h2>{rest}'
    body = body.replace('<h2>References</h2>', '<section class="references"><h2>References</h2>') + '</section>'
    css = (HERE / 'report.css').read_text(encoding='utf-8')
    return ('<!doctype html><html lang="en-GB"><head><meta charset="utf-8">'
            '<title>Paddy burnt-area intelligence for Punjab</title>'
            f'<style>{font_faces()}</style><style>{css}</style></head><body>{body}</body></html>')


def browser(p):
    from playwright.sync_api import Error as PlaywrightError
    try:
        return p.chromium.launch(channel='msedge')
    except PlaywrightError:
        return p.chromium.launch()


def page_count(pdf):
    return len(re.findall(rb'/Type\s*/Page[^s]', pdf.read_bytes()))


def build_report(build):
    from playwright.sync_api import sync_playwright
    page_file = build / 'report.html'
    page_file.write_text(report_html(), encoding='utf-8')
    out = HERE / 'report.pdf'
    with sync_playwright() as p:
        b = browser(p)
        page = b.new_page()
        page.goto(page_file.as_uri(), wait_until='load')
        page.evaluate('document.fonts.ready')
        page.pdf(path=str(out), format='A4', print_background=True, margin=MARGIN, display_header_footer=True,
                 header_template='<span></span>',
                 footer_template=FOOTER.format(left='Paddy burnt-area intelligence for Punjab · Technical and '
                                                    'product report · Mohit Sharma, November 2026'))
        b.close()
    print(f'{out.relative_to(PROJECT)}: {page_count(out)} pages, {out.stat().st_size / 1e6:.1f} MB')


def build_one_pager(build):
    from playwright.sync_api import sync_playwright
    source = HERE / 'one_pager.html'
    if not source.exists():
        print(f'{source.relative_to(PROJECT)} not found; skipped')
        return
    html = source.read_text(encoding='utf-8').replace('/* FONTS */', font_faces())
    html = html.replace('<!-- MARK -->', mark_svg())
    def embed(m):
        file, fragment = (HERE / unquote(m[1])).resolve(), m[2] or ''
        if fragment in ('#qgis-panel', '#qgis-map'):
            return f'src="{data_uri(qgis_panel(file, legend=fragment == "#qgis-panel"), "PNG")}"'
        im = Image.open(file)
        if fragment.startswith('#crop='):         # left, top, right, bottom as fractions of the image
            l, t, r, b = (float(v) for v in fragment[6:].split(','))
            im = im.crop((round(l * im.width), round(t * im.height), round(r * im.width), round(b * im.height)))
        if file.suffix.lower() in ('.webp', '.jpg', '.jpeg'):
            if im.width > 1400:
                im = im.resize((1400, round(im.height * 1400 / im.width)), Image.LANCZOS)
            return f'src="{data_uri(im, "JPEG")}"'
        return f'src="{data_uri(im, "PNG")}"'
    html = re.sub(r'src="([^"]+\.(?:png|webp|jpg))(#[^"]*)?"', embed, html)
    page_file = build / 'one_pager.html'
    page_file.write_text(html, encoding='utf-8')
    with sync_playwright() as p:
        b = browser(p)
        page = b.new_page(viewport={'width': 794, 'height': 1123}, device_scale_factor=2)
        page.goto(page_file.as_uri(), wait_until='load')
        page.evaluate('document.fonts.ready')
        page.pdf(path=str(HERE / 'one_pager.pdf'), format='A4', print_background=True,
                 margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'})
        page.screenshot(path=str(HERE / 'one_pager.png'), full_page=False)
        b.close()
    pdf = HERE / 'one_pager.pdf'
    print(f'{pdf.relative_to(PROJECT)}: {page_count(pdf)} page(s); report/one_pager.png written')


if __name__ == '__main__':
    what = sys.argv[1:] or ['report', 'one-pager']
    build = Path(tempfile.mkdtemp(prefix='report_build_'))
    try:
        if 'report' in what:
            build_report(build)
        if 'one-pager' in what:
            build_one_pager(build)
    finally:
        shutil.rmtree(build, ignore_errors=True)
