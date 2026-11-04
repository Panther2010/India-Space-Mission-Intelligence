"""Mission Trade-offs: which satellite data fits the straw buyer, compared on the brief's six factors.

The page reads report/mission_tradeoff.md, so the report draft stays the one source: section 4's numbered list becomes
the option cards up front, and sections 3, 1, 2 and 5 and the labels and sources become tabs.
"""
import re

import streamlit as st

import common as c

PATH = c.REPORT / 'mission_tradeoff.md'


def sections(draft):
    """The draft's '## ' sections as heading -> body, with the text before the first one under ''."""
    parts, heading = {'': []}, ''
    for line in draft.split('\n')[1:]:                 # the first line is the draft's own title
        if line.startswith('## '):
            heading = line[3:].strip()
            parts[heading] = []
        else:
            parts[heading].append(line)
    return {k: '\n'.join(v).strip() for k, v in parts.items()}


def find(parts, number):
    return next(((k, v) for k, v in parts.items() if k.startswith(f'{number}.')), (None, None))


def unnumbered(heading):
    return re.sub(r'^\d+\.\s*', '', heading)


draft = c.text(PATH)
if draft is None:
    c.page_header('Mission Trade-offs')
    c.missing(PATH)
    st.stop()

parts = sections(draft)
pick_heading, pick = find(parts, 4)
items = re.findall(r'^\d+\.\s+\*\*(.+?)\*\*\s*(.*)$', pick or '', flags=re.M)
c.page_header('Mission Trade-offs',
              'Six data options compared on the brief\'s six factors, and which to use: the report draft, shown as '
              'written.',
              eyebrow='Report draft · mission trade-off')
if len(items) < 3:                                     # the draft changed shape: show it as written
    st.markdown(draft.split('\n', 1)[1] if draft.startswith('# ') else draft)
else:
    # ---- The recommendation up front, one card per option ----------------------------------------------------
    with c.panel('pick'):
        c.eyebrow(unnumbered(pick_heading), 'scale', c.EMBER)
        st.markdown(parts[''].split('\n\n')[0])
        lead = pick.split('\n')[0]
        if not re.match(r'^\d+\.', lead):
            st.markdown(f'**{lead}**')
        for row in range(0, len(items), 3):
            cols = st.columns(3, gap='medium')
            for col, (n, (title, body)) in zip(cols, enumerate(items[row:row + 3], start=row + 1)):
                with col:
                    with c.card(f'option_{n}'):
                        c.html(f'<div class="mc-eyebrow">Option {n}</div>'
                               f'<div class="mc-card-title">{c.esc(title.rstrip("."))}</div>')
                        st.markdown(body)

    # ---- The rest of the draft, one tab at a time -------------------------------------------------------------
    # Short tab names by section number; each tab shows the section's own heading.
    short = {3: 'What 2025 showed', 1: 'The requirement', 2: 'The six factors', 5: 'Validation'}
    rest = []
    for number in (3, 1, 2, 5):
        heading, body = find(parts, number)
        if body:
            rest.append((short[number], unnumbered(heading), body))
    labels = parts[''].split('\n\n', 2)[2] if parts[''].count('\n\n') >= 2 else ''
    rest.append(('Sources', 'Labels and sources', labels + '\n\n' + parts.get('Sources', '')))
    with c.panel('draft'):
        for tab, (_, heading, body) in zip(st.tabs([name for name, _, _ in rest]), rest):
            with tab:
                c.eyebrow(c.esc(heading))
                st.markdown(body)
c.footer('From the report draft `report/mission_tradeoff.md`.')
