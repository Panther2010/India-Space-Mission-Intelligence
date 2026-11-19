"""Rewrite the 2026 forecast passages from Notebook 04's committed outputs, interim or final.

The report, the findings draft, the method notes, the demo script and the two READMEs all describe the check of the
2026 forecast. This script writes those passages from data/processed/, so every document gives the numbers of the
latest committed run of Notebook 04. Once every forecast week, to 30 Nov, has been checked, it switches them to the
final wording: the forecast's score, and the documents stop calling themselves interim.

Run from the project folder, after a Notebook 04 run has been committed:
    python report/update_forecast_text.py            rewrite the passages
    python report/update_forecast_text.py --check    show what would change, and write nothing
then rebuild the PDFs with python report/build_report.py.

Each passage sits between markers that GitHub doesn't show, <!-- forecast:NAME --> and <!-- /forecast:NAME -->, and
nothing outside them is touched. Table rows have no room for markers: those passages are found by how the row begins
or by the clause that changes. For testing, --data DIR reads another copy of data/processed/, and --today YYYY-MM-DD
sets the date the documents give (by default, today).
"""
import argparse
import datetime as dt
import difflib
import math
import re
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent

AREAS = ['Punjab', 'Sangrur']
METHODS = ['past seasons rescaled', 'last season', 'SARIMA']            # the headline method first
CALLED = {'past seasons rescaled': 'the headline method', 'last season': 'the last-season baseline',
          'SARIMA': 'SARIMA'}
FRAGILE = {'Sangrur'}           # flagged as fragile the day the forecast was issued (decision log, 1 Nov 2026)
TIMES = {2: 'twice', 3: 'three times', 4: 'four times', 5: 'five times', 6: 'six times', 7: 'seven times',
         8: 'eight times', 9: 'nine times', 10: 'ten times', 11: 'eleven times', 12: 'twelve times'}
FRACTIONS = [(0.1, 'a tenth'), (0.2, 'a fifth'), (0.25, 'a quarter'), (1 / 3, 'a third'), (0.4, 'two-fifths'),
             (0.5, 'half'), (2 / 3, 'two-thirds'), (0.75, 'three-quarters')]
WORDS = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five'}


# ---- Numbers and dates, written the way the documents write them ---------------------------------------------------
def num(x):
    return f'{float(x):,.0f}'


def small(x):
    # A forecast of half a detection is not a forecast of none.
    return 'under 1' if 0 < float(x) < 1 and num(x) == '0' else num(x)


def about(x):
    # 'about 2,700' for thousands, the nearest ten for hundreds, exact below 100
    x = float(x)
    step = 100 if x >= 1000 else 10 if x >= 100 else 1
    return f'{round(x / step) * step:,.0f}'


def day(d):
    t = pd.Timestamp(d)
    return f'{t.day} {t:%b}'


def days(a, b):
    a, b = pd.Timestamp(a), pd.Timestamp(b)
    return f'{a.day}–{b.day} {b:%b}' if a.month == b.month else f'{a.day} {a:%b}–{b.day} {b:%b}'


def fraction(share):
    return min(FRACTIONS, key=lambda f: abs(f[0] - share))[1]


def off_by(forecast, actual, kind='count'):
    """How far a forecast was from what happened: 'about a fifth too few', '6% too few', 'about nine times too few',
    'more than twice as many'. None when within 5%, close enough to need no qualifier."""
    low, high, alike = ('too few', 'too many', 'as many') if kind == 'count' else ('too low', 'too high', 'as high')
    r = float(forecast) / float(actual)
    if abs(r - 1) < 0.05:
        return None
    if r < 1:
        if r < 0.4:
            return f'about {TIMES.get(round(1 / r), f"{round(1 / r)} times")} {low}'
        if r <= 0.6:
            return f'about half {alike}'
        return f'{1 - r:.0%} {low}' if 1 - r < 0.15 else f'about {fraction(1 - r)} {low}'
    if r >= 2:
        return f'more than twice {alike}' if r < 2.5 else f'about {TIMES.get(round(r), f"{round(r)} times")} {alike}'
    return f'{r - 1:.0%} {high}' if r - 1 < 0.15 else f'about {fraction(r - 1)} {high}'


def percent_off(forecast, actual):
    r = float(forecast) / float(actual)
    return f'{abs(r - 1):.0%} too {"high" if r > 1 else "low"}'


def listed(items):
    items = list(items)
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + ' and ' + items[-1]


def ours(sentence):
    # The label goes before the closing full stop, as everywhere else in the documents.
    sentence = sentence.rstrip()
    return (sentence[:-1] if sentence.endswith('.') else sentence) + ' [Ours].'


def error_factor(forecast, actual):
    # As Notebook 04 scores its backtests: the ratio of forecast and outcome, taken as at least 1.
    return math.exp(abs(math.log((float(forecast) + 1) / (float(actual) + 1))))


# ---- The state of the check ---------------------------------------------------------------------------------------
class Area:
    def __init__(self, name, summary, weekly, check, updates):
        self.name = name
        rows = summary[summary['area'] == name].set_index('method')
        self.head = rows.loc[METHODS[0]]
        self.rows = rows
        self.weekly = weekly[(weekly['area'] == name) & (weekly['method'] == METHODS[0])].set_index('week')
        self.check = check[check['area'] == name].set_index('week')
        self.done = self.check[self.check['actual'].notna()]
        self.final = len(self.done) == len(self.check)
        self.actual = self.done['actual'].sum()
        self.totals = {m: self.done[m].sum() for m in METHODS}
        self.seen0 = float(self.head['seen_so_far'])
        self.seen = self.seen0 + self.actual
        self.season_low = self.seen0 + self.head['rest_low']
        self.season_high = self.seen0 + self.head['rest_high']
        self.update = None
        if updates is not None and len(updates):
            mine = updates[updates['area'] == name]
            if len(mine):
                self.update = mine[mine['issue_week'] == mine['issue_week'].max()].iloc[0]

    def week_dates(self, week):
        row = self.weekly.loc[int(week)]
        return row['week_start'], row['week_end']

    def peak_forecast(self):
        return int(self.head['peak_week'])

    def peak_actual(self):
        # Over the whole season, as Notebook 04 finds it: the weeks seen before the forecast and the weeks checked.
        seen = self.weekly['seen'].dropna()
        series = pd.concat([seen, self.done['actual']])
        return int(series.idxmax())

    def rest(self, method):
        return self.rows.loc[method]


def load(data):
    summary = pd.read_csv(data / 'fire_forecast_2026_summary.csv')
    weekly = pd.read_csv(data / 'fire_forecast_2026.csv')
    check = pd.read_csv(data / 'fire_forecast_check_2026.csv')
    path = data / 'fire_forecast_2026_updates_summary.csv'
    updates = pd.read_csv(path) if path.exists() else None
    areas = {a: Area(a, summary, weekly, check, updates) for a in AREAS}
    done = areas['Punjab'].done
    if done.empty:
        sys.exit('No forecast week has been checked yet: nothing to write.')
    sources = check.loc[check['actual'].notna(), 'actual_source']
    ratio = next((s.split('x')[-1].strip() for s in sources if 'NOAA-20' in s), None)
    return areas, ratio


# ---- Sentences shared by the documents ----------------------------------------------------------------------------
def closest(totals, actual, kind):
    ratios = {m: totals[m] / actual for m in METHODS}
    best = min(METHODS, key=lambda m: abs(math.log(ratios[m])))

    def told(m):
        o = off_by(totals[m], actual, kind)
        return f'{CALLED[m]} forecast {o} ({num(totals[m])})' if o else f'{CALLED[m]} forecast {num(totals[m])}'

    if best == METHODS[0]:
        return f'The headline method came closest; {told(METHODS[1])}, and {told(METHODS[2])}.'
    other = next(m for m in METHODS[1:] if m != best)
    o = off_by(totals[best], actual, kind)
    lead = CALLED[best][0].upper() + CALLED[best][1:]
    return f'{lead} came closest ({num(totals[best])}{", " + o if o else ""}), and {told(other)}.'


def failed(area):
    gone = area.seen > area.season_high if not area.final else not inside_rest(area)
    if not gone:
        return ''
    return (' The fragile forecast failed, as flagged when it was issued.' if area.name in FRAGILE
            else ' It has gone past its 80% range.')


def inside_rest(area):
    return area.head['rest_low'] <= area.actual <= area.head['rest_high']


def peak_sentence(areas, final, style='report'):
    right = {a.name: a.peak_actual() == a.peak_forecast() for a in areas.values()}
    p, s = areas['Punjab'], areas['Sangrur']
    so_far = '' if final else ' so far'
    if all(right.values()) and p.peak_forecast() == s.peak_forecast():
        if style == 'report':
            return f'*The busiest week{so_far} was right for both:* week {p.peak_forecast()}.'
        return f'**Busiest week{so_far}:** week {p.peak_forecast()} for both, as forecast [Ours].'
    parts = []
    for a in areas.values():
        verb = 'as forecast' if right[a.name] else f'against week {a.peak_forecast()} forecast'
        parts.append(f'{a.name} week {a.peak_actual()}, {verb}')
    if style == 'report':
        return f'*The busiest week{so_far}:* ' + '; '.join(parts) + '.'
    return f'**Busiest week{so_far}:** ' + '; '.join(parts) + ' [Ours].'


def issued_bullets(areas, style):
    p, s = areas['Punjab'], areas['Sangrur']
    ph, sh = p.head, s.head
    pk = p.peak_forecast()
    start, end = p.week_dates(pk)
    both = ', for both' if s.peak_forecast() == pk else f'; for Sangrur, week {s.peak_forecast()}'
    if style == 'report':
        return (f"- **The forecast, issued {day(ph['issued_on'])} from data to {day(ph['data_through'])}** [Ours]:\n"
                f"  - *Punjab:* about {about(ph['forecast_rest'])} more Suomi NPP detections by 30 Nov (80% range "
                f"{about(ph['rest_low'])}–{about(ph['rest_high'])}), or about {about(ph['forecast_season'])} for the "
                f"season, against {num(ph['last_season'])} in 2025.\n"
                f"  - *Sangrur:* about {about(sh['forecast_rest'])} more (range {about(sh['rest_low'])}–"
                f"{about(sh['rest_high'])}). It rested on only {num(s.seen0)} detections, a weakness recorded the day "
                f"it was issued.\n"
                f"  - *Busiest week:* most likely week {pk} ({days(start, end)}){both}.\n")
    return (f"- **The forecast, issued {day(ph['issued_on'])} from data to {day(ph['data_through'])}.** The method is "
            f"past seasons rescaled, which was best in backtests over 2021–2025 [Ours].\n"
            f"  - **Punjab:** about {about(ph['forecast_rest'])} more Suomi NPP detections by 30 Nov (80% range "
            f"{about(ph['rest_low'])}–{about(ph['rest_high'])}), or about {about(ph['forecast_season'])} for the "
            f"season, against {num(ph['last_season'])} in 2025 [Ours].\n"
            f"  - **Sangrur:** about {about(sh['forecast_rest'])} more (range {about(sh['rest_low'])}–"
            f"{about(sh['rest_high'])}), resting on only {num(s.seen0)} detections to {day(sh['data_through'])} [Ours].\n"
            f"  - **Busiest week:** most likely week {pk} ({days(start, end)}){' for both' if both == ', for both' else both}"
            f" [Ours].\n")


def season_so_far(area):
    h = area.head
    lead = f"{area.name}'s {num(area.seen)} detections to {day(area.done['week_end'].iloc[-1])}"
    if area.seen > h['forecast_season']:
        if area.seen <= area.season_high:
            return (f"{lead} already exceed the 1 Nov forecast for the whole season (about {about(h['forecast_season'])}),"
                    f" but lie inside its 80% range of {num(area.season_low)}–{num(area.season_high)}.")
        return (f"{lead} already exceed the 1 Nov forecast for the whole season (about {about(h['forecast_season'])}) "
                f"and its 80% range of {num(area.season_low)}–{num(area.season_high)}.")
    return f"{lead} are {area.seen / h['forecast_season']:.0%} of the 1 Nov forecast for the whole season (about {about(h['forecast_season'])})."


def compared_with_2025(value, last):
    r = float(value) / float(last)
    return 'close to' if abs(r - 1) < 0.05 else 'above' if r > 1 else 'below'


def noaa_note(ratio):
    return f" by the two sensors' 2026 ratio ({ratio})" if ratio else ''


# ---- The passages --------------------------------------------------------------------------------------------------
def report_section(areas, ratio):
    p, s = areas['Punjab'], areas['Sangrur']
    first, last = int(p.done.index.min()), int(p.done.index.max())
    start, end = p.done['week_start'].iloc[0], p.done['week_end'].iloc[-1]
    text = []
    if not p.final:
        text.append(f'### 6.5 The 2026 forecast so far (interim, to {day(end)})\n\n')
        text.append(issued_bullets(areas, 'report'))
        text.append(f'- **Checked over weeks {first}–{last}, {day(start)} to {day(end)}** [Ours]:\n')
        for a, word in ((p, ' detections'), (s, '')):
            o = off_by(a.totals[METHODS[0]], a.actual)
            text.append(f'  - *{a.name}:* {num(a.actual)}{word} against {num(a.totals[METHODS[0]])} forecast'
                        f'{", " + o if o else ""}. {closest(a.totals, a.actual, "count")}{failed(a)}\n')
        text.append(f'  - {peak_sentence(areas, False)}\n')
        u = p.update
        updated = (f" The updated forecast of {day(u['issued_on'])} puts the season at {num(u['forecast_season'])}, "
                   f"{compared_with_2025(u['forecast_season'], p.head['last_season'])} 2025's "
                   f"{num(p.head['last_season'])}." if u is not None else '')
        text.append(f'- **The season so far** [Ours]. {season_so_far(p)}{updated}\n')
        text.append('- **Caveat.** From week 8, the actual counts are NOAA-20\'s converted to Suomi NPP terms, which '
                    'adds uncertainty [Ours]. The score is final after 30 Nov.\n\n')
        still = [w for w in p.check.index if w not in p.done.index]
        to_come = (f'. Week {still[0]} is still to come' if len(still) == 1 else
                   f'. Weeks {", ".join(map(str, still[:-1]))} and {still[-1]} are still to come')
    else:
        text.append('### 6.5 The 2026 forecast, scored\n\n')
        text.append(issued_bullets(areas, 'report'))
        text.append(f'- **The score, weeks {first}–{last}, {day(start)} to {day(end)}** [Ours]:\n')
        for a, word in ((p, ' detections'), (s, '')):
            rest = {m: a.rest(m)['forecast_rest'] for m in METHODS}
            o = off_by(rest[METHODS[0]], a.actual)
            where = 'inside' if inside_rest(a) else 'outside'
            ef, typical = error_factor(rest[METHODS[0]], a.actual), float(a.head['typical_error_all'])
            text.append(f'  - *{a.name}:* {num(a.actual)}{word} against {num(rest[METHODS[0]])} forecast'
                        f'{", " + o if o else ""}: {where} its 80% range of {num(a.head["rest_low"])}–'
                        f'{num(a.head["rest_high"])}. Its error factor of {ef:.2f} is '
                        f'{"within" if ef <= typical else "beyond"} the method\'s typical {typical:.2f} in backtests. '
                        f'{closest(rest, a.actual, "count")}{failed(a)}\n')
        text.append(f'  - {peak_sentence(areas, True)}\n')
        seasons = '; '.join(
            f"{a.name} {num(a.seen)}, against about {about(a.head['forecast_season'])} forecast and "
            f"{num(a.head['last_season'])} in 2025" for a in (p, s))
        text.append(f'- **The season** [Ours], in Suomi NPP terms: {seasons}.\n')
        text.append(f"- **Caveat.** From week 8, the actual counts are NOAA-20's converted to Suomi NPP terms"
                    f"{noaa_note(ratio)}, which adds uncertainty [Ours].\n\n")
        to_come = ''
    text.append('![Forecast against what happened](../maps/notebook04/04_forecast_check.png)\n\n')
    text.append(f'*Figure 3. Weekly detections forecast by the three methods against what happened, weeks '
                f'{int(p.check.index.min())}–{int(p.check.index.max())} of the 2026 season{to_come} '
                f'[Ours, Notebook 04, data to {day(end)} 2026].*\n')
    return ''.join(text)


def findings_section(areas, ratio):
    p, s = areas['Punjab'], areas['Sangrur']
    first, last = int(p.done.index.min()), int(p.done.index.max())
    start, end = p.done['week_start'].iloc[0], p.done['week_end'].iloc[-1]
    text = []
    if not p.final:
        text.append('## 5. The 2026 forecast so far\n\n')
        text.append(f'With data to {day(end)} 2026, from the latest committed run of Notebook 04. This section is '
                    'rewritten after each weekly check by `report/update_forecast_text.py`, and the score is final '
                    'after 30 Nov.\n\n')
    else:
        text.append('## 5. The 2026 forecast, scored\n\n')
        text.append(f'Every forecast week has been checked, to {day(end)} 2026. Written by '
                    '`report/update_forecast_text.py` from the final run of Notebook 04.\n\n')
    text.append(issued_bullets(areas, 'findings'))
    label = 'Weeks checked so far' if not p.final else 'The weeks checked'
    text.append(f'- **{label}: {first}–{last}, {day(start)} to {day(end)}.** Week 7 was the last week Suomi NPP '
                'covered.\n')
    weeks = [f"{num(r['actual'])}{' detections' if i == 0 else ''} against {num(r[METHODS[0]])}"
             f"{' forecast' if i == 0 else ''} in week {int(w)} ({percent_off(r[METHODS[0]], r['actual'])})"
             for i, (w, r) in enumerate(p.done.iterrows())]
    text.append(f"  - **Punjab, week by week:** {ours(listed(weeks))}\n")
    if not p.final:
        for a in (p, s):
            o = off_by(a.totals[METHODS[0]], a.actual, 'level')
            prefix = '**Punjab, together:** ' if a is p else (
                f"**Sangrur:** {listed(small(v) for v in a.done['actual'])} against "
                f"{listed(small(v) for v in a.done[METHODS[0]])}: together ")
            text.append(f'  - {prefix}{num(a.actual)} against {num(a.totals[METHODS[0]])}{", " + o if o else ""}. '
                        + ours(f'{closest(a.totals, a.actual, "level")}{failed(a)}') + '\n')
    else:
        for a in (p, s):
            rest = {m: a.rest(m)['forecast_rest'] for m in METHODS}
            o = off_by(rest[METHODS[0]], a.actual, 'level')
            text.append(f"  - **{a.name}, weeks {first}–{last} together:** {num(a.actual)} against "
                        f"{num(rest[METHODS[0]])} forecast{', ' + o if o else ''}, "
                        f"{'inside' if inside_rest(a) else 'outside'} its 80% range of {num(a.head['rest_low'])}–"
                        f"{num(a.head['rest_high'])}; error factor {error_factor(rest[METHODS[0]], a.actual):.2f}, "
                        f"against a typical {float(a.head['typical_error_all']):.2f} in backtests. "
                        + ours(f"{closest(rest, a.actual, 'level')}{failed(a)}") + '\n')
    text.append(f'  - {peak_sentence(areas, p.final, "findings")}\n')
    if not p.final:
        text.append(f'- **The season so far.** {ours(season_so_far(p))}\n')
        if p.update is not None:
            u, v = p.update, s.update
            text.append(f"- **The updated forecast,** remade at each weekly run since 10 Nov beside the fixed one, which "
                        f"stays the test: on {day(u['issued_on'])} it put the season at {num(u['forecast_season'])} for "
                        f"Punjab and {num(v['forecast_season'])} for Sangrur, against {num(p.head['last_season'])} and "
                        f"{num(s.head['last_season'])} in 2025 [Ours].\n")
    else:
        text.append(f"- **The season,** in Suomi NPP terms: Punjab {num(p.seen)} against about "
                    f"{about(p.head['forecast_season'])} forecast and {num(p.head['last_season'])} in 2025; Sangrur "
                    f"{num(s.seen)} against about {about(s.head['forecast_season'])} and {num(s.head['last_season'])} in 2025 [Ours].\n")
    text.append('- **From week 8, counts come from NOAA-20.** Suomi NPP data stopped at 13:00 UTC on 2 Nov 2026 '
                f"[Reported]. So the actual counts are NOAA-20's, converted with the two sensors' 2026 ratio"
                f"{' (' + ratio + ')' if ratio else ''} [Ours].\n\n")
    text.append('Figure: `maps/notebook04/04_forecast_check.png`.\n')
    return ''.join(text)


def methodology_results(areas):
    p = areas['Punjab']
    if not p.final:
        return (f"final after 30 Nov; the weeks checked so far, to {day(p.done['week_end'].iloc[-1])}, are in "
                '`report/findings.md`, section 5.')
    parts = []
    for a in areas.values():
        h = a.head
        parts.append(f"{a.name}: {num(a.actual)} detections after week {int(h['issue_week'])} against "
                     f"{num(h['forecast_rest'])} forecast by {METHODS[0]} ({'inside' if inside_rest(a) else 'outside'} "
                     f"its range {num(h['rest_low'])}–{num(h['rest_high'])})")
    peak = peak_sentence(areas, True, 'findings').replace(' [Ours]', '').replace('**', '')
    return ('; '.join(parts) + f". {peak} "
            'Details in `report/findings.md`, section 5.')


def demo_answer(areas):
    p, s = areas['Punjab'], areas['Sangrur']
    if not p.final:
        n = len(p.done)
        o = off_by(p.totals[METHODS[0]], p.actual, 'level') or 'close'
        week = 'the busiest week so far was right' if p.peak_actual() == p.peak_forecast() else 'the busiest week was not'
        return (f"For Punjab's first {WORDS.get(n, n)} weeks it was {o}, and {week}; Sangrur's forecast, made from "
                f"{num(s.seen0)} detections, {'failed as flagged' if s.seen > s.season_high else 'is holding'}. "
                'Final score after 30 Nov')
    o = off_by(p.head['forecast_rest'], p.actual, 'level') or 'close'
    week = 'the busiest week was right' if p.peak_actual() == p.peak_forecast() else 'the busiest week was wrong'
    return (f"Over weeks {int(p.done.index.min())}–{int(p.done.index.max())} Punjab's was {o}, "
            f"{'inside' if inside_rest(p) else 'outside'} its 80% range, and {week}; Sangrur's, made from "
            f"{num(s.seen0)} detections, {'failed as flagged' if not inside_rest(s) else 'held'}")


def notebooks_clause(areas, today):
    # The end of Notebook 04's entry in the README's list of deliverables.
    p, s = areas['Punjab'], areas['Sangrur']
    if not p.final:
        run = pd.Timestamp(p.update['issued_on']) if p.update is not None else pd.Timestamp(today)
        return f'the latest run ({run.day} {run:%b %Y}) checks it to week {int(p.done.index.max())}'
    return (f"the final run ({today.day} {today:%b %Y}) scores the fixed one against every week to 30 Nov "
            f"(Punjab {'inside' if inside_rest(p) else 'outside'} its 80% range, Sangrur "
            f"{'inside' if inside_rest(s) else 'outside'})")


def report_status(areas, today):
    if not areas['Punjab'].final:
        end = day(areas['Punjab'].done['week_end'].iloc[-1])
        return (f'> **Status: interim.** Everything here is final except the 2026 forecast (section 6.5), which is '
                f'scored to {end} 2026 and will be finalised after 30 Nov 2026.')
    return f'> **Status: final** ({today.day} {today:%B %Y}). Section 6.5 scores the 2026 forecast against every week to 30 Nov 2026.'


def report_next_step(areas):
    if not areas['Punjab'].final:
        return '**Score the 2026 forecast** after 30 Nov and finalise section 6.5, in early December 2026.'
    return ('**Move the forecast to NOAA-20 and NOAA-21** for the 2027 season, since Suomi NPP data ended on 2 Nov 2026 '
            '[Recommendation].')


# ---- Writing them into the files ----------------------------------------------------------------------------------
def read(path):
    return path.read_bytes().decode('utf-8').replace('\r\n', '\n')


def write(path, text):
    # Keep the file's own line endings on any platform, so that git sees only the lines that changed.
    eol = '\r\n' if b'\r\n' in path.read_bytes() else '\n'
    path.write_bytes(text.replace('\n', eol).encode('utf-8'))


def between(text, name, new, path, inline=False):
    # Inline markers sit inside a line of text; block markers stand on lines of their own, with blank lines round the
    # passage so that what it holds (a quote, a figure) still renders as Markdown.
    start, end = f'<!-- forecast:{name} -->', f'<!-- /forecast:{name} -->'
    pattern = re.compile(re.escape(start) + r'(.*?)' + re.escape(end), re.S)
    if not pattern.search(text):
        sys.exit(f'{path}: markers for "{name}" not found')
    body = new if inline else '\n\n' + new.strip('\n') + '\n\n'
    return pattern.sub(lambda m: start + body + end, text, count=1)


def first_item(text, heading, new, path):
    # The first item of the numbered list under a heading. A marker can't open a list item: Markdown would read the
    # whole item as HTML.
    lines = text.split('\n')
    if heading not in lines:
        sys.exit(f'{path}: heading {heading!r} not found')
    i = lines.index(heading)
    j = next((k for k in range(i + 1, len(lines)) if lines[k].startswith('1. ')), None)
    if j is None:
        sys.exit(f'{path}: no numbered list under {heading!r}')
    lines[j] = '1. ' + new
    return '\n'.join(lines)


def clause(text, pattern, new, path):
    hits = re.findall(pattern, text)
    if len(hits) != 1:
        sys.exit(f'{path}: expected one match for {pattern!r}, found {len(hits)}')
    return re.sub(pattern, lambda m: new, text)


def row(text, begins, new_row, path):
    lines = text.split('\n')
    hits = [i for i, line in enumerate(lines) if line.startswith(begins)]
    if len(hits) != 1:
        sys.exit(f'{path}: expected one line starting {begins!r}, found {len(hits)}')
    lines[hits[0]] = new_row
    return '\n'.join(lines)


def rewrite(areas, ratio, today):
    final = areas['Punjab'].final
    changes = {}

    path = HERE / 'report.md'
    t = read(path)
    t = between(t, 'date', f'{today.day} {today:%B %Y}', path, inline=True)
    t = between(t, 'status', report_status(areas, today), path)
    t = between(t, 'section', report_section(areas, ratio), path)
    t = first_item(t, '## 10. Next steps', report_next_step(areas), path)
    changes[path] = t

    path = HERE / 'findings.md'
    changes[path] = between(read(path), 'section', findings_section(areas, ratio), path)

    path = PROJECT / 'methodology' / 'methodology.md'
    changes[path] = between(read(path), 'results', methodology_results(areas), path, inline=True)

    path = HERE / 'demo_script.md'
    changes[path] = row(read(path), '| And the 2026 forecast? |',
                        f'| And the 2026 forecast? | {demo_answer(areas)} | Section 6.5 |', path)

    path = PROJECT / 'README.md'
    t = read(path)
    t = clause(t, r'the (?:latest|final) run \(\d{1,2} [A-Z][a-z]{2} \d{4}\) (?:checks it to week \d+|scores the fixed '
                  r'one against every week to 30 Nov \([^)]*\))', notebooks_clause(areas, today), path)
    if final:
        t = t.replace(', to be scored after 30 Nov;', ';')
        t = t.replace('status-in%20progress-orange', 'status-complete-brightgreen')
        t = re.sub(r'\(\d+ pages; interim until the 2026 forecast is scored after 30 Nov 2026\)', '(final)', t)
        t = row(t, '| 6 | Technical and product report',
                f"| 6 | Technical and product report, 8–12 pages | `report/report.pdf` | Final ({today.day} "
                f"{today:%b %Y}): built from `report/report.md` by `report/build_report.py`, with the 2026 forecast "
                "scored against every week to 30 Nov. Its working drafts: `findings.md`, `mission_tradeoff.md`, "
                "`ml_classifier.md` and `limitations.md` |", path)
        t = row(t, '| Final |', f'| Final | {today.day} {today:%b} | The 2026 forecast scored and the report finalised |',
                path)
    changes[path] = t

    if final:
        path = HERE / 'README.md'
        changes[path] = read(path).replace(
            ' Interim until the 2026 forecast is scored after 30 Nov 2026.', '')
    return changes


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--check', action='store_true', help='show what would change, and write nothing')
    parser.add_argument('--data', type=Path, default=PROJECT / 'data' / 'processed')
    parser.add_argument('--today', type=dt.date.fromisoformat, default=dt.date.today())
    args = parser.parse_args()
    areas, ratio = load(args.data)
    changes = rewrite(areas, ratio, args.today)
    state = 'final' if areas['Punjab'].final else f"interim, to week {int(areas['Punjab'].done.index.max())}"
    changed = False
    for path, new in changes.items():
        old = read(path)
        if old == new:
            continue
        changed = True
        if args.check:
            sys.stdout.writelines(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                                                       str(path.relative_to(PROJECT)), str(path.relative_to(PROJECT))))
        else:
            write(path, new)
            print(f'{path.relative_to(PROJECT)}: rewritten')
    if not changed:
        print(f'Forecast passages: {state}. Already up to date.')
    else:
        print(f'Forecast passages: {state}.' + (' Nothing written (--check).' if args.check else
                                                ' Now rebuild the PDFs: python report/build_report.py'))


if __name__ == '__main__':
    main()
