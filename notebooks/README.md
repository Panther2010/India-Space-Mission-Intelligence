# Notebooks

Run them in order. Each notebook writes to `data/processed/` and `maps/`, and logs every dataset it downloads in `sources/source_register.csv`.

| Notebook | Question | Status | Key or login needed |
|---|---|---|---|
| `01_fire_counts.ipynb` | How many VIIRS fire detections per season, where, and at what time of day? Which district should we study? | Run on 22 Oct 2026 | `FIRMS_MAP_KEY` |
| `02_eo_analysis_burnt_area.ipynb` | How much area burned in Sangrur in 2025, when, and what share did fire counts miss? | Whole district run on 26 Oct 2026; validation labels completed and the burn rule checked against them on 30 Oct 2026. Maps other seasons too, with `SEASON_YEAR`: 2021 mapped on 1 Nov 2026 for Notebook 02c | Copernicus Data Space login (openEO) and `FIRMS_MAP_KEY` |
| `02b_landsat_views.ipynb` | Do Landsat 8 and 9 (HLS) add clear views where Sentinel-2 had none, so `unsure` validation points can be settled? | Run 31 Oct 2026: 3 of the 26 `gap` points relabelled; also draws a Sentinel-2 and Landsat timeline for each `gap` point | NASA Earthdata token (`EARTHDATA_TOKEN`) |
| `02c_season_comparison.ipynb` | From 2021 to 2025, did the burnt area fall as fast as fire detections, and do fire counts now miss more of the burning? | Run 1 Nov 2026: from 2021 to 2025 the burnt area fell 47% while Suomi NPP detections fell 95%; on the same two satellites, the share of burnt area with no detection rose from 27% to 94%. Under a minute; downloads nothing | none |
| `03_ml_burn_classifier.ipynb` | Does a Random Forest beat the rule-based burn map? | Run 31 Oct 2026: the forest ties the rule at the labelled points (F1 0.92 each) but maps less burnt area, so the rule stays. Takes about 5 minutes and downloads nothing | none |
| `04_fire_forecast.ipynb` | When will the 2026 season peak, and how high? | Forecast issued 1 Nov 2026 from weeks 1–6 and saved. Later runs check it against what happened, and from 3 Nov the check is committed after each weekly run so the dashboard stays current; the final score comes after 30 Nov. From 10 Nov each run also makes an updated forecast from every week seen so far (section 7), kept beside the 1 Nov forecast. About a minute | `FIRMS_MAP_KEY` |

Where keys go: on your computer, in a `.env` file in the project folder (one `NAME=value` line each; git ignores the file). In Colab, in Secrets (key icon in the left sidebar).

Tip: run the whole notebook with **Run All** (VS Code) or **Runtime → Run all** (Colab). Running cells out of order can leave stale variables behind. No GPU is needed.

Notebook 02 runs in steps, because its openEO jobs use Copernicus credits:
1. A 10 km pilot, which projects the cost and download size of the whole district.
2. The whole district, after you set `RUN_FULL = True`. This run also draws the validation points and fetches single-date images around them for labelling (one more small openEO job).
3. A final run after the validation points are labelled.
4. Another season, for Notebook 02c: set `SEASON_YEAR = 2021` and repeat steps 1 and 2. There is no labelling step, because validation is for 2025 only. Then close the notebook without saving, so it stays set to 2025.

Its downloads go to `data/raw/sentinel2/`, which git ignores (another season's to `data/raw/sentinel2/sangrur_2021/`). The whole-district run on 26 Oct 2026 downloaded about 1 GB and used 8 credits (the pilot had projected 1.8 GB and 135); it is best done on a computer rather than in Colab. The 2021 run on 1 Nov 2026 used 20 credits (pilot 4, cloud-mask check 9, district 7) and downloaded about 0.95 GB for the district.

While a job's files download, the cell prints a line as each file arrives; on a slow connection a 60 MB composite can take several minutes. If a download breaks off, or gets no data for 2 minutes, it is tried again, up to five times before the cell stops. Running the cell again resumes the same openEO job without starting a new one, keeps the files already complete and fetches the rest.
