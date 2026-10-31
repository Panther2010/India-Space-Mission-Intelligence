# Mission trade-off

**Question.** Which satellite data should a paddy-straw buyer in Punjab rely on to see, every few days of the harvest, which fields still hold straw and which have been burnt?

This is Section 5 of the brief: data options compared on detail, how often the area is imaged, bands, clouds and season, coverage and cost, and validation. The lesson it is meant to teach holds here too: no satellite is best; what matters is which one fits the decision.

**Labels.**
- **[Reported]** comes from a cited source. Most of these facts come from dataset B (`data/raw/research/dataset_B_satellite_missions.csv`), which records each source URL and access date; the sources are also listed at the end.
- **[Ours]** was measured in this project, for Sangrur district in the 2025 season.
- **[Recommendation]** is our judgement.

## 1. The requirement

- **User and decision.** The lead user is the biomass procurement manager of a compressed-biogas plant, deciding where to send balers before straw is burnt. The second is the district agriculture officer, who tracks burnt area and the burning that fire counts miss (`methodology/problem_statement.md`).
- **What the data must do** [Recommendation]:
  - **Detail:** resolve single fields, so pixels of 30 m or finer, ideally 10–20 m.
  - **Frequency:** a clear view every few days from mid-October to late November. In 2025, burnt fields were first seen burnt a median of 10 days after harvest [Ours], and tilling can erase a scar between two views.
  - **Bands:** short-wave infrared (SWIR), which separates burnt fields from tilled or damp soil.
  - **Weather:** keep working through the cloud, haze and smoke of the burning season.
  - **Cost:** free for a prototype; paid data only where a customer would pay for what it adds.
  - **Validation:** results must be checkable against reference points.

## 2. The options on the six factors

| Option | Detail | How often | Bands | Clouds and season | Coverage and cost | Validation |
|---|---|---|---|---|---|---|
| **Sentinel-2 MSI** (2A, 2B, 2C) | 10 m visible and NIR; 20 m red-edge and SWIR [Reported] | 5 days at the equator with two satellites [Reported]. In 2025, with three, each point was imaged on 3 to 5 days in every 10 [Ours] | 13 bands, 443–2190 nm, with both SWIR bands (about 1.6 and 2.2 µm) that the burn tests use [Reported] | Optical: blind under cloud and thick smoke. In 2025 it still saw at least 99.9% of the district clearly in every 5-day window from 15 Oct, except 25–29 Oct (71%) [Ours] | Free and open; 290 km swath [Reported]. The whole-district job used 8 openEO credits [Ours] | Done here: 240 stratified reference points, 187 of them labelled burnt or not. Map as reported: F1 0.92, overall accuracy 0.96 [Ours] |
| **HLS: Landsat 8 and 9** (30 m, harmonised with Sentinel-2) | 30 m [Reported] | Every 8 days per orbital path with both satellites [Reported]; with Sentinel-2 in HLS, every 2–3 days [Reported]. Over Sangrur, pairs of dates a day apart every 8 days [Ours] | Both SWIR bands, on the Sentinel-2 grid [Reported] | Same optical limits. 27 Oct 2025 was nearly cloud-free (0–4%), but almost every November view carries a high-aerosol (smoke) flag [Ours] | Free with an Earthdata login; 185 km Landsat swath [Reported]. Reading small windows around 56 points took about 10 minutes on a home connection, and no credits [Ours] | Used to check labels: it settled 3 of 26 points that had a week-long gap in Sentinel-2 [Ours] |
| **VIIRS active fires** (FIRMS: Suomi NPP, NOAA-20, NOAA-21) | 375 m fire pixels [Reported] | Each satellite covers the globe daily; passes around midday and at night [Reported] | Thermal and mid-infrared fire detection: a fire at the moment of the pass, not a burn scar [Reported] | Misses fires under cloud or thick smoke and fires between passes; most large Punjab fires in 2024–25 were after 3 pm [Reported] | Free, near real time; 3,000 km swath [Reported]. Suomi NPP data ends on 2 Nov 2026; NOAA-20 and NOAA-21 continue [Reported] | Measured here: no detection within 375 m for 90.6% of the confirmed burnt area [Ours] |
| **Sentinel-1 SAR** (1A and 1C in 2025; 1C and 1D since July 2026) | 5 × 20 m in Interferometric Wide mode [Reported] | 6 days at the equator with two satellites [Reported] | C-band radar; no optical bands [Reported] | Sees through cloud and smoke [Reported] | Free and open; 250 km swath [Reported] | Not tested. Whether radar can tell burnt from baled straw is unproven here; it may date when straw leaves a field [Recommendation: test] |
| **Resourcesat-2 and 2A AWiFS** (ISRO) | 56 m at nadir, 70 m at the swath edge [Reported] | 2–3 days with both satellites [Reported] | Green, red, NIR and one SWIR band (1.55–1.70 µm) [Reported]. Without the 2.2 µm band, our burn rule (NBR, MIRBI) cannot run as it is [Ours] | Same optical limits | Free on NRSC Bhoonidhi, which opens data coarser than 5 m to all users; 740 km swath [Reported] | Not tested |
| **PlanetScope** (commercial) | About 3 m [Reported] | Near daily [Reported] | 8 bands, visible to NIR; no SWIR [Reported] | Same optical limits | Paid; scenes about 32.5 × 19.6 km [Reported] | Not tested |

**Other radars in dataset B.** India's EOS-04 (C-band) repeats every 17 days in its medium mode, and NISAR (L-band, public since July 2026) every 12 days [Reported]. Both are too slow for a straw window of about 10 days, so Sentinel-1 is the radar to test first [Recommendation].

## 3. What the 2025 season showed [Ours]

- **Sentinel-2 was the workhorse.** Going by the dates downloaded for each point, its three satellites passed over 171 of the 240 validation points on 5 days in every 10, over 65 on 3 days in every 10, and over 4 on 4 days in 10. In every 5-day window from 15 Oct to 3 Dec except 25–29 Oct, all but 0.1% of the district was seen clearly.
- **Its weak spot is the burning peak.** At 26 of 240 points (11%), no clear view came for a week or more while the straw went, all between 23 Oct and 2 Nov. Sentinel-2's repeat pattern also puts passes over these points on 28 and 30 Oct, but those scenes were either too cloudy to download (over 60% cloud) or showed cloud, thin cirrus or cloud shadow at the points.
- **Landsat helped, but little.** It imaged the district on 11 dates between 10 Oct and 25 Nov. Its 27 Oct pass was nearly cloud-free and gave a view inside the gap at all 26 points, but at 30 m and often under smoke flags. It settled 3 of them: one burnt, two not. At 16 of the other 23, the straw was still there on 27 Oct and gone by 2 Nov: a 6-day hole that neither optical mission could see into. The rest were damp, at a field edge, beside a canal or only just harvested.
- **Fire counts missed most of the burning.** No VIIRS detection fell within 375 m of 90.6% of the confirmed burnt area. Allowing 750 m still left 73.8% unseen, and adding MODIS detections within 1 km left 60.4%.

## 4. Recommendation [Recommendation]

For the buyer's decision, which harvested fields still hold straw, refreshed every few days:

1. **Sentinel-2 as the core.** It has the finest free detail with both SWIR bands (10–20 m), and in 2025 it saw almost the whole district in every 5-day window but one. Note that Sentinel-2A's extended campaign is set to end on 31 Dec 2026 [Reported]. From 2027, passes may fall back towards the two-satellite 5 days.
2. **HLS for extra dates.** It costs nothing and adds Landsat views on other days, on the same grid. Expect modest gains in the smoke weeks: 3 of 26 gap points in 2025.
3. **VIIRS for alerts, never for area.** Use it to flag fires the same day, and for long trends. It missed about 91% of the burnt area.
4. **Sentinel-1 is the next experiment.** It is the only option that sees through the late-October smoke. It probably cannot confirm a burn, but it may date when straw leaves a field, which is the buyer's question. Test it on the 23 gap points that are still `unsure`.
5. **AWiFS as an Indian backup, not the core.** It is free, wide and frequent, and has a SWIR band. But 56 m pixels blur fields more than Landsat's 30 m, which already struggled, and it lacks the 2.2 µm band. Worth a test for continuity, not as the main source.
6. **PlanetScope only for a paying customer.** Near-daily 3 m imagery would shrink the gaps, but it has no SWIR to tell a burnt field from damp soil, and it is paid.

## 5. How each option would be validated

- **Sentinel-2:** done. 240 points drawn by stratified random sampling, labelled from single-date imagery by two readers, with area-weighted accuracy and `unsure` points reported both ways (methodology, section 5).
- **HLS:** same points. A burn seen on a clear Landsat date counts as a burn; a "not burnt" call needs straw and plain soil at most 3 days apart (methodology, section 5).
- **VIIRS:** done, as the share of confirmed burnt area with no detection nearby (methodology, section 6).
- **Sentinel-1:** use the points whose straw-to-soil change is dated within 3 days by optical views, and test whether the radar change falls in the same window. Then try the 23 undated points.
- **AWiFS:** run a NIR–SWIR 1 index on the same points and compare it with the Sentinel-2 labels; report the accuracy lost at 56 m.
- **PlanetScope:** a small paid sample over the same points, if a customer pilot justifies it.

## Sources

Specifications marked [Reported] come from dataset B, rows for Sentinel-2A, 2B and 2C; Sentinel-1C and 1D; Landsat 8 and 9; Suomi NPP, NOAA-20 and NOAA-21; Resourcesat-2 and 2A; EOS-04; NISAR; and PlanetScope (SuperDove). The main pages, accessed 26 Oct 2026 unless noted:

- ESA, Sentinel-2 facts and figures: https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-2/Facts_and_figures
- CDSE, Sentinel-2A extended campaign: https://dataspace.copernicus.eu/node/3911
- ESA, Sentinel-1 facts and figures: https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-1/Facts_and_figures
- USGS, Landsat 8 and Landsat 9: https://www.usgs.gov/landsat-missions/landsat-8 ; https://www.usgs.gov/landsat-missions/landsat-9
- Sentinel Hub, HLS documentation (revisit of HLS): https://docs.sentinel-hub.com/api/latest/data/hls/
- NASA FIRMS FAQ: https://www.earthdata.nasa.gov/faq/firms-faq
- NOAA NESDIS, end of Suomi NPP data on 2 Nov 2026: https://www.nesdis.noaa.gov/news/administrative-update-2-cessation-of-suomi-national-polar-orbiting-partnership-s-npp-data-users-november-02-2026-1300-utc-and-decommissioning-issued-october-19-2026-1400-utc
- ISSDC, Resourcesat sensors: https://www.issdc.gov.in/docs/others/ResourceSat.pdf
- NRSC, EOS-04 brochure: https://bhoonidhi.nrsc.gov.in/bhoonidhi_resources/help/docs/E04_BROUCHURE.pdf
- NASA Earthdata, NISAR L-band data release: https://www.earthdata.nasa.gov/news/nisar-l-band-data-released-expanding-record-surface-changes (accessed 16 Oct 2026)
- NRSC, Bhoonidhi brochure 2025: https://www.nrsc.gov.in/nrscnew/assets/pdf/brochures/Bhoonidhi_Brochure_2025.pdf
- Planet, PlanetScope documentation: https://docs.planet.com/data/imagery/planetscope.md

The timing of Punjab's fires (most large ones after 3 pm in 2024–25) is from The Tribune's report of iFOREST's *Stubble Burning Status Report 2025*, 9 Dec 2025 (`sources/references.md`). The primary report has not been located yet.

Results marked [Ours] come from Notebook 02 (`data/processed/s2_burn_summary_sangrur_2025.csv`, `s2_burn_by_window_sangrur_2025.csv`, the single dates fetched for the validation points) and Notebook 02b (`hls_l30_scenes_sangrur_2025.csv`, `validation_landsat_views_sangrur_2025.csv`).
