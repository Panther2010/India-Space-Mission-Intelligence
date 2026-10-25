# Processed data

Files here are written by the notebooks and can be recreated by re-running them. Small tables are committed; large point files (`*.parquet`) and rasters (`*.tif`) are not. The validation label sheet is the exception to "recreated": it holds hand-made labels, so it is committed and never overwritten.

| File | Written by | Contents |
|---|---|---|
| `firms_viirs_punjab_haryana_points.parquet` | Notebook 01 | Clean VIIRS detections with district, state and IST time |
| `firms_detections_by_season_state.csv` | Notebook 01 | Suomi NPP detections per season and state |
| `firms_detections_by_district_season.csv` | Notebook 01 | Detections per district and season, with 2021–2025 totals and change |
| `firms_snpp_noaa20_ratio.csv` | Notebook 01 | Suomi NPP to NOAA-20 detection ratio, 2020–2025 |
| `district_shortlist.csv` | Notebook 01 | Top three districts for Checkpoint 1 |
| `s2_burn_classes_<area>_2025.tif` | Notebook 02 | 20 m GeoTIFF, four bands: class (1 not a harvested crop, 2 harvested but not burnt, 3 burnt and flagged by VIIRS, 4 burnt and missed), burn window, harvest window, last clear view before the burn (windows numbered from 1; 0 = none). Not committed. |
| `s2_burn_summary_<area>_2025.csv` | Notebook 02 | Headline numbers: harvested and burnt area, missed shares under three matching rules, FIRMS products used, credits |
| `s2_burn_by_window_<area>_2025.csv` | Notebook 02 | Per 5-day window: share of the area seen clearly, hectares harvested and burnt, detections |
| `s2_burn_grid_1km_<area>_2025.geojson` | Notebook 02 | 1 km squares for the dashboard: harvested, burnt and missed hectares, mean harvest and burn timing |
| `firms_detections_<area>_2025.csv` | Notebook 02 | VIIRS and MODIS detections used for matching, with their 5-day window |
| `s2_scl_check_pilot_2025.csv` | Notebook 02 | Scene class of burnt-looking pixels on single dates in the pilot box |
| `validation_points_sangrur_2025.csv` | Notebook 02 | The 240 validation points with their sampling class and half (A or B). Not for labelling: it shows the map's class. |
| `validation_labels_sangrur_2025.csv` | Notebook 02, then by hand | Blind label sheet: burnt yes / no / unsure for each point |
| `validation_accuracy_sangrur_2025.csv`, `validation_area_estimate_sangrur_2025.csv`, `burn_rule_calibration_grid_sangrur_2025.csv` | Notebook 02 | Calibration and accuracy, once at least 100 points are labelled |

`<area>` is `pilot` (a 10 km box) or `sangrur` (the whole district, pre-2021 boundary).
