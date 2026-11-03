# Limitations

**Question.** What can't this analysis conclude, and which way would each limit move the findings?

This draft is for Section 8 (Limitations) of the report. It brings together the limits stated in `methodology/methodology.md` and the README, and says how far each one reaches. Section 10 (Next steps) takes up the experiments that would narrow them.

**Labels**, as in the other drafts:
- **[Reported]** comes from a cited source.
- **[Ours]** was measured in this project, for Sangrur district on its pre-2021 boundary.
- **[Recommendation]** is our judgement.

## 1. Burnt area is a lower bound, not the straw burnt

- **Small and partial burns may never show.** A burn covering only part of a 20 m pixel may not pass the rule's three tests. How small a burn the rule can see has not been measured [Ours]. Two practices could produce such burns:
  - **Straw burnt in small heaps.** A farmer in Maharashtra described burning residue in small patches over time (personal communication to us). It is one person's account from another state. How common the practice is in Sangrur is unknown [Reported].
  - **Only the loose straw burnt.** In villages of Sangrur and Patiala, farmers burnt only the loose straw the combine leaves, with the stubble left standing, then sowed with a super seeder (Rajpurohit 2022) [Reported]. Such burns would leave patchier, lighter scars. Some of the `dull` points that stayed `unsure` may be of this kind [Recommendation].
- **Fire counts don't fill the gap.** VIIRS can detect small fires (Schroeder et al. 2014), but only those burning while a satellite passes [Reported]. So brief, small fires are rarely counted either [Recommendation].
- **Scars fade within days.**
  - In the label strips, a black field looked like tilled soil again within two to three days [Ours].
  - A burn between two clear views can be invisible to both the map and the labels. So a `no` label means "no burn visible", not "not burnt" [Ours].
- **Which way it moves the findings.**
  - The 63,400 ha is a field-scale lower bound [Recommendation].
  - The missed share keeps its definition, but fire counts probably miss more burning than 90.6% suggests. The burns the map can't see are the small and brief ones fire counts are least likely to catch [Recommendation].
- **Burnt area is not the straw burnt,** and "harvested, not seen burnt" is not straw still available. Some of that straw was ploughed in or removed, and some burns were missed [Ours].

## 2. Limits of the accuracy figures

- **Labels come from images, not field visits.** Every point was read twice: by the author, and independently by Claude, an AI assistant, from the same image strips and reflectance values. Disagreements were resolved and doubtful points left `unsure`. Neither reader visited the fields [Ours].
- **The doubtful points are many.**
  - 53 of the 240 points (22%) stayed `unsure` [Ours].
  - Counted both ways, F1 runs from 0.78 to 0.92, and the burnt area from the labels from 52,700 to 141,200 ha [Ours].
  - At 26 points, Sentinel-2 had no clear view for a week or more while the straw went, all between 23 Oct and 2 Nov. Landsat settled 3 of them. At 16 of the rest, the straw was there on 27 Oct and gone by 2 Nov, with no clear view from either satellite in between [Ours].
- **Field edges and small patches are untested.**
  - Points sit at the centres of uniform 3 × 3 blocks (60 m across), so accuracy at field edges and in small burnt patches is not measured [Ours].
  - That is where the rule and the Random Forest disagree most: 91% of the pixels only the rule calls burnt lie on the edge of a burnt patch [Ours].
- **Late burns are unconfirmed.** From 19 Nov, damp soil under a young crop can pass the burn tests, so 8,200 ha are kept out of the headline. Some may be real burns: if all of them were, 2025's burnt area would be 71,600 ha [Ours].
- **There is no crop map.** "Harvested" means land that greened and was then harvested during the season. It is not checked to be paddy [Ours].

## 3. The missed share depends on how "nearby" is defined

- **The radius is a choice.**
  - A VIIRS detection gives the centre of a fire pixel, nominally 375 m across, not the fire's exact position [Reported].
  - So "nearby" is a choice, and the 2025 missed share ranges from 90.6% (VIIRS within 375 m) to 60.4% (VIIRS within 750 m or MODIS within 1 km) [Ours].
  - Under every rule tried, most of the burning went undetected [Ours].
- **A detection counts only at the right time:** between the pixel's last clear view and the window in which its burn shows. A detection made before that last clear view, while the field still looked unburnt, is not credited, however close it lies [Ours].
- **Why the counts miss is not shown.**
  - These data have no burn times, so they can't say whether the missed fires were late in the day, small or brief [Ours].
  - The finding that most large fires occur after 3 pm is iFOREST's, known here only through news reports. The primary report has not been located [Reported].

## 4. The 2021 comparison

- **The 2021 map has no labels of its own.** It applies the rule as checked on the 2025 labels, so its accuracy is unknown [Ours].
- **Seasons can differ.** Smoke, cloud and soil moisture can change how well the rule works [Recommendation].
- **The satellites' passes changed between the seasons.** NOAA-20 moved in its orbit in April 2024, so the spacing between the two satellites' passes was not the same in 2021 and 2025 [Reported].
- **The 19 Nov cut-off weighs more on 2021.** Late burns are 14% of all mapped burns in 2021, against 11% in 2025, and 27% in the south in 2021 [Ours].
  - The conclusion holds either way: burning fell 47% (confirmed) or 49% (all burns), against 95% for fire detections [Ours].
  - The fall by area, south to north, depends on the choice more: −23% or −39% in the south [Ours].

## 5. The forecast

- **It forecasts fire detections, not burnt area,** and only fires burning while a satellite passes [Ours].
- **The data differ in kind.** The 2026 counts are near-real-time data, while the archive the methods learn from is standard processing [Ours].
- **The ranges are rough.** Ten backtest seasons give only a rough 80% range. Sangrur's weekly counts are small, and its forecast rests on 3 detections, so its range is probably too narrow, as week 7 showed [Ours].
- **Later weeks are converted.** Suomi NPP data stopped on 2 Nov 2026 [Reported]. From week 8, the actual counts are NOAA-20's converted by a ratio estimated from the 2026 weeks both sensors covered, which adds uncertainty to the check [Ours].

## 6. Scope

- **One district, two seasons.** Sangrur on its pre-2021 boundary, in 2021 and 2025. Districts with different practices, crops or harvest dates may differ [Recommendation].
- **Optical data only.** Sentinel-1 radar sees through cloud and smoke [Reported], but it is untested here (`mission_tradeoff.md`) [Ours].
- **The product is untested.** Whether buyers would pay, and whether a 5-day map arrives in time to change where balers go, are open questions [Ours].
- **Health effects are not measured.** Air quality appears only as context [Ours].

## Sources

- Rajpurohit, S. (2022). Punjab's farmers are burning less stubble. Thanks to super seeders. *Newslaundry*, 14 November 2022. https://www.newslaundry.com/2022/11/14/punjabs-farmers-are-only-partially-burning-stubble-thanks-to-super-seeders (accessed 2026-10-30).
- Schroeder, W., Oliva, P., Giglio, L. and Csiszar, I. A. (2014). The new VIIRS 375 m active fire detection data product: algorithm description and initial assessment. *Remote Sensing of Environment* 143, 85–96. https://doi.org/10.1016/j.rse.2013.12.008
- The Tribune, "Satellites miss majority of stubble fires…", 9 Dec 2025, reporting the iFOREST *Stubble Burning Status Report 2025*: https://www.tribuneindia.com/news/delhi/satellites-miss-majority-of-stubble-fires-delhi-air-pollution-underestimated-report
- CIRA RAMMB, "NOAA-21 designated as the primary satellite of the JPSS constellation", 3 May 2024: https://rammb2.cira.colostate.edu/visit-blog/2024/05/03/noaa-21-designated-as-the-primary-satellite-of-the-jpss-constellation
- NOAA NESDIS, Update #2 on the cessation of Suomi NPP data at 13:00 UTC on 2 Nov 2026, issued 19 Oct 2026 (link in `findings.md`).
- NASA FIRMS attribute definitions for VIIRS 375 m active fire data ("Center of nominal 375 m fire pixel"), as listed in the Earth Engine community catalog: https://gee-community-catalog.org/projects/firms_vector/ (accessed 2026-11-03). FIRMS's own FAQ page could not be fetched from here.
- Sentinel-1 seeing through cloud and smoke: ESA, Sentinel-1 facts and figures, as cited in `mission_tradeoff.md`.
- **Ours:** `methodology/methodology.md`, sections 4–8, and the files listed in `findings.md`. The share of late burns is computed from `s2_burn_summary_sangrur_2021.csv` and `_2025.csv`, and their share in the south from `season_comparison_by_band_sangrur.csv`.
