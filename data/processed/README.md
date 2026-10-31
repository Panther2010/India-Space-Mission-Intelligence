# Processed data

Files here are written by the notebooks (the two boundary outlines by `maps/build_qgis_project.py`) and can be recreated by re-running them. Small tables are committed; large point files (`*.parquet`) and rasters (`*.tif`) are not, except the final Sangrur burn map, which the QGIS project needs, and Notebook 03's agreement map. The validation label sheet is the exception to "recreated": it holds hand-made labels, so it is committed and never overwritten.

| File | Written by | Contents |
|---|---|---|
| `firms_viirs_punjab_haryana_points.parquet` | Notebook 01 | Clean VIIRS detections with district, state and IST time |
| `firms_detections_by_season_state.csv` | Notebook 01 | Suomi NPP detections per season and state |
| `firms_detections_by_district_season.csv` | Notebook 01 | Detections per district and season, with 2021–2025 totals and change |
| `firms_snpp_noaa20_ratio.csv` | Notebook 01 | Suomi NPP to NOAA-20 detection ratio, 2020–2025 |
| `district_shortlist.csv` | Notebook 01 | Top three districts for Checkpoint 1 |
| `s2_burn_classes_<area>_2025.tif` | Notebook 02 | 20 m GeoTIFF, four bands: class (1 not a harvested crop, 2 harvested but not burnt, 3 burnt and flagged by VIIRS, 4 burnt and missed, 5 burnt from 19 Nov and unconfirmed), burn window, harvest window, last clear view before the burn (windows numbered from 1; 0 = none). Committed for Sangrur only. |
| `s2_burn_summary_<area>_2025.csv` | Notebook 02 | Headline numbers: harvested area, confirmed and unconfirmed burnt area, missed shares of confirmed burns under three matching rules, the rule and its status, FIRMS products used, credits |
| `s2_burn_by_window_<area>_2025.csv` | Notebook 02 | Per 5-day window: share of the area seen clearly, hectares harvested and burnt, detections, and whether the window's burns count as confirmed |
| `s2_burn_grid_1km_<area>_2025.geojson` | Notebook 02 | 1 km squares for the dashboard: harvested, burnt (confirmed), unconfirmed and missed hectares, mean harvest and burn timing |
| `firms_detections_<area>_2025.csv` | Notebook 02 | VIIRS and MODIS detections used for matching, with their 5-day window |
| `s2_scl_check_pilot_2025.csv` | Notebook 02 | Scene class of burnt-looking pixels on single dates in the pilot box |
| `validation_points_sangrur_2025.csv` | Notebook 02 | The 240 validation points with their sampling class and half (A or B). Not for labelling: it shows the map's class. |
| `validation_labels_sangrur_2025.csv` | Notebook 02, then by hand | Blind label sheet: burnt yes / no / unsure for each point |
| `validation_accuracy_sangrur_2025.csv` | Notebook 02 | Accuracy of the suggested rule, the thresholds in Settings and the map as reported, on half B and on all labelled points |
| `validation_area_estimate_sangrur_2025.csv` | Notebook 02 | Burnt area from the labels alone, with a 95% confidence interval, with `unsure` points left out, counted as not burnt and counted as burnt |
| `validation_unsure_bounds_sangrur_2025.csv` | Notebook 02 | Accuracy of the map as reported, with `unsure` points left out, counted as not burnt and counted as burnt |
| `validation_late_window_check_sangrur_2025.csv` | Notebook 02 | Labels against the window in which the rule first calls each point burnt (before or from 19 Nov) |
| `burn_rule_calibration_grid_sangrur_2025.csv` | Notebook 02 | F1 on half A for every combination of thresholds tried |
| `hls_l30_scenes_sangrur_2025.csv` | Notebook 02b | Landsat (HLSL30) scenes over the validation points: tile, date, cloud cover, whether read, points inside |
| `validation_landsat_views_sangrur_2025.csv` | Notebook 02b | For each point read: its Landsat strip, and its clear, hazy and cloudy Landsat dates. It lists dates and notes, not the map's class, so it is safe to open while relabelling. |
| `ml_point_features_sangrur_2025.csv` | Notebook 03 | The 240 validation points: label, the rule's calls (map as reported and every burn), the forest's out-of-sample probability of a burn, the half-A forest's call on half B, and the 23 season features |
| `ml_accuracy_sangrur_2025.csv` | Notebook 03 | Precision, recall, F1 and area-weighted accuracy of the rule and the Random Forest: on half B, and on all labelled points (the forest cross-validated: mean, lowest and highest of 10 runs) |
| `ml_learning_curve_sangrur_2025.csv` | Notebook 03 | The forest's F1 on held-out points by number of training points, with the rule's F1 on the same points |
| `ml_feature_importance_sangrur_2025.csv` | Notebook 03 | Drop in the forest's F1 when each feature, or each group of related features, is shuffled |
| `ml_map_comparison_sangrur_2025.csv` | Notebook 03 | The forest's and the rule's maps compared: hectares burnt in each, in both and in one only; the labels' estimate; shares of disagreeing pixels on patch edges and in patches under 1 ha |
| `ml_burn_agreement_sangrur_2025.tif` | Notebook 03 | 20 m GeoTIFF on the class map's grid: 1 not a harvested crop, 2 harvested and burnt in neither map, 3 burnt in both, 4 burnt in the rule's map only, 5 burnt in the forest's map only (0 = outside the district). Committed. |
| `fire_weekly_counts.csv` | Notebook 04 | Suomi NPP and NOAA-20 detections per week (15 Sep to 30 Nov) in Punjab and Sangrur, 2012–2026, with whether each 2026 week is complete |
| `fire_forecast_backtests.csv` | Notebook 04 | Each method's forecast of the rest of every season 2016–2025, from the same week as the 2026 forecast, against what happened |
| `fire_forecast_2026.csv` | Notebook 04 | The 2026 forecast week by week, as issued. Written once and never overwritten |
| `fire_forecast_2026_summary.csv` | Notebook 04 | The 2026 forecast in brief, as issued: rest-of-season total and its 80% range, busiest week, the headline method and its typical backtest error |
| `fire_forecast_check_2026.csv` | Notebook 04 | The forecast against the weeks that have ended: Suomi NPP to 2 Nov, then NOAA-20 converted. Refreshed at each run |
| `boundary_sangrur_pre2021.geojson` | `maps/build_qgis_project.py` | Sangrur district outline (pre-2021 boundary, includes Malerkotla), the polygon Notebook 02 analyses, from geoBoundaries IND ADM2. Under the Open Database License (ODbL 1.0), like its source. |
| `boundary_punjab.geojson` | `maps/build_qgis_project.py` | Punjab outline from geoBoundaries IND ADM1 (DataMeet and the Election Commission of India), simplified, for the map inset. CC BY 2.5 IN. |

`<area>` is `pilot` (a 10 km box) or `sangrur` (the whole district, pre-2021 boundary).
