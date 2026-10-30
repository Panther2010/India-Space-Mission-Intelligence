# Maps

- `notebook01/`: charts and district maps written by Notebook 01.
- `notebook02/`: study area, pilot and cloud-mask checks, burnt-area map, timeline, missed share and burn-rule diagnostic, written by Notebook 02. These are working charts; the export-ready maps come from QGIS.
- `burnt_area.qgz`: the QGIS project. Its paths are relative, so it opens from any copy of the repository. It is saved with QGIS 3.44, so it opens in QGIS 3.44 and in 4.x: QGIS 3 refuses projects saved by QGIS 4. The layer panel has one group per map, with only the burnt-area map ticked; each print layout keeps its own set of layers.
- `qgis/`: the export-ready maps, A4 portrait, as 300 dpi PNG and as PDF. Each has a legend, a scale bar, a north arrow, an inset of Punjab, its coordinate reference system, data credits and a one-line method note.
  - `01_burnt_area_2025`: burnt area, split by whether a VIIRS detection fell within 375 m, with the unconfirmed late burns
  - `02_missed_by_viirs_1km`: burnt area with no VIIRS detection, as a share of each 1 km square, with the VIIRS detections
  - `03_burn_timing`: the average burn window of each 1 km square
  - `A1_validation_points`: the 240 validation points and their labels
- `build_qgis_project.py`: builds the project and the maps from Notebook 02's outputs, so every map can be rebuilt after a rerun.

## Rebuilding the maps

In QGIS 3.34 or later (including 4.x): **Plugins → Python Console → Show Editor → Open Script**, choose `maps/build_qgis_project.py`, then **Run Script**. The script never touches the project open in QGIS. It writes the district and state outlines to `data/processed/` first, if they are missing, from the geoBoundaries files that Notebook 01 downloads.

Rebuilding replaces `burnt_area.qgz` and the files in `qgis/`. Make lasting style changes in the script, or save a project you have edited by hand under another name. A project rebuilt with QGIS 4 won't open in QGIS 3.x, so commit it only if everyone uses QGIS 4.
