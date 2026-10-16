# Methodology

This is a living document: each section is filled in as its notebook is finished. Planned methods are marked *planned*.

## 1. Question and scope
See `problem_statement.md`. Study area: one Punjab district, chosen at Checkpoint 1 (20 Oct 2026). Main season: 15 Sep–30 Nov 2025. The 2021 rerun is the before-shift comparison. The 2026 season serves as a live demo.

## 2. Data
All datasets, access dates, licences and preprocessing are in `sources/source_register.csv`.

## 3. Fire detections (Notebook 01)
- **Source:** VIIRS 375 m active fire detections from the NASA FIRMS area API, one request per block of up to 10 days.
- **Trends:** Suomi NPP standard processing (`VIIRS_SNPP_SP`), 2012–2025, so seasons compare like for like.
- **Sensor overlap:** NOAA-20 standard processing, 2020–2025.
- **2026 season:** near-real-time data from Suomi NPP (until 1 Nov 2026), NOAA-20 and NOAA-21.
- **Cleaning:**
  - Drop exact duplicates.
  - Keep the "presumed vegetation fire" type where the field exists.
  - Convert UTC to IST.
  - Skip rows with an unreadable date or time.
  - Keep only points inside Punjab and Haryana districts. Districts get their state from their representative point.
- **Outputs:** detections by season, state and district; time of detection; season shape; the Suomi NPP to NOAA-20 ratio; the district shortlist.

## 4. Burnt-area mapping (Notebook 02, *planned*)
- **Imagery:** Sentinel-2 L2A through openEO on the Copernicus Data Space Ecosystem, at 20 m.
- **Clear pixels:** the scene classification layer removes cloud, shadow and snow.
- **Cropland only:** the mask is ESA WorldCover 2021's cropland class.
- **Indices, per clear date:**
  - NBR = (B8A − B12) / (B8A + B12)
  - MIRBI = 10 × B12 − 9.8 × B11 + 2 (reflectance 0–1)
  - NDVI = (B8 − B4) / (B8 + B4)
- **Rule:** a pixel is burnt when its indices change sharply between consecutive clear dates. The first such date is recorded. Thresholds are set at Checkpoint 3 from the reference labels.

## 5. Validation (*planned*)
- About 300 reference points are labelled burnt or unburnt by interpreting Sentinel-2 imagery in QGIS.
- Training and test areas are kept geographically apart.
- Reported measures: confusion matrix, precision, recall and F1.

## 6. Missed share (*planned*)
- **Definition:** burnt area with no VIIRS detection nearby, divided by total burnt area.
- **Why "nearby" needs care:** a detection marks the centre of a 375 m pixel, and the real footprint grows away from the satellite track.
- **Sensitivity check:** the result is reported for more than one search distance, so the conclusion does not hinge on a single choice.

## 7. ML burn classifier (Notebook 03, *planned*)
- **Model:** Random Forest on Sentinel-2 bands, indices and index changes.
- **Training data:** the Week 2 labels.
- **Comparison:** scored against the rule on the same held-out points.

## 8. Fire-activity forecast (Notebook 04, *planned*)
- **Target:** weekly Suomi NPP detections.
- **Models:** a seasonal-naive baseline against SARIMA on log counts.
- **Backtests:** the 2024 and 2025 seasons.
- **2026 comparison:** the forecast is compared with NOAA-20 actuals after 1 Nov, using the ratio from Notebook 01.
- **Caveat:** this forecasts detections, not burnt area.

## 9. Limitations
See the README's running list. Every output states its own limits.

## 10. Reproducibility
- Run the notebooks in order: 01, 02, 03, 04.
- Downloads are cached in `data/raw/`.
- Pin package versions (`pip freeze`) before the final submission.
