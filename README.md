# India Space Mission Intelligence

### Paddy burnt-area monitoring with open satellite data

![Status](https://img.shields.io/badge/status-in%20progress-orange)
![Python](https://img.shields.io/badge/python-3-blue)
![Data](https://img.shields.io/badge/data-Sentinel--2%20%7C%20VIIRS-2ea44f)
![Dashboard](https://img.shields.io/badge/dashboard-Streamlit-ff4b4b)

A decision-support prototype that maps paddy-residue burnt area in Punjab from Sentinel-2 imagery. It also measures how much of that burning the VIIRS fire counts, which official monitoring relies on, never see. The project is built to the *Satellite Mission Intelligence for India* deep-tech portfolio brief. That brief covers the Indian space ecosystem, a sourced satellite mission dataset, a reproducible geospatial analysis, mission trade-offs and a product concept.

> **Core question:** in a high-burning Punjab district, what share of the burnt area visible in Sentinel-2 imagery during the 2025 season was never flagged by a VIIRS fire detection?

## At a glance

| | |
|---|---|
| **Users** | Buyers of paddy straw for energy, such as compressed-biogas plants, deciding where and when to collect straw. State agriculture departments deciding where to send residue-management machinery. |
| **Area and period** | One Punjab district. Main season: 15 Sep–30 Nov 2025. Comparison: 2021. The 2026 season serves as a live demo. |
| **Satellite data** | Sentinel-2 L2A (Copernicus), VIIRS active fires (NASA FIRMS), ESA WorldCover cropland. Sentinel-1, HLS and Resourcesat are compared in the mission trade-off. |
| **Methods** | Multi-date burn indices (NBR, MIRBI, NDVI), accuracy assessment against reference points, a Random Forest classifier, and a fire-activity forecast (SARIMA vs a seasonal baseline) |
| **Outputs** | Burnt-area maps, the share of burning the fire counts missed, a Streamlit dashboard, an 8–12 page report and a product one-pager |

## Why this matters

- Official stubble-burning monitoring counts fires seen by MODIS and VIIRS in a narrow midday window.
- A December 2025 report by iFOREST says most large Punjab farm fires in 2024 and 2025 occurred after 3 pm ([as reported by The Tribune](https://www.tribuneindia.com/news/delhi/satellites-miss-majority-of-stubble-fires-delhi-air-pollution-underestimated-report)).
- NOAA ends Suomi NPP data delivery on 1 Nov 2026 ([NOAA notice](https://www.nesdis.noaa.gov/news/cessation-of-suomi-national-polar-orbiting-partnership-s-npp-data-users-onafter-november-01-2026)).
- The two VIIRS satellites that remain pass about 25 minutes before and after Suomi NPP ([CIRA, May 2024](https://rammb2.cira.colostate.edu/visit-blog/2024/05/03/noaa-21-designated-as-the-primary-satellite-of-the-jpss-constellation)). So no VIIRS sensor looks later in the afternoon.
- Burnt area measured from Sentinel-2 is an established method ([NRSC, 2023](https://www.nrsc.gov.in/sites/default/files/ScienceStory/Science_Story_Stubble_burning_Pun_Har_2023.pdf)). This project applies it at district level and quantifies what fire counts miss.

## How the pieces fit

```mermaid
flowchart LR
    firms["NASA FIRMS<br/>VIIRS fire detections"] --> nb1["01 · Fire counts<br/>trend, timing, districts"]
    s2["Copernicus<br/>Sentinel-2 L2A"] --> nb2["02 · Burnt-area map<br/>and validation"]
    nb1 -- "district choice" --> nb2
    nb2 --> missed["Missed share<br/>burnt area with no VIIRS detection"]
    nb2 --> nb3["03 · ML burn classifier"]
    firms --> nb4["04 · Fire-activity forecast"]
    missed --> dash["Streamlit dashboard"]
    nb3 --> dash
    nb4 --> dash
    research["Datasets A and B<br/>ecosystem and missions"] --> dash
```

## Deliverables

| # | Deliverable | Where | Status |
|---|---|---|---|
| 1 | Research datasets: Indian space ecosystem (A) and satellite missions (B) | `data/raw/research/` | B drafted, under verification; A in progress |
| 2 | Python notebooks | `notebooks/` | 01 ready to run |
| 3 | Geospatial analysis: QGIS project and export-ready maps | `maps/` | Planned |
| 4 | Interactive dashboard (Streamlit) | `dashboard/` | Planned |
| 5 | GitHub repository | this repo | Set up |
| 6 | Technical and product report, 8–12 pages | `report/` | Planned |
| 7 | Product one-pager | `report/` | Planned |
| 8 | Three-minute demo | `report/` | Planned |

## Repository structure

```
India-Space-Mission-Intelligence/
├── README.md
├── decision_log.md          dated decisions and the reasons for them
├── requirements.txt
├── data/
│   ├── raw/                 downloads, never edited; only research/ is committed
│   │   └── research/        hand-compiled datasets A (ecosystem) and B (missions)
│   └── processed/           outputs written by notebooks and scripts
├── notebooks/               01 fire counts · 02 burnt area · 03 ML classifier · 04 forecast
├── src/                     shared helper code, once notebooks stabilise
├── dashboard/               Streamlit app
├── maps/                    export-ready maps and the QGIS project
├── methodology/             problem statement and method notes
├── sources/                 source register, references and verification log
└── report/                  report, one-pager, demo script
```

## Quick start (Google Colab)

1. Copy this repository to Google Drive as `MyDrive/India-Space-Mission-Intelligence`.
2. Open `notebooks/01_fire_counts.ipynb` in Google Colab.
3. Add a free [FIRMS map key](https://firms.modaps.eosdis.nasa.gov/api/area/csv) as a Colab secret named `FIRMS_MAP_KEY` (key icon in the left sidebar).
4. Choose **Runtime → Run all**. Outputs go to `data/processed/` and `maps/`, and every dataset used is logged in `sources/source_register.csv`.

## Data and licences

| Data | Provider | Terms |
|---|---|---|
| VIIRS active fire detections | [NASA FIRMS](https://www.earthdata.nasa.gov/faq/firms-faq) | NASA open data policy; cite per the FIRMS citation policy |
| Sentinel-2 L2A imagery | [Copernicus Data Space Ecosystem](https://dataspace.copernicus.eu/) | Free and open; credit "Contains modified Copernicus Sentinel data [year]" ([licence](https://ads.atmosphere.copernicus.eu/licences/ec-sentinel)) |
| District boundaries | [geoBoundaries via HDX](https://data.humdata.org/m/dataset/geoboundaries-admin-boundaries-for-india) | ODbL |
| Cropland mask | [ESA WorldCover 2021](https://registry.opendata.aws/esa-worldcover-vito/index.html) | CC BY 4.0 |

Access dates and preprocessing steps are in `sources/source_register.csv`, and context sources are in `sources/references.md`. Raw downloads are not committed, because of their size and their licence terms.

## Evidence rules

These come from the project brief:
- Every factual record carries a source URL and an access date.
- Reported facts, our calculations and our recommendations are labelled separately.
- Missing values stay blank or are marked "not found". They are never guessed.
- Raw data is never edited; scripts produce the processed outputs.
- Coordinate systems, units, dates, nulls and duplicates are checked.

## Known limitations

- A fire detection is a 375 m pixel that contained fire at the moment the satellite passed. It is not a field, and counts are not burnt area.
- Optical imagery misses burns under cloud or smoke, and burn scars can vanish once fields are tilled.
- Reference labels come from interpreting imagery, not from field visits.
- Health impacts are context only; this project does not measure them.

## Timeline

| Week | Dates (2026) | Focus |
|---|---|---|
| 1 | 17–23 Oct | Set-up, fire counts, district choice, datasets A and B, problem statement |
| 2 | 24–30 Oct | Sentinel-2 burnt-area mapping, validation, maps, mission trade-off |
| 3 | 31 Oct–6 Nov | ML classifier, forecast, 2021 comparison, dashboard v1 |
| 4 | 7–13 Nov | Product concept, report, one-pager, demo |

## Author

**Mohit Sharma** ([@Panther2010](https://github.com/Panther2010)). The code licence will be added before the first release. Data keep their original licences.
