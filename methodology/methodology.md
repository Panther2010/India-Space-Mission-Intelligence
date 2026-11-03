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
- **Other seasons:** setting `SEASON_YEAR` maps another season with the same rule, thresholds, district outline and 5-day windows, starting on the same calendar days. The pilot and cloud-mask check run again, because the scaling of the values can differ between years. That season's downloads, outputs and charts are kept apart from 2025's (`…_sangrur_2021…` files, `maps/notebook02/2021/`). Validation (section 5) is for 2025 only, so another season's map applies the rule without labels of its own. NOAA-21 is skipped before the 2023 season, because it launched in November 2022.

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
- **2021 against 2025 (Notebook 02c; run 1 Nov 2026):**
  - **Question:** Suomi NPP detections in Sangrur fell 95% from 2021 to 2025, from 9,076 to 482 (Notebook 01). Did the burnt area fall as much, or do fire counts now miss more of the burning?
  - **The same satellites:** Notebook 02's missed share uses every VIIRS satellite flying that season: three in 2025, two in 2021. A higher share in 2021 would then partly reflect the missing satellite. So Notebook 02c recomputes the strict share (375 m) for both seasons from Suomi NPP and NOAA-20 only. It first reproduces Notebook 02's 2025 figure from the saved files. In 2025 the strict share is 90.6% with all three satellites and 93.7% with the two.
  - **Also compared:** harvested and burnt area, the burnt share of the harvest (overall, and on the land harvested in both seasons), days from harvest to burn, clear views, detections per 1,000 ha burnt, burning by 5-day window, and 1 km maps of the change in burnt area, with a south-to-north summary.
  - **How often Sentinel-2 looked:** more looks catch more burns before fields are ploughed. Sentinel-2C took over from Sentinel-2A on 21 January 2025 ([Copernicus](https://dataspace.copernicus.eu/node/2039)), and Sentinel-2A stayed on in an extended campaign from 13 March 2025 ([Copernicus](https://dataspace.copernicus.eu/news/2025-2-28-sentinel-2a-extended-campaign-starting-march-13-2025)), so 2025 may have had more looks than 2021. Notebook 02c counts the dates with Sentinel-2 data over the pilot box from 15 Oct to 24 Nov in each season, from Notebook 02's cloud-mask check downloads. More looks in 2025 would make its burnt area look larger against 2021's, so they would understate the fall in burning.
  - **Results:**
    - **Harvest about the same:** 315,700 ha harvested in 2021 and 306,500 ha in 2025 (−3%).
    - **Burning about halved:** confirmed burnt area fell 47%, from 119,800 ha to 63,400 ha; counting the late, unconfirmed burns, 49% (139,500 to 71,600 ha). On the 297,700 ha harvested in both seasons, 39.6% burnt in 2021 and 21.1% in 2025.
    - **Fire counts fell 95%:** Suomi NPP detections inside the district fell from 9,078 to 483 over 5 Sep–4 Dec (Notebook 01 counts 9,076 and 482 over 15 Sep–30 Nov). Detections per 1,000 ha burnt fell from 76 to 8.
    - **Fire counts now miss most of the burning:** on Suomi NPP and NOAA-20 alone, the share of confirmed burnt area with no detection within 375 m rose from 27% to 94%. Notebook 02, with every VIIRS satellite flying, reports 27% and 91%.
    - **Same land:** 56% of the area burnt in 2025 had burnt in 2021 too; 30% of the area burnt in 2021 burnt again in 2025.
    - **Timing:** the 2021 season ran about one 5-day window later. Half the harvest was first seen by the window starting 30 Oct (25 Oct in 2025), and half the burnt area by 9 Nov (4 Nov).
    - **Where:** burning fell in 86% of the 1 km squares, or 93% counting the late burns. It fell least in the southern quarter of the district: −39% counting the late burns, and only −23% for confirmed burns, since 27% of the south's 2021 burning was first seen from 19 Nov and so counts as unconfirmed. It fell most in the northern quarter (−56% counting the late burns, −61% confirmed).
    - **Seen about as well:** Sentinel-2 had 15 dates over the pilot box from 15 Oct to 24 Nov in 2021 and 17 in 2025. The 2021 windows from 25 Oct were clear (clear share 0.95–1.0); its lower mean clear share (0.87 against 0.95) comes from September, before the harvest.
    - **Checks:** the areas recomputed from the two maps, and the missed shares recomputed with exact distances, match the notebook's figures. The 2021 scaling and cloud-mask check match 2025's: no offset, and 98% of burnt-looking pixels in the 2021 pilot box (99% in 2025) are classed as bare soil and kept. The 2021 map has no labels, but 73% of its confirmed burnt area had a VIIRS detection within 375 m at the right time.
    - **What it means:** fire counts overstate the fall in burning by a wide margin. Burning fell by about half, detections by 95%, so in 2025 Sangrur's fire count said little about how much of it burned. These data can't say why detections fell further: later burning, smaller or shorter fires and partial burns are all possible.
  - **Limits:**
    - The 2021 map has no labels of its own, so its accuracy is unknown. Smoke, cloud and soil moisture can differ between seasons and change how well the rule works.
    - NOAA-20 shifted in its orbit in April 2024 ([CIRA, May 2024](https://rammb2.cira.colostate.edu/visit-blog/2024/05/03/noaa-21-designated-as-the-primary-satellite-of-the-jpss-constellation)), so the spacing between the two satellites' passes was not the same in both seasons.
    - Fires that start and burn out between overpasses are missed in both seasons. A move to later burning would show here as a higher missed share, without saying why.

## 7. ML burn classifier (Notebook 03; run 31 Oct 2026)
- **Question:** does a classifier trained on the validation labels map burnt fields better than the three-threshold rule? Walker et al. (2022) trained a Random Forest on PlanetScope and Sentinel-2 data against ground records of burning in Punjab and reached 82% overall accuracy. Here the question is narrower: does a forest add anything to a rule that already scores well against the same image-interpreted labels? Checkpoint 3 also left an NDVI ceiling on the burn test untried; the forest sees NDVI at and after the darkest view, so it can learn one if it helps.
- **Features:** 23 numbers per harvested pixel from the 18 five-day composites, with the rule's own harvest test (green to NDVI 0.6, then below 0.35):
  - the crop before harvest: green-peak NDVI, NBR just before harvest
  - how dark the field turned after harvest: the lowest NBR, NIR, red and SWIR 2 and highest MIRBI, the NBR drop, and every band and index of the darkest view (lowest NIR)
  - timing: harvest date, date of the darkest view, days between them
  - after the darkest view: NDVI and the rise in NIR at the next view, highest NDVI after harvest, the season's last NDVI
  - the number of clear views after harvest

  Pixels never harvested get no features, and both methods call them not burnt. The notebook's harvest test matches Notebook 02's at every pixel of the district.
- **Model:** a Random Forest (Breiman 2001) of 500 trees, at least 2 training points per leaf, classes weighted to balance, a burn called at a probability of 0.5, and a fixed seed. It learns from the 147 labelled, harvested points (69 burnt); `unsure` points are left out. Two variants tried while the notebook was being built did no better and were dropped: a probability threshold tuned within cross-validation, and the 19 Nov cut-off applied to the date of the forest's darkest view.
- **Scoring:** as for the rule in section 5. Half A trains and half B tests; then 5-fold cross-validation on all labelled points, repeated 10 times with different splits, so every point is predicted by forests that never saw it. Both methods get precision, recall, F1 and the area-weighted accuracy of Stehman (2014), and an exact McNemar test (McNemar 1947) asks whether the points only one method gets right split unevenly. The rule's thresholds were set before any label existed, so it is scored on all labelled points as it stands; the map as reported adds one choice made after looking at the labels, the 19 Nov cut-off.
- **Results (31 Oct 2026):**
  - Half B: the forest scored F1 0.86 (overall accuracy 0.92), against 0.91 (0.94) for the map as reported. The rule alone was right on 5 points, the forest alone on 2 (McNemar p = 0.45).
  - All 187 labelled points, cross-validated: forest F1 0.92 (0.88–0.94 across the 10 runs) and overall accuracy 0.95 (0.94–0.96), against F1 0.92 and 0.96 for the map as reported and 0.91 and 0.95 for every burn. McNemar p ranged from 0.39 to 1.00 across runs. The two tie.
  - More labels of the same kind are unlikely to change this: on the same held-out points, the forest's F1 levels off at about 0.92 from 40 training points, level with the rule's.
  - What the forest relies on: how dark the field turned after harvest, the signal the rule tests. Shuffling that group of features cuts its F1 on held-out points by 0.45; shuffling any other group changes it by less than 0.01. Shuffling NDVI at the darkest view alone, or the whole group of what followed it, cuts F1 by only 0.005 and 0.003, so an NDVI ceiling on the rule looks unlikely to help. At the darkest view, the rule's NIR limit alone is right on 133 of the 147 labelled, harvested points, against 92 for its NBR limit alone and 74 for its MIRBI limit alone.
  - On the 53 `unsure` points, the rule (every burn) calls 22 burnt and the forest 18; they agree on 45. These calls are not labels.
  - Across the district, the forest maps 55,700 ha burnt, against 71,600 ha for the rule's every burn (63,400 ha as reported) and 68,300 ha (95% CI 57,400–79,200 ha) from the labels alone. 49,100 ha are burnt in both maps, 22,500 ha in the rule's only and 6,500 ha in the forest's only.
  - Of the pixels burnt in the rule's map only, 91% lie on the edge of a burnt patch and 38% in patches under 1 ha, against 71% and 19% of the pixels burnt in both. The forest calls 42% of the rule's unconfirmed late burns burnt.
- **Other classifiers (3 Nov 2026, for the report):** under the same cross-validation, Extra Trees, gradient boosting, a support vector machine, k-nearest neighbours, logistic regression and a single decision tree score F1 0.89–0.94, with default settings. None beats the rule beyond chance (McNemar p at least 0.15 in every run). Details in `report/ml_classifier.md`; the table comes from `report/compare_classifiers.py`.
- **Decision:** the rule's map stays (decision log, 31 Oct). The forest adds no accuracy at the labelled points, needs labels to train, and is harder to explain or to carry to another season. Its area falls below the labels' interval, although the labels too come from block centres, so they say little about edges. The agreement map (`ml_burn_agreement_sangrur_2025.tif`) is kept as a cross-check of where the two methods agree and where they differ.
- **Limits:** the labelled points are centres of uniform 3 × 3 blocks, so neither method has been checked at field edges or in small patches, which is where most of the disagreement lies. The forest learns from the same image-interpreted labels it is scored on. One season and one district.

## 8. Fire-activity forecast (Notebook 04; forecast issued 1 Nov 2026)
- **Question:** from the 2026 season so far, how many more Suomi NPP fire detections will Punjab and Sangrur (pre-2021 boundary) have by 30 Nov, and which week will be busiest? It forecasts detections, not burnt area.
- **Data:** Suomi NPP detections counted by IST week, 11 whole weeks from 15 Sep to 30 Nov. Seasons 2012–2025 come from Notebook 01's standard-processing archive. The 2026 season is downloaded in near real time when the notebook runs, and cleaned by Notebook 01's rules.
- **When:** the forecast starts after the last whole week of Suomi NPP data. Run on 1 or 2 Nov, that is week 6 (20–26 Oct); from 3 Nov, week 7 (27 Oct–2 Nov), the last week Suomi NPP covers.
- **Methods:**
  - *last season* (the seasonal-naive baseline): each remaining week as in the same week of the previous season (Hyndman and Athanasopoulos 2021).
  - *SARIMA*: a seasonal ARIMA (1,0,0)(0,1,1) model with an 11-week period, fitted to log(1 + weekly count) with the seasons laid end to end; 1,000 simulated paths.
  - *past seasons rescaled*: each season since 2012 keeps its own week-by-week shape, scaled to the 2026 detections so far relative to its own over the same weeks; the median of these 14 scenarios is the forecast.
- **Backtests:** each method forecasts every season from 2016 to 2025 from the same week, using only earlier seasons. The score is a *typical error factor* for the rest-of-season total: the geometric mean of the ratio between forecast and outcome, taken as at least 1, so 1.5 means typically 1.5 times too high or too low. The headline method has the smallest typical error over 2021–2025, the years detections fell fastest. Its errors over all ten seasons give an 80% range for the 2026 total.
- **What the backtests show** (forecasts from week 6, on Notebook 01's archive):
  - In 2024 and 2025 SARIMA and last season forecast 2 to 6 times too many detections for Punjab; past seasons rescaled was within 0.7 to 1.1 times. Three other SARIMA orders tried while building the notebook overshot as well.
  - Past seasons rescaled had a typical error factor of 1.5 for Punjab over 2016–2025. It found the busiest week in 7 of the 10 seasons, and was within a week in 9.
- **Made once:** the first run saves the forecast with its date, and later runs load it rather than forecast again. It is committed straight away, so the commit date shows it came before the outcome.
- **The check:** weeks to 2 Nov are checked against Suomi NPP. From 3 Nov, Suomi NPP has stopped, so the actual counts are NOAA-20's multiplied by the ratio of the two sensors over the 2026 weeks both covered. Early 2026 data already ran below the 2020–2025 seasons' range of 0.87–1.01 (0.83 over weeks 1–5 in Notebook 01's download), so the same-season ratio is used rather than the 2020–2025 average. The notebook flags any week in which Suomi NPP saw far fewer detections than NOAA-20, a sign of missing data. From 3 Nov 2026 the check is committed after each weekly run, so the dashboard shows the weeks checked so far; the forecast files never change (decision log, 3 Nov). The score is final after 30 Nov.
- **The forecast, issued 1 Nov 2026** from weeks 1–6 (data to 26 Oct). The headline method for both areas is past seasons rescaled. As issued, the forecast is in `data/processed/fire_forecast_2026.csv` and its summary; the git history shows when they were committed.
  - **Punjab:** 749 Suomi NPP detections to 26 Oct. About 2,700 more are forecast by 30 Nov (80% range 2,200–6,400): about 3,500 for the season, against 4,269 in 2025. The busiest week is most likely week 8 (3–9 Nov), in 10 of the 14 scenarios, with about 1,200 detections.
  - **Sangrur:** only 3 detections to 26 Oct, against 50 over the same weeks of 2025. About 44 more are forecast (range 23–65), about 47 for the season against 481 in 2025, with week 8 the most likely busiest week.
  - **A fragile number:** the Sangrur forecast rests on 3 detections, fewer than in any backtest season, so its range is probably too narrow. In the five days to 31 Oct, already in the data when the forecast was made but after its cut-off, Suomi NPP saw 18 detections in Sangrur, more than the 14 forecast for the whole of week 7. The other two methods forecast about 400–430 more. The forecast stands as issued (decision log, 1 Nov).
- **Results of the check:** after 30 Nov.
- **Limits:** detections, not burnt area, and only fires burning at an overpass. 2026 counts are near-real-time data, while the archive the methods learn from is standard processing. Ten backtests give only a rough 80% range. Sangrur's weekly counts are small, so its forecast is noisier than Punjab's.

## 9. Limitations
See the README's running list. Every output states its own limits.

## References
- Breiman, L. (2001). Random forests. *Machine Learning* 45, 5–32. https://doi.org/10.1023/A:1010933404324
- Hyndman, R. J. and Athanasopoulos, G. (2021). *Forecasting: principles and practice*, 3rd edition. OTexts. https://otexts.com/fpp3/
- McNemar, Q. (1947). Note on the sampling error of the difference between correlated proportions or percentages. *Psychometrika* 12, 153–157. https://doi.org/10.1007/BF02295996
- Olofsson, P., Foody, G. M., Herold, M., Stehman, S. V., Woodcock, C. E. and Wulder, M. A. (2014). Good practices for estimating area and assessing accuracy of land change. *Remote Sensing of Environment* 148, 42–57. https://doi.org/10.1016/j.rse.2014.02.015
- Rajpurohit, S. (2022). Punjab's farmers are burning less stubble. Thanks to super seeders. *Newslaundry*, 14 November 2022. https://www.newslaundry.com/2022/11/14/punjabs-farmers-are-only-partially-burning-stubble-thanks-to-super-seeders
- Schroeder, W., Oliva, P., Giglio, L. and Csiszar, I. A. (2014). The new VIIRS 375 m active fire detection data product: algorithm description and initial assessment. *Remote Sensing of Environment* 143, 85–96. https://doi.org/10.1016/j.rse.2013.12.008
- Stehman, S. V. (2014). Estimating area and map accuracy for stratified random sampling when the strata are different from the map classes. *International Journal of Remote Sensing* 35, 4923–4939. https://doi.org/10.1080/01431161.2014.930207
- Walker, K., Moscona, B., Jack, K., Jayachandran, S., Kala, N., Pande, R., Xue, J. and Burke, M. (2022). Detecting crop burning in India using satellite data. arXiv:2209.10148 (preprint). https://arxiv.org/abs/2209.10148

## 10. Reproducibility
- Run the notebooks in order: 01, 02, 03, 04. For the 2021 comparison, run 02 again with `SEASON_YEAR = 2021`, then 02c.
- Downloads are cached in `data/raw/`.
- Pin package versions (`pip freeze`) before the final submission.
