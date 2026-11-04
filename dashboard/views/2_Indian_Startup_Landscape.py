"""Indian Startup Landscape: Indian space companies across the value chain (dataset A)."""
import altair as alt
import folium
from folium.plugins import MarkerCluster
import streamlit as st

import common as c

PATH = c.RESEARCH / 'dataset_A_india_space_ecosystem.csv'
companies = c.csv(PATH)
if companies is None:
    c.page_header('Indian Startup Landscape')
    c.missing(PATH)
    st.stop()

# Approximate city centres, for placing markers only (our lookup, not company addresses). Vemagal: indiamapia.com.
CITY = {
    'Ahmedabad': (23.0225, 72.5714), 'Bengaluru': (12.9716, 77.5946), 'Chennai': (13.0827, 80.2707),
    'Gurugram': (28.4595, 77.0266), 'Hyderabad': (17.3850, 78.4867), 'Mumbai': (19.0760, 72.8777),
    'Navi Mumbai': (19.0330, 73.0297), 'Noida': (28.5355, 77.3910), 'Thane': (19.2183, 72.9781),
    'Thiruvananthapuram': (8.5241, 76.9366), 'Vemagal': (13.1824, 78.0325), 'Visakhapatnam': (17.6868, 83.2185),
}
CATEGORY_COLOURS = {
    'Launch': '#4e79a7', 'Propulsion': '#f28e2b', 'Satellites': '#59a14f', 'Earth Observation': '#e15759',
    'Components': '#b07aa1', 'Ground Systems': '#9c755f', 'Space Data/Analytics': '#76b7b2',
}
NEAR = ['Earth Observation', 'Space Data/Analytics']

c.page_header('Indian Startup Landscape',
              f'{len(companies)} Indian space companies across the seven value-chain categories of the brief, each '
              'with the page it came from and the date that page was read. Company statements, such as press '
              'releases, are flagged in the notes. [Reported]',
              eyebrow='Research · dataset A',
              pill='<i class="mc-dot amber"></i>Spot-check <b>in progress</b>')

# ---- The key numbers up front ------------------------------------------------------------------------------------
states = companies['state'].value_counts()
c.tiles([c.tile('rocket', f'{len(companies)}', '', 'Indian space companies'),
         c.tile('layers', f"{companies['value_chain_category'].nunique()}", '', 'Value-chain categories'),
         c.tile('map-pin', f'{states.iloc[0]}', '', f'In {c.esc(states.index[0])}, the most of any state',
                f"{companies['state'].nunique()} states"),
         c.tile('satellite-dish', f"{companies['value_chain_category'].isin(NEAR).sum()}", '',
                'In Earth observation and space data', 'closest to this product', glow='ember')],
        note='Dataset A is being spot-checked, so some rows may still change.')

# ---- The rest, one tab at a time ----------------------------------------------------------------------------------
with c.panel('startups'):
    left, right = st.columns(2)
    categories = left.multiselect('Value-chain category', list(CATEGORY_COLOURS))
    chosen_states = right.multiselect('State', sorted(companies['state'].dropna().unique()))
    shown = companies
    if categories:
        shown = shown[shown['value_chain_category'].isin(categories)]
    if chosen_states:
        shown = shown[shown['state'].isin(chosen_states)]
    c.html(f'<div class="mc-small">{len(shown)} of {len(companies)} shown, on every tab.</div>')

    t_map, t_counts, t_table, t_near = st.tabs(['Map', 'By category and state', 'All companies',
                                                'Closest to this product'])
    with t_map:
        m = c.dark_map(folium.Map(location=(21.5, 79.0), zoom_start=5, tiles='OpenStreetMap'))
        cluster = MarkerCluster().add_to(m)
        for _, r in shown.iterrows():
            if r['city'] not in CITY:
                continue
            colour = CATEGORY_COLOURS.get(r['value_chain_category'], '#555555')
            folium.CircleMarker(
                CITY[r['city']], radius=8, color=colour, fill=True, fill_color=colour, fill_opacity=0.85,
                tooltip=f"{r['company']} ({r['value_chain_category']})",
                popup=folium.Popup(f"<b>{r['company']}</b><br>{r['city']}, {r['state']}<br>"
                                   f"{r['value_chain_category']}<br><br>{r['product_or_capability']}", max_width=320),
            ).add_to(cluster)
        c.show_map(m, height=520, key='companies')
        unplaced = shown.loc[~shown['city'].isin(list(CITY)), 'company'].tolist()
        st.caption('Markers sit at approximate city centres, not company addresses; click a cluster to spread it.'
                   + (' Not on the map (no city in the source): ' + '; '.join(unplaced) + '.' if unplaced else ''))

    with t_counts:
        a, b = st.columns(2, gap='large')
        counts = shown['value_chain_category'].value_counts().rename_axis('category').reset_index(name='companies')
        a.altair_chart(alt.Chart(counts).mark_bar().encode(
            x=alt.X('companies:Q', title='companies'),
            y=alt.Y('category:N', sort='-x', title=None, axis=alt.Axis(labelLimit=220)),
            color=alt.Color('category:N', scale=alt.Scale(domain=list(CATEGORY_COLOURS),
                                                          range=list(CATEGORY_COLOURS.values())), legend=None),
            tooltip=['category', 'companies']).properties(title='By value-chain category', width='container'))
        by_state = shown['state'].fillna('not stated').value_counts().rename_axis('state').reset_index(name='companies')
        b.altair_chart(alt.Chart(by_state).mark_bar(color='#4e79a7').encode(
            x=alt.X('companies:Q', title='companies'), y=alt.Y('state:N', sort='-x', title=None),
            tooltip=['state', 'companies']).properties(title='By state', width='container'))

    with t_table:
        st.dataframe(
            shown[['company', 'value_chain_category', 'city', 'state', 'product_or_capability',
                   'target_customer_or_application', 'evidence_url', 'date_accessed', 'notes']],
            hide_index=True,
            column_config={
                'company': 'Company', 'value_chain_category': 'Category', 'city': 'City', 'state': 'State',
                'product_or_capability': 'Product or capability', 'target_customer_or_application': 'Customers or use',
                'evidence_url': st.column_config.LinkColumn('Source', display_text='open'), 'date_accessed': 'Read on',
                'notes': 'Notes',
            })

    with t_near:
        near = shown[shown['value_chain_category'].isin(NEAR)]
        if near.empty:
            st.caption('None of the companies shown are in Earth observation or space data.')
        else:
            c.eyebrow('Could supply imagery or build a similar service [Recommendation]')
            c.html('<div class="mc-card" style="margin-top:.7rem">'
                   + ''.join(f'<div class="mc-pipe"><i class="mc-dot plain"></i><div><strong>{c.esc(r.company)}</strong>'
                             f'<em>{c.esc(r.product_or_capability)}</em></div><span class="mc-chip">'
                             f'{c.esc(r.value_chain_category)}</span></div>' for r in near.itertuples())
                   + '</div>')

c.footer('Source: `data/raw/research/dataset_A_india_space_ecosystem.csv`.')
