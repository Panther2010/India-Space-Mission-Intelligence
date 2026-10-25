# Methodology

This is a living document: each section is filled in as its notebook is finished. Planned methods are marked *planned*.

## 1. Question and scope
See `problem_statement.md`. Study area: Sangrur district, Punjab, on its pre-2021 boundary, which includes Malerkotla (decision log, 22 Oct 2026). Main season: 15 Sep–30 Nov 2025. The 2021 rerun is the before-shift comparison. The 2026 season serves as a live demo.

## 2. Data
All datasets, access dates, licences and preprocessing are in `sources/source_register.csv`.

## 3. Fire detections (Notebook 01)
- **Source:** VIIRS 375 m active fire detections from the NASA FIRMS area API, one request per block of up to 5 days (the live API's limit).
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

## 4. Burnt-area mapping (Notebook 02; built, first run pending)
- **Imagery:** Sentinel-2 L2A bands B04, B08, B11 and B12, through openEO on the Copernicus Data Space Ecosystem. They are resampled to 20 m in UTM zone 43N by nearest neighbour.
- **Clear pixels:** the scene classification (SCL) keeps classes 2, 4, 5, 6 and 7 (dark area, vegetation, bare soil, water, unclassified). It masks cloud, cirrus, cloud shadow, snow, saturated and no-data pixels. Scenes over 80% cloud are skipped. A pilot job checks which classes burnt-looking pixels fall in, in case burn scars are being masked as shadow.
- **Composites:** median of the clear observations in each 5-day window, 5 Sep–4 Dec 2025 (18 windows). They are computed on Copernicus's servers and downloaded as 16-bit integers.
- **Scaling:** values are reflectance × 10,000. Whether the +1,000 offset of processing baseline 04.00 is present is detected from the pilot's red band.
- **Indices, per window:**
  - NDVI = (B08 − B04) / (B08 + B04)
  - NBR = (B08 − B12) / (B08 + B12)
  - MIRBI = 10 × B12 − 9.8 × B11 + 2 (reflectance 0–1)
- **Rule, per pixel, in window order:**
  - **Green:** NDVI has reached 0.6 in an earlier window.
  - **Harvested:** after that, NDVI falls below 0.35.
  - **Burnt:** in a harvested window, NBR ≤ −0.05 and MIRBI ≥ 1.65.
  - The harvest window, the burn window and the last clear view before the burn are recorded. The thresholds are provisional until Checkpoint 3.
- **No land-cover mask:** the green-then-harvested sequence already restricts the analysis to fields harvested during the season. Trees, towns, water and crops still standing in December never meet it.
- **Cost control:** a 10 km pilot runs first. The whole district runs only if the pilot's cost, scaled up by area, fits the credit budget and the projected download fits on disk.

## 5. Validation (Notebook 02; labels due by Checkpoint 3)
- **Sample:** 240 points drawn at random by mapped class: 100 burnt, 100 harvested but not burnt, and 40 from the rest of the district, to catch burns the rule missed entirely. Each point is the centre of a 3 × 3 block of one class.
- **Labels:** burnt, not burnt or unsure, judged blind from image strips of all 18 windows in false colour (SWIR 2, NIR, red), 1.5 km across.
- **Calibration:** half the points choose the NBR and MIRBI thresholds (best F1). The other half check them.
- **Measures:** precision, recall and F1 on the check half. Area-weighted user's, producer's and overall accuracy use the stratified estimator of Stehman (2014), which allows the scored map to differ from the sampled one. The burnt area is also estimated from the labels alone, with a 95% confidence interval, following Olofsson et al. (2014).
- **Limits:** labels come from interpreting 20 m imagery, not field visits. Points avoid field edges, so edge accuracy isn't measured.

## 6. Missed share (Notebook 02)
- **Definition:** burnt area with no fire detection nearby, divided by total burnt area.
- **Detections:** VIIRS from Suomi NPP, NOAA-20 and NOAA-21, plus MODIS, for the district plus 0.05°. Standard processing is used where FIRMS has it, near real time elsewhere, with duplicates and non-vegetation fire types removed.
- **When:** a detection counts if it falls between the pixel's last clear view before the burn and the window in which the burn shows.
- **Where, three rules:**
  - VIIRS within 375 m (strict)
  - VIIRS within 750 m (lenient)
  - VIIRS within 750 m or MODIS within 1 km (any satellite)
- **Why "nearby" needs care:** a detection marks the centre of a 375 m pixel, and the real footprint grows away from the satellite track. The generous rules make the missed share conservative.

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

## References
- Olofsson, P., Foody, G. M., Herold, M., Stehman, S. V., Woodcock, C. E. and Wulder, M. A. (2014). Good practices for estimating area and assessing accuracy of land change. *Remote Sensing of Environment* 148, 42–57. https://doi.org/10.1016/j.rse.2014.02.015
- Stehman, S. V. (2014). Estimating area and map accuracy for stratified random sampling when the strata are different from the map classes. *International Journal of Remote Sensing* 35, 4923–4939. https://doi.org/10.1080/01431161.2014.930207

## 10. Reproducibility
- Run the notebooks in order: 01, 02, 03, 04.
- Downloads are cached in `data/raw/`.
- Pin package versions (`pip freeze`) before the final submission.
