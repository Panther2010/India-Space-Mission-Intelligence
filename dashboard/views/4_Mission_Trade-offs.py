"""Mission Trade-offs: which satellite data fits the straw buyer, compared on the brief's six factors."""
import streamlit as st

import common as c


PATH = c.REPORT / 'mission_tradeoff.md'
draft = c.text(PATH)
if draft is None:
    st.title('Mission Trade-offs')
    c.missing(PATH)
else:
    st.markdown(draft)
c.footer('From the report draft `report/mission_tradeoff.md` (31 Oct 2026).')
