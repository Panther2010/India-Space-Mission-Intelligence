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
- **2026 season:** near-real-time data from Suomi NPP (until 13:00 UTC on 2 Nov 2026), NOAA-20 and NOAA-21.
- **Cleaning:**
  - Drop exact duplicates.
  - Keep the "presumed vegetation fire" type where the field exists.
  - Convert UTC to IST.
  - Skip rows with an unreadable date or time.
  - Keep only points inside Punjab and Haryana districts. Districts get their state from their representative point.
- **Outputs:** detections by season, state and district; time of detection; season shape; the Suomi NPP to NOAA-20 ratio; the district shortlist.

## 4. Burnt-area mapping (Notebook 02; whole district run 26 Oct 2026)
- **Imagery:** Sentinel-2 L2A bands B04, B08, B11 and B12, through openEO on the Copernicus Data Space Ecosystem. They are resampled to 20 m in UTM zone 43N by nearest neighbour.
- **Clear pixels:** the scene classification (SCL) keeps classes 2, 4, 5, 6 and 7 (dark area, vegetation, bare soil, water, unclassified). It masks cloud, cirrus, cloud shadow, snow, saturated and no-data pixels. Scenes over 80% cloud are skipped. A pilot job checks which classes burnt-looking pixels fall in, in case burn scars are being masked as shadow. In the pilot, 98.8% fell in class 5 (bare soil) and about 0.1% in masked classes, so there the mask isn't hiding burn scars.
- **Composites:** median of the clear observations in each 5-day window, 5 Sep–4 Dec 2025 (18 windows). They are computed on Copernicus's servers and downloaded as 16-bit integers.
- **Scaling:** values are reflectance × 10,000. Whether the +1,000 offset of processing baseline 04.00 is present is detected from the pilot's red band. The pilot found none: the red band's 2nd percentile is 186, too low to carry the offset.
- **Indices, per window:**
  - NDVI = (B08 − B04) / (B08 + B04)
  - NBR = (B08 − B12) / (B08 + B12)
  - MIRBI = 10 × B12 − 9.8 × B11 + 2 (reflectance 0–1)
- **Rule, per pixel, in window order:**
  - **Green:** NDVI has reached 0.6 in an earlier window.
  - **Harvested:** after that, NDVI falls below 0.35.
  - **Burnt:** in a harvested window, NBR ≤ −0.05, MIRBI ≥ 1.65 and NIR (B08) reflectance ≤ 0.13.
  - The harvest window, the burn window and the last clear view before the burn are recorded. The thresholds were checked against the validation labels at Checkpoint 3 (30 Oct 2026) and kept (section 5).
- **Why NIR:** the NIR condition was added after the pilot (decision log, 26 Oct 2026). Bare soil after harvest passes the NBR and MIRBI tests too, but it is brighter in NIR than fresh char. Without the condition the pilot marked 91% of harvested land burnt; with it, 25%.
- **Unconfirmed late burns:** burns first seen in a window from 19 Nov are mapped as a class of their own and kept out of the headline figures (decision log, 30 Oct 2026). Damp soil under a young crop can pass all three burn tests: one field labelled `no` (P016) does so on 22 and 24 Nov. In 2025 these late burns cover about 8,200 ha, against 63,400 ha of confirmed burns.
- **No land-cover mask:** the green-then-harvested sequence already restricts the analysis to fields harvested during the season. Trees, towns, water and crops still standing in December never meet it.
- **Cost control:** a 10 km pilot runs first. The whole district runs only if the pilot's cost, scaled up by area, fits the credit budget and the projected download fits on disk. The pilot cost 4 credits for the composites and 4 for the cloud-mask check. It projected about 135 credits and a 1.8 GB download for the whole district; the district job then used 8 credits, took 11 minutes and downloaded about 1 GB.

## 5. Validation (Notebook 02; 240 points labelled and the rule checked, 30 Oct 2026; 3 relabelled from Landsat, 31 Oct)
- **Sample:** 240 points drawn at random by mapped class: 100 burnt, 100 harvested but not burnt, and 40 from the rest of the district, to catch burns the rule missed entirely. Each point is the centre of a 3 × 3 block of one class.
- **Labels:** `yes` (burnt), `no` or `unsure`, judged blind from image strips:
  - **Main evidence:** single Sentinel-2 dates from 20 Sep to 4 Dec 2025 at 10 m, 640 m across, in true colour and in false colour (SWIR 2, NIR, red). Only dates on which the scene classification shows the point's 60 m block clear are included. A separate small openEO job fetches them, one file per point.
  - **Context:** the 18 five-day composites in false colour, 1.5 km across.
  - **Rules:** on the first clear date after the straw goes, the field is compared with the tilled fields around it on that date.
    - `yes`: black or near-black up to the field's edges, covering most of the square, centre included.
    - `no`: the same colour as the tilled fields. Damp soil (navy or blue-grey in false colour) and new crops are also `no`.
    - `unsure` carries a reason in the notes: `dull` (darker than the tilled fields but not black), `gap` (no clear view for a week or more while the straw went), `edge` (a burn edge through the centre of the square) or `hazy` (dark only on a hazy date).
  - **Second reading:** every point was also read independently by Claude, an AI assistant, from the same strips and the underlying reflectance values. Disagreements were discussed and resolved, and points that stayed in doubt became `unsure`. Agreement between the first pass and the second reading rose from about three-quarters in the first batches to 90% in the last 40 points.
- **Landsat views (Notebook 02b, 31 Oct 2026):** the 56 `unsure` points got extra views from Landsat 8 and 9 (NASA HLS, 30 m), and each `gap` point a timeline of its Sentinel-2 and Landsat views in date order. Landsat passes on its own schedule; its pass on 27 Oct was almost cloud-free and fell inside the gap at all 26 `gap` points.
  - **Rules:** a point becomes `yes` if its field is black on a clear Landsat date. It becomes `no` only if the views together leave no more than 3 days between the last straw view and the first view of plain, dry soil, and none looks burnt. Damp soil right after the straw doesn't count, because a burn followed by watering can look the same. Relabelled points carry the Landsat date in their notes.
  - **Order of reading:** for these 26 points it was reversed. Claude read first, from the timelines and the reflectance values, and the author checked each call against the images.
  - **Result:** 1 `yes` (P218) and 2 `no` (P095, P119). The other 23 `gap` points stay `unsure`: at 16 of them the straw was still there on 27 Oct and gone by 2 Nov, with no clear view in between from either satellite; the rest were damp, at a field edge, beside a canal or only just harvested. The 30 other `unsure` points (`dull`, `edge`, `hazy` and similar) were not relabelled, because their doubt is what a darkening is or where a burn edge falls, which 30 m pixels can't settle.
- **Checking the rule:** half the points (A) fit NBR, MIRBI and NIR thresholds (best F1). The other half (B) checks them against the thresholds already in use. `unsure` points are left out. Thresholds fitted on half A are judged on half B only; thresholds that no label helped choose are also scored on all labelled points.
- **Measures:** precision, recall and F1. Area-weighted user's, producer's and overall accuracy use the stratified estimator of Stehman (2014), which allows the scored map to differ from the sampled one. The burnt area is also estimated from the labels alone, with a 95% confidence interval, following Olofsson et al. (2014).
- **Unsure points, both ways:** leaving them out can flatter the accuracy, because the hard cases go. So the accuracy of the map as reported and the label-based burnt area are repeated with every `unsure` counted as not burnt, then as burnt.
- **Late-window check:** the window in which the rule first calls each labelled point burnt is set against its label. The map has about 8,200 ha of burns in the windows from 19 Nov but only 24 VIIRS detections there. In the label strips, one field labelled `no` (P016) shows damp soil on 14 Nov and a young crop from 22 Nov, most likely wheat. Its single-date values pass all three burn tests on 22 and 24 Nov, so damp soil under a young crop may be passing as burns. Result: none of the 5 labelled points the rule first calls burnt from 19 Nov is a confirmed burn (1 `no`, 4 `unsure`), so those burns are now unconfirmed (section 4).
- **Results (31 Oct 2026, after the Landsat relabels; 69 `yes`, 118 `no`, 53 `unsure`):**
  - Thresholds fitted on half A (NBR ≤ −0.10, MIRBI ≥ 1.30, NIR ≤ 0.12) scored F1 0.82 on half B, against 0.90 for the thresholds in use, which were kept (0.83 against 0.90 on 30 Oct).
  - The map as reported, on all 187 `yes` and `no` points: precision 0.87, recall 0.97, F1 0.92. Area-weighted accuracy for burnt: user's 0.87, producer's 0.90; overall accuracy 0.96 (standard error 0.015). On half B alone: F1 0.91, overall accuracy 0.94 (0.03).
  - With every `unsure` point counted as not burnt, then as burnt: F1 0.82 and 0.78; overall accuracy 0.93 and 0.76.
  - Burnt area from the labels alone: 68,300 ha (95% CI 57,400–79,200 ha). The map's 63,400 ha of confirmed burns lies inside that interval. Counting every `unsure` point as not burnt gives 52,700 ha, and as burnt 141,200 ha. The upper end comes from the 31 `unsure` points in fields mapped as harvested but not burnt, each standing for about 2,300 ha; 16 of them are `gap` cases.
- **Limits:**
  - Labels come from interpreting satellite imagery, not field visits. The second reader is an AI assistant, not an independent field expert.
  - Labels come mainly from single dates at 10 m, not from the 5-day composites the rule reads, so they don't simply repeat the rule.
  - Burn scars fade fast. In the strips, a black field looked like tilled soil again within two to three days. A burn between two clear views can be invisible to both the labels and the map, so `no` means "no burn visible".
  - Damp soil after irrigation and missed cloud shadows can look dark, like a burn. The labelling guide in Notebook 02 says how to tell them apart.
  - Small and partial burns may never pass the rule. These include burns covering only a small part of a 20 m pixel, such as straw burnt in small heaps, and burns of the loose straw only, with the stubble left standing. A farmer in Maharashtra described the small-heap practice to us; how common it is in Sangrur is unknown. Loose-straw burning followed by a super seeder was reported from Sangrur and Patiala in 2022 (Rajpurohit 2022). VIIRS can detect small fires (Schroeder et al. 2014), but only those burning at an overpass, so brief fires are rarely caught either. Burnt area is therefore a field-scale lower bound, and it isn't the same as the amount of straw burnt.
  - Points come from pure 3 × 3 blocks of one map class, yet some still sit on a field or burn edge. Those are `unsure` (`edge`), so edge accuracy isn't measured.

## 6. Missed share (Notebook 02)
- **Definition:** confirmed burnt area with no fire detection nearby, divided by confirmed burnt area. Unconfirmed late burns (section 4) are left out, and the strict share with them included is reported too. In 2025 the strict share is 90.6% (91.6% with the unconfirmed burns).
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
- **2026 comparison:** the forecast is compared with NOAA-20 actuals after Suomi NPP stops on 2 Nov, using the ratio from Notebook 01.
- **Caveat:** this forecasts detections, not burnt area.

## 9. Limitations
See the README's running list. Every output states its own limits.

## References
- Olofsson, P., Foody, G. M., Herold, M., Stehman, S. V., Woodcock, C. E. and Wulder, M. A. (2014). Good practices for estimating area and assessing accuracy of land change. *Remote Sensing of Environment* 148, 42–57. https://doi.org/10.1016/j.rse.2014.02.015
- Rajpurohit, S. (2022). Punjab's farmers are burning less stubble. Thanks to super seeders. *Newslaundry*, 14 November 2022. https://www.newslaundry.com/2022/11/14/punjabs-farmers-are-only-partially-burning-stubble-thanks-to-super-seeders
- Schroeder, W., Oliva, P., Giglio, L. and Csiszar, I. A. (2014). The new VIIRS 375 m active fire detection data product: algorithm description and initial assessment. *Remote Sensing of Environment* 143, 85–96. https://doi.org/10.1016/j.rse.2013.12.008
- Stehman, S. V. (2014). Estimating area and map accuracy for stratified random sampling when the strata are different from the map classes. *International Journal of Remote Sensing* 35, 4923–4939. https://doi.org/10.1080/01431161.2014.930207

## 10. Reproducibility
- Run the notebooks in order: 01, 02, 03, 04.
- Downloads are cached in `data/raw/`.
- Pin package versions (`pip freeze`) before the final submission.
