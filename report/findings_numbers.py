"""Print every number used in report/findings.md and in sections 3 and 6 of report/report.md, from committed files.

Reads data/processed/ and dataset A only, and downloads nothing. The recurrence of burning on the same land needs the two 20 m burn
maps and rasterio (in the project's environment); without rasterio that part is skipped.

Run from the project folder:  python report/findings_numbers.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

P = Path(__file__).resolve().parent.parent / 'data' / 'processed'


def show(label, value):
    print(f'  {label}: {value}')


def summary(year):
    return pd.read_csv(P / f's2_burn_summary_sangrur_{year}.csv').set_index('metric')['value']


def burnt_and_harvest(s):
    print('1. Burnt area, 2025 (Notebook 02)')
    show('harvested ha', f"{float(s['harvested_ha']):,.0f}")
    show('burnt ha, confirmed', f"{float(s['burnt_ha']):,.0f}")
    show('burnt share of harvested', s['burnt_share_of_harvested'])
    show('late burns from 19 Nov, unconfirmed, ha', f"{float(s['burnt_unconfirmed_ha']):,.0f}")
    show('harvested, not seen burnt, ha', f"{float(s['harvested_not_burnt_ha']):,.0f}")
    show('median days from harvest to burn', s['median_days_harvest_to_burn'])


def validation():
    print('2. Accuracy (Notebook 02, labels of 30-31 Oct 2026)')
    acc = pd.read_csv(P / 'validation_accuracy_sangrur_2025.csv')
    row = acc[acc['rule'].str.startswith('map as reported') & (acc['scored_on'] == 'all labelled points')].iloc[0]
    for col in ['points', 'precision', 'recall', 'f1', 'users_accuracy_burnt', 'producers_accuracy_burnt',
                'overall_accuracy', 'overall_accuracy_se']:
        show(col, round(float(row[col]), 3))
    bounds = pd.read_csv(P / 'validation_unsure_bounds_sangrur_2025.csv')
    for _, r in bounds[bounds['scored_on'] == 'all labelled points'].iterrows():
        show(f"{r['case']}: F1, overall accuracy", f"{r['f1']:.3f}, {r['overall_accuracy']:.3f}")
    area = pd.read_csv(P / 'validation_area_estimate_sangrur_2025.csv')
    for _, r in area.iterrows():
        show(f"burnt ha from labels, {r['case']}",
             f"{r['burnt_ha_from_labels']:,.0f} (95% CI {r['ci95_low_ha']:,.0f}-{r['ci95_high_ha']:,.0f})")
    labels = pd.read_csv(P / 'validation_labels_sangrur_2025.csv')
    show('labels', labels['burnt'].value_counts().to_dict())


def missed(s):
    print('3. What the fire counts missed, 2025 (Notebook 02)')
    for key in ['missed_share_viirs_375m', 'missed_share_viirs_750m', 'missed_share_viirs_750m_or_modis_1000m',
                'missed_share_viirs_375m_including_unconfirmed', 'viirs_detections_inside', 'modis_detections_inside']:
        show(key, s[key])
    bw = pd.read_csv(P / 's2_burn_by_window_sangrur_2025.csv')
    peak = bw[bw['window_start'].isin(['2025-10-30', '2025-11-04', '2025-11-09'])]
    for _, r in peak.iterrows():
        show(f"window {r['window_start']}: share of burnt area flagged",
             f"{r['burnt_flagged_ha'] / r['burnt_ha']:.3f} ({r['viirs_detections_inside']} VIIRS detections)")
    det = pd.read_csv(P / 'firms_detections_sangrur_2025.csv')
    inside = det[det['inside']].copy()
    hhmm = pd.to_datetime(inside['acq_time'].astype(int).astype(str).str.zfill(4), format='%H%M')
    inside['ist'] = (hhmm + pd.to_timedelta(330, unit='min')).dt.strftime('%H:%M')
    viirs = inside[inside['sensor'].str.startswith('VIIRS')]
    day = viirs[(viirs['ist'] >= '06:00') & (viirs['ist'] < '18:00')]
    show('VIIRS detections inside', len(viirs))
    show('VIIRS daytime detections, earliest and latest IST', f"{day['ist'].min()}, {day['ist'].max()} ({len(day)})")
    show('VIIRS night detections', f'{len(viirs) - len(day)} ({(len(viirs) - len(day)) / len(viirs):.3f})')
    show('VIIRS detections in the three busiest windows together', int(peak['viirs_detections_inside'].sum()))
    modis = inside[inside['sensor'] == 'MODIS']
    show('MODIS detections inside, earliest and latest IST', f"{modis['ist'].min()}, {modis['ist'].max()}")


def timing():
    print('4. Timing, 2025 (Notebook 02)')
    bw = pd.read_csv(P / 's2_burn_by_window_sangrur_2025.csv')
    harvest_half = bw.loc[bw['harvested_ha'].cumsum() >= bw['harvested_ha'].sum() / 2, 'window_start'].iloc[0]
    confirmed = bw[bw['burns_confirmed']]
    burn_half = confirmed.loc[confirmed['burnt_ha'].cumsum() >= confirmed['burnt_ha'].sum() / 2,
                              'window_start'].iloc[0]
    show('half the harvest first seen by the window starting', harvest_half)
    show('half the confirmed burnt area first seen by the window starting', burn_half)
    top = confirmed.nlargest(1, 'burnt_ha').iloc[0]
    show('busiest window for burning', f"{top['window_start']} ({top['burnt_ha']:,.0f} ha, "
         f"{top['burnt_ha'] / confirmed['burnt_ha'].sum():.3f} of confirmed)")
    three = confirmed[confirmed['window_start'].isin(['2025-10-30', '2025-11-04', '2025-11-09'])]['burnt_ha'].sum()
    show('share of confirmed burnt area first seen 30 Oct-13 Nov', f"{three / confirmed['burnt_ha'].sum():.3f}")
    busiest = bw.nlargest(1, 'viirs_detections_inside').iloc[0]
    show('busiest window for VIIRS detections', f"{busiest['window_start']} ({busiest['viirs_detections_inside']})")
    straw = pd.read_csv(P / 'straw_by_window_sangrur_2025.csv').groupby('window_start')['fresh_straw_ha'].sum()
    show('fresh straw at the peak (harvested in the 10 days to the window\'s end, not seen burnt)',
         f"{straw.max():,.0f} ha, window starting {straw.idxmax()}")
    season = bw[bw['window_start'] >= '2025-10-15']
    show('clear share below 0.999 from 15 Oct', season.loc[season['clear_share_of_area'] < 0.999,
                                                           ['window_start', 'clear_share_of_area']].values.tolist())


def classifiers():
    print('4b. Machine learning (Notebook 03 and report/compare_classifiers.py)')
    comp = pd.read_csv(P / 'ml_model_comparison_sangrur_2025.csv')
    for _, r in comp.iterrows():
        p_min = '' if pd.isna(r['mcnemar_p_min']) else f", lowest McNemar p {r['mcnemar_p_min']:.3f}"
        show(r['method'], f"F1 {r['f1_mean']:.3f} ({r['f1_min']:.3f}-{r['f1_max']:.3f}){p_min}")
    curve = pd.read_csv(P / 'ml_learning_curve_sangrur_2025.csv')
    show('Random Forest F1 by training points', dict(zip(curve['training_points'], curve['f1_mean'].round(3))))


def comparison():
    print('5. 2021 against 2025 (Notebook 02c)')
    comp = pd.read_csv(P / 'season_comparison_sangrur.csv').set_index('measure')
    for measure in ['harvested area (ha)', 'burnt area, confirmed (ha)',
                    'burnt area, including unconfirmed late burns (ha)',
                    'burnt share of land harvested in both seasons',
                    'Suomi NPP detections inside', 'Suomi NPP detections per 1,000 ha burnt',
                    'missed share, Suomi NPP and NOAA-20 only (375 m)',
                    'Sentinel-2 dates over the pilot box, 15 Oct to 24 Nov']:
        r = comp.loc[measure]
        change = r['relative change'] if pd.notna(r['relative change']) else r['difference']
        show(measure, f"2021 {r['2021']:,.3f}, 2025 {r['2025']:,.3f}, change {change:+.3f}")
    bands = pd.read_csv(P / 'season_comparison_by_band_sangrur.csv')
    for _, r in bands.iterrows():
        show(f"{r['band']}: change confirmed, including late burns",
             f"{r['change, confirmed']:+.3f}, {r['change, including late burns']:+.3f}")
    cells = {}
    for year in (2021, 2025):
        grid = json.loads((P / f's2_burn_grid_1km_sangrur_{year}.geojson').read_text(encoding='utf-8'))
        cells[year] = {f['properties']['cell']: f['properties'] for f in grid['features']}
    pairs = [(cells[2021][k], cells[2025][k]) for k in cells[2021] if k in cells[2025]]

    def total(p, late):
        return (p.get('burnt_ha') or 0) + ((p.get('burnt_unconfirmed_ha') or 0) if late else 0)
    for late in (False, True):            # as Notebook 02c: share of all the district's squares
        fell = sum(total(b, late) < total(a, late) for a, b in pairs)
        show(f"1 km squares where burning fell{' (with late burns)' if late else ''}",
             f'{fell / len(pairs):.3f} of {len(pairs)}')
    state = pd.read_csv(P / 'firms_detections_by_season_state.csv').set_index('season')
    show('Punjab Suomi NPP detections 2021, 2025 (15 Sep-30 Nov, Notebook 01)',
         f"{state.loc[2021, 'Punjab']:,}, {state.loc[2025, 'Punjab']:,} "
         f"({state.loc[2025, 'Punjab'] / state.loc[2021, 'Punjab'] - 1:+.3f})")
    try:
        import rasterio
    except ImportError:
        show('same land', 'skipped: needs rasterio')
        return
    # Band 1 holds the class (data/processed/README.md): 3 burnt and flagged by VIIRS, 4 burnt and missed, so 3 or 4
    # is a confirmed burn; 5 is a burn from 19 Nov, unconfirmed.
    with rasterio.open(P / 's2_burn_classes_sangrur_2021.tif') as a, \
            rasterio.open(P / 's2_burn_classes_sangrur_2025.tif') as b:
        c21, c25 = a.read(1), b.read(1)
    if c21.shape != c25.shape:
        show('same land', 'skipped: the two maps are on different grids')
        return
    # As Notebook 02c: confirmed burns on the land harvested in both seasons (classes 2 to 5 in both maps).
    harvested_both = np.isin(c21, (2, 3, 4, 5)) & np.isin(c25, (2, 3, 4, 5))
    b21, b25 = np.isin(c21, (3, 4)) & harvested_both, np.isin(c25, (3, 4)) & harvested_both
    show('land harvested in both seasons: share of 2025 burnt area also burnt in 2021',
         f'{(b25 & b21).sum() / b25.sum():.3f}')
    show('land harvested in both seasons: share of 2021 burnt area burnt again in 2025',
         f'{(b25 & b21).sum() / b21.sum():.3f}')


def forecast():
    print('6. The 2026 forecast and its check (Notebook 04)')
    summ = pd.read_csv(P / 'fire_forecast_2026_summary.csv')
    for _, r in summ[summ['headline']].iterrows():
        show(f"{r['area']}: seen to {r['data_through']}, forecast rest (80% range), season (80% range), last season, "
             'peak',
             f"{r['seen_so_far']:,.0f}; {r['forecast_rest']:,} ({r['rest_low']:,}-{r['rest_high']:,}); "
             f"{r['forecast_season']:,} ({r['seen_so_far'] + r['rest_low']:,.0f}-{r['seen_so_far'] + r['rest_high']:,.0f}); "
             f"{r['last_season']:,.0f}; {r['peak_week_dates']} in {r['peak_week_share']:.2f} of scenarios")
    check = pd.read_csv(P / 'fire_forecast_check_2026.csv')
    done = check[check['actual'].notna()]
    for _, r in done.iterrows():
        show(f"{r['area']} week {r['week']} ({r['actual_source']})",
             f"actual {r['actual']:,.0f}; headline {r['past seasons rescaled']:,.1f} "
             f"(x{r['past seasons rescaled'] / r['actual']:.2f}); last season {r['last season']:,.0f}; "
             f"SARIMA {r['SARIMA']:,.0f}")
    methods = ['past seasons rescaled', 'last season', 'SARIMA']
    for area, g in done.groupby('area'):
        actual = g['actual'].sum()
        show(f"{area}, weeks {g['week'].min()}-{g['week'].max()} together",
             f"actual {actual:,.0f}; " + '; '.join(f"{m} {g[m].sum():,.0f} (x{g[m].sum() / actual:.2f})"
                                                   for m in methods))
    updates = pd.read_csv(P / 'fire_forecast_2026_updates_summary.csv')
    for _, r in updates[updates['issue_week'] == updates['issue_week'].max()].iterrows():
        show(f"{r['area']}: updated forecast issued {r['issued_on']}, data to {r['data_through']}",
             f"seen so far {r['seen_so_far']:,.0f}; season {r['forecast_season']:,}; busiest week {r['busiest_week']}")


def ecosystem():
    print('7. Dataset A, the Indian space ecosystem (report section 3)')
    a = pd.read_csv(P.parent / 'raw' / 'research' / 'dataset_A_india_space_ecosystem.csv')
    show('companies', len(a))
    show('by category', a['value_chain_category'].value_counts().to_dict())
    show('by state', a['state'].fillna('not stated').value_counts().to_dict())
    show('in Bengaluru', int((a['city'] == 'Bengaluru').sum()))
    near = a[a['value_chain_category'].isin(['Earth Observation', 'Space Data/Analytics'])]
    show('in Earth observation or space data', f"{len(near)}: {', '.join(near['company'])}")


if __name__ == '__main__':
    s25 = summary(2025)
    burnt_and_harvest(s25)
    validation()
    missed(s25)
    timing()
    classifiers()
    comparison()
    forecast()
    ecosystem()
