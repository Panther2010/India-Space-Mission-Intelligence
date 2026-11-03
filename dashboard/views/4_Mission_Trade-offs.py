"""Mission Trade-offs: which satellite data fits the straw buyer, compared on the brief's six factors.

The page reads report/mission_tradeoff.md, so the report draft stays the one source: section 4's numbered list becomes
the option cards, section 3 stays in view, and the rest sits in expanders.
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


c.page_header('balance', 'Mission Trade-offs',
              'Six data options compared on the brief\'s six factors, and which to use: the report draft, shown as '
              'written.')
draft = c.text(PATH)
if draft is None:
    c.missing(PATH)
    st.stop()

parts = sections(draft)
pick_heading, pick = find(parts, 4)
items = re.findall(r'^\d+\.\s+\*\*(.+?)\*\*\s*(.*)$', pick or '', flags=re.M)
if len(items) < 3:                                     # the draft changed shape: show it as written
    st.markdown(draft.split('\n', 1)[1] if draft.startswith('# ') else draft)
else:
    st.markdown(parts[''].split('\n\n')[0])
    st.subheader(unnumbered(pick_heading))
    lead = pick.split('\n')[0]
    if not re.match(r'^\d+\.', lead):
        st.markdown(lead)
    for row in range(0, len(items), 3):
        cols = st.columns(3, gap='medium')
        for col, (n, (title, body)) in zip(cols, enumerate(items[row:row + 3], start=row + 1)):
            with col:
                with st.container(border=True):
                    st.markdown(f'#### {n}. {title.rstrip(".")}')
                    st.markdown(body)
    shown_heading, shown = find(parts, 3)
    if shown:
        st.subheader(unnumbered(shown_heading))
        st.markdown(shown)
    for number in (1, 2, 5):
        heading, body = find(parts, number)
        if body:
            with st.expander(unnumbered(heading)):
                st.markdown(body)
    labels = parts[''].split('\n\n', 2)[2] if parts[''].count('\n\n') >= 2 else ''
    with st.expander('Labels and sources'):
        st.markdown(labels + '\n\n' + parts.get('Sources', ''))
c.footer('From the report draft `report/mission_tradeoff.md`.')
