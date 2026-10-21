# Decision log

One row per decision: what was decided, what else was considered, and why. Newest first.

| Date | Decision | Options considered | Reason |
|---|---|---|---|
| 2026-10-22 | FIRMS downloads use 5-day requests, and shorten automatically if the API asks for fewer days | Keep 10-day requests as the API page documents | The live API rejected a 10-day request with "Invalid day range. Expects [1..5]." on 21 Oct 2026, although its documentation still says 1–10. |
| 2026-10-22 | Notebooks run on a laptop in VS Code or in Google Colab; no GPU | Colab only; Kaggle | No step needs a GPU: openEO processes Sentinel-2 on Copernicus servers, and the Random Forest and SARIMA models run on a CPU. Local runs write straight into the repository, and the Streamlit dashboard and QGIS need a local setup anyway. Kaggle's main advantage, a free GPU quota, does not apply. |
| 2026-10-21 | Re-baselined to 22 Oct–18 Nov 2026 with the same scope; the cut line moves to 4 Nov | Keep the 13 Nov finish by dropping the 2021 comparison, then the live 2026 refresh | The start slipped by five days. Keeping the full scope matters more than the original end date. |
| 2026-10-16 | The forecast trains on Suomi NPP detections and converts later counts using the NOAA-20 overlap | Train on NOAA-20 only (2020 onward); ignore the sensor change | NOAA ends Suomi NPP data delivery on 1 Nov 2026 (NOAA NESDIS notice, 3 Aug 2026). Suomi NPP has the longest single-sensor record (2012 onward). |
| 2026-10-16 | Personal portfolio project; no external approval step | Mentor sign-off checkpoint | The mentor gave the brief as a personal project. |
| 2026-10-16 | Dashboard in Streamlit | Power BI; both | Shows satellite maps natively, deploys free at a public link, and builds on a previous Streamlit deployment |
| 2026-10-16 | Four weeks, 17 Oct to 13 Nov 2026, at 15–20 hours a week | 8 or 12 weeks | Personal availability. A cut line is set in advance and checked on 30 Oct. |
| 2026-10-16 | Extras: an ML burn classifier and a fire-activity forecast | Customer interviews; brief only | Shows AI/ML and forecasting skills on top of the brief |
| 2026-10-16 | Use case: paddy-residue burnt-area intelligence in Punjab–Haryana | Crop-stress monitoring for crop insurance in Maharashtra; climate-health EO in a city | Distinctive and timely. It still counts as agricultural monitoring, and links agriculture, air quality and public health. |
