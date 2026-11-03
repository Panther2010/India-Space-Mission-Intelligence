"""Mission Trade-offs: which satellite data fits the straw buyer, compared on the brief's six factors."""
import streamlit as st

import common as c


PATH = c.REPORT / 'mission_tradeoff.md'
draft = c.text(PATH)
c.page_header('balance', 'Mission Trade-offs',
              'Six data options compared on the brief\'s six factors, and which to use: the report draft, '
              'shown as written.')
if draft is None:
    c.missing(PATH)
else:
    # The page header replaces the draft's own title.
    st.markdown(draft.split('\n', 1)[1] if draft.startswith('# ') else draft)
c.footer('From the report draft `report/mission_tradeoff.md` (31 Oct 2026).')
