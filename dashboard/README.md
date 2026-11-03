# Dashboard (Streamlit)

Version 1, built 3 Nov 2026. The app reads the files the notebooks and scripts have written to `data/processed/`, the research datasets in `data/raw/research/`, the figures in `maps/` and the drafts in `report/` and `methodology/`. Nothing heavy is computed while it runs, and every number it shows comes from those files.

| Page | What it shows |
|---|---|
| Overview | The headline numbers and what each page shows |
| Mission Explorer | The 22 satellites and missions of dataset B: search, a filter by kind of data (our grouping of the sensor column), each record in full with its source, and launch dates |
| Indian Startup Landscape | The 32 companies of dataset A: a map at approximate city centres, counts by value-chain category and by state, and the table with sources |
| EO Analysis | Five tabs. **Burnt-area map:** 1 km squares for 2025 or 2021, coloured by burnt area, burnt area with no VIIRS detection, harvested area not seen burnt, or when harvest and burning were first seen, with the VIIRS detections and the 20 m map. **What fire counts missed:** the missed share under three rules, and burnt area and detections by 5-day window. **2021 against 2025:** Notebook 02c's results. **ML classifier:** the rule against the Random Forest and six other models. **2026 forecast:** the forecast as issued on 1 Nov and the weeks checked so far |
| Mission Trade-offs | `report/mission_tradeoff.md` |
| Commercial Opportunity | What the map gives the straw buyer and the agriculture department, the problem statement, and the next validation step |

Statements are labelled as in the report: [Reported] from a cited source, [Ours] measured in this project, [Recommendation] our judgement.

## Run it on your computer

From the project folder, in the `eo` environment (the project's `requirements.txt` already includes Streamlit, Folium and streamlit-folium):

```
D:/conda-envs/eo/python.exe -m streamlit run dashboard/app.py
```

It opens in the browser at http://localhost:8501. The maps need an internet connection, because the map tiles and the map library come from the web.

## Put it online (Streamlit Community Cloud)

1. Sign in at https://share.streamlit.io with GitHub, and allow it to read this repository.
2. Create an app from the repository `Panther2010/India-Space-Mission-Intelligence`, branch `main`, main file `dashboard/app.py`.
3. Community Cloud installs `dashboard/requirements.txt`, because it looks in the app's folder before the repository root. That file holds only what the dashboard needs, not the notebooks' heavier packages.
4. The repository is private, so the app starts private. To share the link, make the app public in its sharing settings. Community Cloud allows one private app at a time.

Steps 3 and 4 follow Streamlit's documentation, read on 3 Nov 2026: [app dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies) and [sharing your app](https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app).

## What the app shows, and when it changes

The app shows whatever is committed to `main`, so it keeps itself up to date: run a notebook in VS Code, commit and push its outputs, and the app shows them. Community Cloud watches the repository and copies committed changes into the running app ([Streamlit: edit your app](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/edit-your-app), read on 3 Nov 2026), and the app re-reads any file that has changed. If it ever shows old numbers, reboot it from its menu on Community Cloud.

The 2026 forecast tab shows the forecast as issued on 1 Nov 2026 and the weeks checked in the last committed run of Notebook 04. The check is committed after each weekly run (from 3 Nov), so the tab moves on week by week: what happened, the headline forecast for that week, and their ratio.

## Files

- `app.py`: page navigation
- `overview.py`: the front page
- `views/`: one file per page
- `common.py`: paths, cached file readers (re-read when a file changes) and small helpers
- `requirements.txt`: the packages for Community Cloud
