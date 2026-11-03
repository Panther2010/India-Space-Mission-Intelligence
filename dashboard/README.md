# Dashboard (Streamlit)

Version 1, built 3 Nov 2026. The app reads the files the notebooks and scripts have written to `data/processed/`, the research datasets in `data/raw/research/`, the figures in `maps/` and the drafts in `report/` and `methodology/`. Nothing heavy is computed while it runs, and every number it shows comes from those files.

| Page | What it shows |
|---|---|
| Overview | The headline finding, a map of 2025's burnt area per 1 km square with the VIIRS detections over it, the headline numbers and what each page shows |
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

Run it from the project folder, as above: Streamlit reads the look from `.streamlit/config.toml` in the folder it is started from. An older Streamlit runs the app with its default look, and may warn about theme settings it doesn't know.

## The look

- **Colours.** Night navy, with ember orange for burning and sky blue for satellite fire detections, set in `.streamlit/config.toml` and repeated in `common.py` for the parts drawn in code. Text has at least 4.5:1 contrast on the navy, and the colours that tell chart series apart at least 3:1.
- **Type.** Rajdhani for headings and numbers, Hind for text, both by Indian Type Foundry under the SIL Open Font License 1.1 (`static/OFL-Rajdhani.txt`, `static/OFL-Hind.txt`). The app serves them itself from `static/`, so it needs no font service.
- **Maps.** The OpenStreetMap tiles are turned dark in the browser, with a CSS filter. Colour ramps run from dark to bright, so the squares with the most stand out. VIIRS detections are drawn 750 m across: the 375 m around each one that the missed share counts as flagged.
- **Logo.** `static/logo.svg` and `static/mark.svg`: a burnt 1 km square circled by a satellite's orbit, with the name in Rajdhani drawn as outlines.

## Put it online (Streamlit Community Cloud)

The app has been online since 3 Nov 2026 at https://india-space-mission-intelligence-dashboard.streamlit.app. To deploy it again, or a copy of it:

1. Sign in at https://share.streamlit.io with GitHub, and allow it to read this repository.
2. Create an app from the repository `Panther2010/India-Space-Mission-Intelligence`, branch `main`, main file `dashboard/app.py`.
3. Community Cloud installs `dashboard/requirements.txt`, because it looks in the app's folder before the repository root. That file holds only what the dashboard needs, not the notebooks' heavier packages.
4. The repository is private, so the app starts private. To share the link, make the app public in its sharing settings. Community Cloud allows one private app at a time.

Steps 3 and 4 follow Streamlit's documentation, read on 3 Nov 2026: [app dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies) and [sharing your app](https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app). The look lives in `.streamlit/config.toml` at the repository root, because Community Cloud runs the app from the root even when the main file is in a subfolder ([file organization](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization), read on 3 Nov 2026).

## Share it as a file

`paddy-burnt-area-dashboard.html` is one file to send instead of a link. It opens the live app inside a page with the project's name and an "Open in a new tab" button, so it always shows the current app; it holds no data itself.

- **The app must be public.** Streamlit doesn't support embedding private apps ([embed your app](https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app/embed-your-app), read on 3 Nov 2026).
- **Sleeping apps.** Community Cloud puts apps to sleep after 12 hours without traffic, and anyone who opens one can wake it with "Yes, get this app back up!" ([manage your app](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app), read on 3 Nov 2026). The file says so.
- **If the app's address changes,** replace the address in the file: it appears twice, in the button and in the frame.

## What the app shows, and when it changes

The app shows whatever is committed to `main`, so it keeps itself up to date: run a notebook in VS Code, commit and push its outputs, and the app shows them. Community Cloud watches the repository and copies committed changes into the running app ([Streamlit: edit your app](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/edit-your-app), read on 3 Nov 2026), and the app re-reads any file that has changed. If it ever shows old numbers, reboot it from its menu on Community Cloud.

The 2026 forecast tab shows the forecast as issued on 1 Nov 2026 and the weeks checked in the last committed run of Notebook 04. The check is committed after each weekly run (from 3 Nov), so the tab moves on week by week: what happened, the headline forecast for that week, and their ratio.

## Files

- `app.py`: page navigation
- `overview.py`: the front page
- `views/`: one file per page
- `common.py`: paths, cached file readers (re-read when a file changes), the page header, number cards, the dark map style and small helpers
- `static/`: the fonts, their licences and the logo, served by the app at `app/static/`
- `paddy-burnt-area-dashboard.html`: the file to share, which opens the live app
- `requirements.txt`: the packages for Community Cloud
- `../.streamlit/config.toml`: the theme and static file serving
