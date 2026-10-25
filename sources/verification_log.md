# Verification log

How the hand-compiled research datasets were checked against their sources, and what changed as a result. Newest first.

## Dataset B (satellite missions): spot-check of 25 Oct 2026, corrections of 26 Oct 2026

**The check.** All 170 checks in `sources/dataset_B_verification.xlsx` were done against their linked pages on 25 Oct 2026.

| Result | Checks |
|---|---|
| Confirmed | 159 |
| Not on page (page didn't load) | 7 |
| Partly | 3 |
| Wrong | 1 |

**The re-check.** Every check not marked confirmed was re-checked on 26 Oct 2026, against the same page or another official one. The quotes recorded for the confirmed checks were also re-read. That turned up three more items: two statuses that later notices had overtaken, and a date whose page gives only the month.

| Checks | Satellite and field | Spot-check finding (25 Oct) | Re-check and change (26 Oct) | Source |
|---|---|---|---|---|
| B092 | Suomi NPP: mission status | **Wrong.** The page says 2 Nov 2026; the dataset said 1 Nov. | Corrected to 13:00 UTC on 2 Nov 2026. NOAA's Update #2, issued 19 Oct 2026, moved the date "as November 1 falls on a Sunday"; its first notice (3 Aug 2026) said 1 Nov. Also added: the satellite is to be lowered for re-entry from 1 Dec to about 12 Dec 2026. The README, methodology and problem statement are corrected too, and a decision-log row records the change. | [NOAA, Update #2](https://www.nesdis.noaa.gov/news/administrative-update-2-cessation-of-suomi-national-polar-orbiting-partnership-s-npp-data-users-november-02-2026-1300-utc-and-decommissioning-issued-october-19-2026-1400-utc) |
| B082, B085, B087 | Suomi NPP, NOAA-20, NOAA-21: spatial resolution | **Partly.** The page treats 375 m and 750 m as different things. | Reworded in the FAQ's terms: VIIRS has 5 bands at 375 m and 17 at 750 m, and FIRMS fire pixels are 375 m (bands I3 and I4, with the 750 m band M11). "Moderate bands" is dropped, since the FAQ doesn't use it. | [FIRMS FAQ](https://www.earthdata.nasa.gov/faq/firms-faq) |
| B095–B098 | NOAA-20: launch date, sensor, orbit, launch vehicle | **Not on page.** The NASA EOSPSO page didn't load. Launch date, sensor and vehicle were confirmed through a web search. | No change. The page loaded on 26 Oct and gives 18 Nov 2017, a Delta II 7920-10C from Vandenberg, VIIRS among the instruments, 833 km, 98.7° and a 1:30 pm local node. | [NASA EOSPSO](https://eospso.gsfc.nasa.gov/missions/joint-polar-satellite-system-1) |
| B141–B143 | Sentinel-2A, 2B, 2C: data product | **Not on page.** The EOPF product-specification page didn't load. | Source replaced with ESA's Level-2A product-formatting page, which states "a scene classification map at 20 m and 60 m resolutions", the 60 m map being resampled from the native 20 m one. The value now says so. | [ESA Sentinel Online](https://sentinel.esa.int/web/sentinel/technical-guides/sentinel-2-msi/level-2a/product-formatting) |
| B084, B086, B088–B090 | Suomi NPP, NOAA-20, NOAA-21, Terra, Aqua: FIRMS products | Confirmed: the FAQ gives the start dates. | The product names (VIIRS_SNPP_SP and the rest) aren't in the FAQ. The FIRMS area API page lists them and is now a source. Other changes: <ul><li>Terra and Aqua say that MODIS_SP and MODIS_NRT combine both satellites, and Aqua's start is given as 4 Jul 2002, as in the FAQ.</li><li>NOAA-21 notes that FIRMS has no standard-processing product.</li><li>NOAA-20 notes that FIRMS's data-availability listing (API tutorial, 2025) starts VIIRS_NOAA20_SP on 1 Apr 2018, earlier than the FAQ's 1 Jan 2020.</li></ul> | [FIRMS FAQ](https://www.earthdata.nasa.gov/faq/firms-faq); [FIRMS area API](https://firms.modaps.eosdis.nasa.gov/api/area/csv); [FIRMS API tutorial](https://firms.modaps.eosdis.nasa.gov/content/academy/data_api/firms_api_use.html) |
| B144 | Sentinel-1C: note | Confirmed | Reworded and sourced to ESA's launch article of 6 Dec 2024. It says Sentinel-1C, with Sentinel-1A, would "return the mission to its full potential as a two-satellite constellation", and that Sentinel-1B's mission ended in Aug 2022 after a technical fault. | [ESA](https://esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-1/Double_win_for_Europe_Sentinel-1C_and_Vega-C_take_to_the_skies) |
| B029 | Sentinel-1C: mission status | Confirmed, but the page gives a plan ("early July 2026 approximately"). | Updated from later CDSE notices. The orbit change ran 9–23 Jun 2026, with the return scheduled for 24 Jun, and on 30 Jun 2026 CDSE reported Sentinel-1C and 1D fully operational. | [CDSE, 28 May 2026](https://dataspace.copernicus.eu/node/3949); [CDSE, 30 Jun 2026](https://dataspace.copernicus.eu/node/4026) |
| B030 | Sentinel-1D: mission status | Confirmed (open access from 17 Apr 2026) | "Planned" and "phased out in July 2026" were out of date. The value now reads "open data access from 17 Apr 2026; Sentinel-1A operations ended on 30 Jun 2026". | [CDSE, 30 Jun 2026](https://dataspace.copernicus.eu/node/4026) |
| B137 | Resourcesat-2A: launch date | Confirmed, but the page gives only the month (December 2016) | Value unchanged (7 Dec 2016). ISRO's PSLV-C36 page, which states the day, is added as a source. | [ISRO, PSLV-C36](https://www.isro.gov.in/mission_PSLV_C36.html) |

**Rows changed.** Eleven rows were changed: Sentinel-2A, 2B and 2C, Sentinel-1C and 1D, Suomi NPP, NOAA-20, NOAA-21, Terra, Aqua and Resourcesat-2A. Their `access_date` is now 2026-10-26. No row was removed, and no blank field was filled by guesswork.

**Open item.** FIRMS gives two start dates for NOAA-20's standard-processing archive: 1 Jan 2020 in its FAQ and 1 Apr 2018 in the data-availability listing. If the 2018 date is right, the 2018 and 2019 seasons could join the Suomi NPP/NOAA-20 overlap behind Notebook 01's ratio, which now uses 2020–2025. The live data-availability service, which needs the map key, would settle it.

## Dataset A (Indian space ecosystem)

Spot-check under way (`sources/dataset_A_verification.xlsx`).
