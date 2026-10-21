# Notebooks

Run them in order. Each notebook writes to `data/processed/` and `maps/`, and logs every dataset it uses in `sources/source_register.csv`.

| Notebook | Question | Status | Key or login needed |
|---|---|---|---|
| `01_fire_counts.ipynb` | How many VIIRS fire detections per season, where, and at what time of day? Which district should we study? | Ready to run | `FIRMS_MAP_KEY` |
| `02_eo_analysis_burnt_area.ipynb` | How much area burned in the chosen district in 2025, and what share did fire counts miss? | Week 2 | Copernicus Data Space login |
| `03_ml_burn_classifier.ipynb` | Does a Random Forest beat the rule-based burn map? | Week 3 | none |
| `04_fire_forecast.ipynb` | When will the season peak, and how high? | Week 3 | `FIRMS_MAP_KEY` |

Where keys go: on your computer, in a `.env` file in the project folder (one `NAME=value` line each; git ignores the file). In Colab, in Secrets (key icon in the left sidebar).

Tip: run the whole notebook with **Run All** (VS Code) or **Runtime → Run all** (Colab). Running cells out of order can leave stale variables behind. No GPU is needed.
