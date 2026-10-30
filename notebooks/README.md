# Notebooks

Run them in order. Each notebook writes to `data/processed/` and `maps/`, and logs every dataset it uses in `sources/source_register.csv`.

| Notebook | Question | Status | Key or login needed |
|---|---|---|---|
| `01_fire_counts.ipynb` | How many VIIRS fire detections per season, where, and at what time of day? Which district should we study? | Run on 22 Oct 2026 | `FIRMS_MAP_KEY` |
| `02_eo_analysis_burnt_area.ipynb` | How much area burned in Sangrur in 2025, when, and what share did fire counts miss? | Whole district run on 26 Oct 2026; validation labels completed 30 Oct 2026; calibration next | Copernicus Data Space login (openEO) and `FIRMS_MAP_KEY` |
| `03_ml_burn_classifier.ipynb` | Does a Random Forest beat the rule-based burn map? | Week 3 | none |
| `04_fire_forecast.ipynb` | When will the season peak, and how high? | Week 3 | `FIRMS_MAP_KEY` |

Where keys go: on your computer, in a `.env` file in the project folder (one `NAME=value` line each; git ignores the file). In Colab, in Secrets (key icon in the left sidebar).

Tip: run the whole notebook with **Run All** (VS Code) or **Runtime → Run all** (Colab). Running cells out of order can leave stale variables behind. No GPU is needed.

Notebook 02 runs in steps, because its openEO jobs use Copernicus credits:
1. A 10 km pilot, which projects the cost and download size of the whole district.
2. The whole district, after you set `RUN_FULL = True`. This run also draws the validation points and fetches single-date images around them for labelling (one more small openEO job).
3. A final run after the validation points are labelled.

Its downloads go to `data/raw/sentinel2/`, which git ignores. The whole-district run on 26 Oct 2026 downloaded about 1 GB and used 8 credits (the pilot had projected 1.8 GB and 135); it is best done on a computer rather than in Colab.
