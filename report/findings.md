# Findings

**Question.** How much paddy residue burned in Sangrur, how much of it did the fire counts miss, when did it burn, how has that changed since 2021, and how is the 2026 forecast doing?

This draft is for Section 6 (Findings) of the report. Section 5 (Method) and `methodology/methodology.md` explain how each number was made. `report/findings_numbers.py` prints every number used here from the committed files.

**Labels**, as in the other drafts:
- **[Reported]** comes from a cited source.
- **[Ours]** was measured in this project, for Sangrur district on its pre-2021 boundary.
- **[Recommendation]** is our judgement.

## 1. How much burned in 2025

- **About a fifth of the harvest burned.** Sentinel-2 mapped 63,400 ha burnt out of 306,500 ha harvested in the season: 20.7% [Ours].
- **Late burns are kept out.** Another 8,200 ha first looked burnt from 19 Nov. They are kept out of the headline as unconfirmed, because damp soil under a young crop can pass the same tests [Ours].
- **The map holds up at the labelled points.**
  - At the 187 points labelled burnt or not burnt from single-date images: precision 0.87, recall 0.97, F1 0.92 [Ours].
  - Area-weighted overall accuracy is 0.96 (standard error 0.015) [Ours].
  - From the labels alone, the burnt area is 68,300 ha (95% confidence interval 57,400–79,200 ha). The map's 63,400 ha lies inside it [Ours].
- **The doubtful points are the largest uncertainty.**
  - 53 of the 240 points stayed `unsure`. Counting them all as not burnt gives F1 0.82, and as burnt 0.78 [Ours].
  - The burnt area from the labels then runs from 52,700 to 141,200 ha [Ours].
  - The high end comes from 31 `unsure` points in fields mapped as harvested but not burnt, each standing for about 2,300 ha (methodology, section 5) [Ours].
- **Machine learning adds nothing here.**
  - A Random Forest trained on the labels tied with the rule (F1 0.92), and six other classifiers scored 0.89–0.94. None beat the rule beyond chance, so the map stays rule-based (`ml_classifier.md`) [Ours].

Figure: `maps/qgis/01_burnt_area_2025.png`, every 20 m pixel.

## 2. What the fire counts missed

- **Nine-tenths of the burnt area had no fire detection nearby.**
  - For 90.6% of the confirmed burnt area, no VIIRS detection fell within 375 m between the field's last clear view and the burn [Ours].
  - Looser rules still leave most of it unseen: 73.8% with VIIRS within 750 m, and 60.4% with VIIRS within 750 m or MODIS within 1 km [Ours].
- **The counts missed most of the peak too.** 1,143 of the season's 1,500 VIIRS detections came in the three windows with the most burning, from 30 Oct to 13 Nov. They flagged only 12%, 11% and 7% of the burnt area first seen in each [Ours].
- **The satellites pass in the early afternoon and at night.**
  - Every daytime VIIRS detection in the district in 2025 was made between 12:28 and 14:39 IST. Only 20 of the 1,500 (1.3%) came at night [Ours]. MODIS detections fell between 14:24 and 15:50 IST [Ours].
  - iFOREST reports that most large Punjab farm fires in 2024 and 2025 occurred after 3 pm [Reported].
  - The two VIIRS satellites left after Suomi NPP pass about 25 minutes before and after it, so none looks later in the afternoon [Reported].
- **What fits the gap.** A fire lit after the afternoon passes and burnt out before the night pass is never counted. That fits the large missed share, but these data have no burn times, so they can't show when fields burned [Recommendation].

Figures: `maps/qgis/02_missed_by_viirs_1km.png` (where the burnt area had no detection nearby) and `maps/notebook02/06_missed_share.png` (by 5-day window).

## 3. Timing: the straw buyer's window

- **Harvest peaked in late October.** Half the season's harvest was first seen by the 5-day window starting 25 Oct [Ours].
- **Burning followed about ten days later.**
  - Fields that burned did so a median of 10 days after harvest, in both 2021 and 2025 [Ours].
  - Half the burnt area was first seen by the window starting 4 Nov. That was the busiest window (24,000 ha, 38% of the season) [Ours].
  - 85% of the burnt area was first seen in the three windows from 30 Oct to 13 Nov [Ours].
- **Detections peaked one window earlier,** in the window starting 30 Oct (619 detections) [Ours]. A burn shows in a 5-day median composite only once most of that window's clear views come after it. A fire late in one window is therefore counted in the next, so the two peaks need not match [Ours].
- **Sentinel-2 saw almost everything.** From 15 Oct, it saw at least 99.9% of the district clearly in every 5-day window but one: 25–29 Oct, when 71% was clear [Ours].
- **What it means for the buyer.** Straw typically lies about 10 days between harvest and burning, and most burning falls in about two weeks. A map refreshed every 5 days catches that window, but with little to spare [Recommendation].

Figure: `maps/qgis/03_burn_timing.png`.

## 4. 2021 against 2025: fire counts overstate the fall

- **The harvest was about the same; burning halved.**
  - Harvested area: 315,700 ha in 2021 and 306,500 ha in 2025 (−3%) [Ours].
  - Confirmed burnt area fell 47%, from 119,800 to 63,400 ha, or 49% counting the late burns [Ours].
  - On the land harvested in both seasons, the burnt share fell from 39.6% to 21.1% [Ours].
- **Fire counts fell much further.**
  - Suomi NPP detections inside the district fell 95%, from 9,078 to 483 [Ours].
  - Per 1,000 ha burnt, they fell from 76 to 8 [Ours].
  - Across Punjab, Suomi NPP detections fell by the same proportion, from 78,678 to 4,271 (−95%) [Ours].
- **So the counts now miss most of the burning.** Counting only the two satellites flying in both seasons (Suomi NPP and NOAA-20), the missed share rose from 27% to 94% [Ours].
- **Much of the same land keeps burning.** On land harvested in both seasons, 56% of the area burnt in 2025 had also burnt in 2021 [Ours].
- **Where burning fell.**
  - Burning fell in 86% of the district's 1 km squares, or 93% counting the late burns [Ours].
  - It fell least in the southern quarter: −23% for confirmed burns and −39% counting late burns. That gap is because 27% of the south's 2021 burning was first seen from 19 Nov [Ours].
  - It fell most in the northern quarter: −61% and −56% [Ours].
- **Not an artefact of fewer looks.**
  - Sentinel-2 had 15 dates over the pilot box from 15 Oct to 24 Nov in 2021 and 17 in 2025, and the 2021 windows from 25 Oct were clear [Ours].
  - More looks in 2025 would, if anything, raise its burnt area against 2021's, so the fall in burning is not overstated [Recommendation].
- **Why the counts fell further is open.** Later burning, smaller or shorter fires and partial burns all fit. These data can't tell them apart [Recommendation].

Figures: `maps/notebook02c/01_change_2021_2025.png` and `maps/notebook02c/03_change_map.png`.

<!-- forecast:section -->

## 5. The 2026 forecast so far

With data to 16 Nov 2026, from the latest committed run of Notebook 04. This section is rewritten after each weekly check by `report/update_forecast_text.py`, and the score is final after 30 Nov.

- **The forecast, issued 1 Nov from data to 26 Oct.** The method is past seasons rescaled, which was best in backtests over 2021–2025 [Ours].
  - **Punjab:** about 2,700 more Suomi NPP detections by 30 Nov (80% range 2,200–6,400), or about 3,500 for the season, against 4,269 in 2025 [Ours].
  - **Sangrur:** about 44 more (range 23–65), resting on only 3 detections to 26 Oct [Ours].
  - **Busiest week:** most likely week 8 (3–9 Nov) for both [Ours].
- **Weeks checked so far: 7–9, 27 Oct to 16 Nov.** Week 7 was the last week Suomi NPP covered.
  - **Punjab, week by week:** 870 detections against 956 forecast in week 7 (10% too high), 1,548 against 1,148 in week 8 (26% too low) and 903 against 577 in week 9 (36% too low) [Ours].
  - **Punjab, together:** 3,322 against 2,681, about a fifth too low. The last-season baseline came closest (3,110, 6% too low), and SARIMA forecast more than twice as high (7,246) [Ours].
  - **Sangrur:** 56, 188 and 90 against 14, 19 and 6: together 333 against 38, about nine times too low. SARIMA came closest (332), and the last-season baseline forecast about a quarter too high (428). The fragile forecast failed, as flagged when it was issued [Ours].
  - **Busiest week so far:** week 8 for both, as forecast [Ours].
- **The season so far.** Punjab's 4,071 detections to 16 Nov already exceed the 1 Nov forecast for the whole season (about 3,500), but lie inside its 80% range of 2,954–7,143 [Ours].
- **The updated forecast,** remade at each weekly run since 10 Nov beside the fixed one, which stays the test: on 18 Nov it put the season at 4,236 for Punjab and 346 for Sangrur, against 4,269 and 481 in 2025 [Ours].
- **From week 8, counts come from NOAA-20.** Suomi NPP data stopped at 13:00 UTC on 2 Nov 2026 [Reported]. So the actual counts are NOAA-20's, converted with the two sensors' 2026 ratio (0.89) [Ours].

Figure: `maps/notebook04/04_forecast_check.png`.

<!-- /forecast:section -->

## 6. What it adds up to

- **Fire counts don't measure how much burned.**
  - Read from fire counts alone, burning in Sangrur fell 95% from 2021 to 2025. The burnt-area map says it halved [Ours].
  - In 2025, about a fifth of the harvest still burned, and nine-tenths of that burnt area had no fire detection nearby [Ours].
- **For the straw buyer:** the burnt-area and harvest maps show where straw was still lying and for how long. A 5-day refresh matches the roughly 10 days between harvest and burning [Recommendation].
- **For the agriculture department:** fire counts can no longer show whether burning is falling. A burnt-area map measures it directly, a few days behind, while each 5-day composite fills [Recommendation].

## Sources

- **Reported:**
  - The Tribune, "Satellites miss majority of stubble fires…", 9 Dec 2025, reporting the iFOREST *Stubble Burning Status Report 2025*: https://www.tribuneindia.com/news/delhi/satellites-miss-majority-of-stubble-fires-delhi-air-pollution-underestimated-report. The primary report has not been located yet (`sources/references.md`).
  - CIRA RAMMB, "NOAA-21 designated as the primary satellite of the JPSS constellation", 3 May 2024: https://rammb2.cira.colostate.edu/visit-blog/2024/05/03/noaa-21-designated-as-the-primary-satellite-of-the-jpss-constellation
  - NOAA NESDIS, Update #2 on the cessation of Suomi NPP data at 13:00 UTC on 2 Nov 2026, issued 19 Oct 2026: https://www.nesdis.noaa.gov/news/administrative-update-2-cessation-of-suomi-national-polar-orbiting-partnership-s-npp-data-users-november-02-2026-1300-utc-and-decommissioning-issued-october-19-2026-1400-utc
- **Ours:** `report/findings_numbers.py` prints every number above from these files in `data/processed/`:
  - Notebook 02: `s2_burn_summary_sangrur_2025.csv`, `s2_burn_by_window_sangrur_2025.csv`, `firms_detections_sangrur_2025.csv`, `validation_accuracy_sangrur_2025.csv`, `validation_area_estimate_sangrur_2025.csv`, `validation_unsure_bounds_sangrur_2025.csv`
  - Notebook 02c: `season_comparison_sangrur.csv`, `season_comparison_by_band_sangrur.csv`, the 1 km grids and 20 m burn maps of both seasons
  - Notebook 01: `firms_detections_by_season_state.csv`
  - Notebook 04: `fire_forecast_2026_summary.csv`, `fire_forecast_check_2026.csv` and `fire_forecast_2026_updates_summary.csv`
