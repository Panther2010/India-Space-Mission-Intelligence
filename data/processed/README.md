# Processed data

Files here are written by the notebooks and can be recreated by re-running them. Small tables are committed; large point files (`*.parquet`) and rasters (`*.tif`) are not, except the final Sangrur burn map, which the QGIS project needs. The validation label sheet is the exception to "recreated": it holds hand-made labels, so it is committed and never overwritten.

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

`<area>` is `pilot` (a 10 km box) or `sangrur` (the whole district, pre-2021 boundary).
