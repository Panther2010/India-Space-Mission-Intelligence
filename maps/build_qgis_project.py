"""Build the QGIS project and the export-ready maps for the 2025 Sangrur burnt-area analysis.

How to run it
- In QGIS (3.34 or later, including 4.x): Plugins > Python Console > Show Editor > Open Script > choose this
  file > Run Script.
- Outside QGIS, with QGIS's own Python (for example `python-qgis` in the OSGeo4W Shell on Windows):
  python maps/build_qgis_project.py

What it does
1. Reads Notebook 02's outputs in data/processed/ (burn map, 1 km grid, fire detections, label sheet, summary).
2. Writes the district and state outlines to data/processed/ if they are missing, from the geoBoundaries files
   that Notebook 01 downloads to data/raw/boundaries/.
3. Saves maps/burnt_area.qgz, with paths relative to the project file, so the project opens from any copy of
   the repository. QGIS 3.x refuses projects saved by QGIS 4, so the committed project is saved with QGIS 3.44:
   it opens in 3.44 and in 4.x.
4. Exports each print layout to maps/qgis/ as a 300 dpi PNG and a PDF.

It only reads and writes files inside the project folder and never touches the project open in QGIS.
"""
import csv
import datetime as dt
import os
import sys
import unicodedata
from pathlib import Path

from qgis.core import (Qgis, QgsApplication, QgsCategorizedSymbolRenderer, QgsColorRampShader,
                       QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsFeature, QgsField, QgsFillSymbol,
                       QgsGeometry, QgsGraduatedSymbolRenderer, QgsInvertedPolygonRenderer,
                       QgsLayoutExporter, QgsLayoutItemLabel, QgsLayoutItemLegend, QgsLayoutItemMap,
                       QgsLayoutItemPage, QgsLayoutItemPicture, QgsLayoutItemScaleBar, QgsLayoutPoint,
                       QgsLayoutSize, QgsLegendRenderer, QgsLegendStyle, QgsMapLayerLegendUtils, QgsMarkerSymbol,
                       QgsPalettedRasterRenderer, QgsPrintLayout, QgsProject, QgsRasterLayer, QgsRasterRange,
                       QgsRasterShader, QgsRectangle, QgsReferencedRectangle, QgsRendererCategory, QgsRendererRange,
                       QgsRuleBasedRenderer,
                       QgsSingleBandPseudoColorRenderer, QgsSingleSymbolRenderer, QgsTextFormat, QgsVectorFileWriter,
                       QgsVectorLayer)
from qgis.PyQt.QtCore import QMetaType, Qt
from qgis.PyQt.QtGui import QColor, QFont

# --- Settings -----------------------------------------------------------------------------------------------
SUFFIX = 'sangrur_2025'
DISTRICT = 'Sangrur'
STATE = 'Punjab'
STATE_BBOX = (73.8, 29.5, 77.0, 32.6)      # lon/lat box used to pick the right polygon if a name repeats
MAP_CRS = 'EPSG:32643'                      # WGS 84 / UTM zone 43N, as in Notebook 02
FONT = 'Arial'
AUTHOR = 'Mohit Sharma'
DPI = 300

# Classes of the burn map (band 1 of s2_burn_classes_*.tif), as written by Notebook 02.
CLASSES = [(1, '#e3e3e3', 'Not a harvested crop'),
           (2, '#9ecae1', 'Harvested, not burnt'),
           (3, '#fdae61', 'Burnt, flagged by VIIRS (375 m)'),
           (4, '#b2182b', 'Burnt, missed by VIIRS'),
           (5, '#8073ac', 'Burnt from 19 Nov, unconfirmed')]
# Burn timing per pixel (band 2: first 5-day window with a burn scar; window 1 starts on 5 Sep 2025). This layer is
# in the project for exploring; the layout maps the average window per 1 km square instead, which reads better.
TIMING = [(10, '#fed976', 'Before 25 Oct'),
          (12, '#fd8d3c', '25 Oct to 3 Nov'),
          (13, '#e31a1c', '4 to 8 Nov'),
          (15, '#800026', '9 to 18 Nov'),
          (18, '#8073ac', '19 Nov to 3 Dec, unconfirmed')]
# Average burn window of the confirmed burns in each 1 km square (grid field mean_burn_window_start).
TIMING_GRID = [('"burnt_ha" < 2', '#ececec', 'Under 2 ha burnt'),
               ('"burnt_ha" >= 2 AND "mean_burn_window_start" < \'2025-10-30\'', '#ffffb2', '25 Oct or earlier'),
               ('"burnt_ha" >= 2 AND "mean_burn_window_start" = \'2025-10-30\'', '#fecc5c', '30 Oct to 3 Nov'),
               ('"burnt_ha" >= 2 AND "mean_burn_window_start" = \'2025-11-04\'', '#fd8d3c', '4 to 8 Nov'),
               ('"burnt_ha" >= 2 AND "mean_burn_window_start" >= \'2025-11-09\'', '#e31a1c', '9 Nov or later')]
# Burnt area missed by VIIRS, as a share of each 1 km square (the square's hectares are its per cent).
MISSED = [(0, 5, '#fee5d9', 'Under 5%'), (5, 10, '#fcae91', '5 to 10%'), (10, 20, '#fb6a4a', '10 to 20%'),
          (20, 30, '#de2d26', '20 to 30%'), (30, 101, '#a50f15', '30% or more')]
LABEL_COLOURS = [('yes', '#b2182b', 'Burnt (yes)'), ('no', '#2166ac', 'Not burnt (no)'),
                 ('unsure', '#7f7f7f', 'Unsure')]


# --- Small helpers that work in QGIS 3.34+ and 4.x ---------------------------------------------------------------
def enum(*candidates):
    # First attribute path that exists, e.g. enum('Qgis.LayoutUnit.Millimeters', 'QgsUnitTypes.LayoutMillimeters').
    for path in candidates:
        obj = globals().get(path.split('.')[0])
        try:
            for part in path.split('.')[1:]:
                obj = getattr(obj, part)
            return obj
        except AttributeError:
            continue
    raise AttributeError(f'None of {candidates} exists in this QGIS version.')


MM = enum('Qgis.LayoutUnit.Millimeters', 'QgsUnitTypes.LayoutMillimeters')
POINTS = enum('Qgis.RenderUnit.Points', 'QgsUnitTypes.RenderPoints')
KM = enum('Qgis.DistanceUnit.Kilometers', 'QgsUnitTypes.DistanceKilometers')
PORTRAIT = enum('QgsLayoutItemPage.Orientation.Portrait', 'QgsLayoutItemPage.Portrait')
HIDDEN = enum('QgsLegendStyle.Style.Hidden', 'QgsLegendStyle.Hidden')
DISCRETE = enum('QgsColorRampShader.Type.Discrete', 'QgsColorRampShader.Discrete')
ALIGN_LEFT = Qt.AlignmentFlag.AlignLeft
SUCCESS = enum('QgsLayoutExporter.ExportResult.Success', 'QgsLayoutExporter.Success')
WRITER_OK = enum('QgsVectorFileWriter.WriterError.NoError', 'QgsVectorFileWriter.NoError')
try:                                        # field types: QMetaType in QGIS 3.38+ and 4.x, QVariant before
    TEXT = QMetaType.Type.QString
    QgsField('test', TEXT)
except TypeError:
    from qgis.PyQt.QtCore import QVariant
    TEXT = QVariant.String


def find_root():
    if os.environ.get('PROJECT_DIR'):
        return Path(os.environ['PROJECT_DIR']).resolve()
    starts = []
    if '__file__' in globals():
        starts.append(Path(__file__).resolve().parent)
    starts.append(Path.cwd().resolve())
    for start in starts:
        for folder in (start, *start.parents):
            if (folder / 'requirements.txt').exists() and (folder / 'notebooks').is_dir():
                return folder
    raise RuntimeError('Could not find the project folder. Set PROJECT_DIR, or run this file from the repository.')


def plain_name(name):
    return unicodedata.normalize('NFKD', str(name)).encode('ascii', 'ignore').decode('ascii').strip().lower()


def text_format(size, bold=False, colour='#000000'):
    fmt = QgsTextFormat()
    font = QFont(FONT)
    font.setBold(bold)
    fmt.setFont(font)
    fmt.setSize(size)
    fmt.setSizeUnit(POINTS)
    fmt.setColor(QColor(colour))
    return fmt


def read_summary(path):
    with open(path, newline='', encoding='utf-8') as f:
        return {row['metric']: row['value'] for row in csv.DictReader(f)}


# --- Boundaries ------------------------------------------------------------------------------------------------
def write_outline(geometry, attributes, path, crs):
    layer = QgsVectorLayer(f'MultiPolygon?crs={crs.authid()}', path.stem, 'memory')
    provider = layer.dataProvider()
    provider.addAttributes([QgsField(k, TEXT) for k in attributes])
    layer.updateFields()
    feature = QgsFeature(layer.fields())
    feature.setGeometry(geometry)
    for k, v in attributes.items():
        feature[k] = v
    provider.addFeature(feature)
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = 'GeoJSON'
    options.layerOptions = ['COORDINATE_PRECISION=5', 'RFC7946=YES']
    error = QgsVectorFileWriter.writeAsVectorFormatV3(layer, str(path), QgsProject.instance().transformContext(),
                                                      options)
    if error[0] != WRITER_OK:
        raise RuntimeError(f'Could not write {path}: {error}')


def pick(path, name, simplify=None):
    layer = QgsVectorLayer(str(path), path.stem, 'ogr')
    if not layer.isValid():
        raise RuntimeError(f'{path} is missing or unreadable. Run Notebook 01 first: it downloads the boundaries.')
    box = QgsGeometry.fromRect(QgsRectangle(*STATE_BBOX))
    matches = [f for f in layer.getFeatures() if plain_name(f['shapeName']) == plain_name(name)]
    if len(matches) > 1:
        matches = [f for f in matches if f.geometry().intersects(box)]
    if len(matches) != 1:
        raise RuntimeError(f'Expected one {name} polygon in {path.name}, found {len(matches)}.')
    geometry = matches[0].geometry().makeValid()
    if simplify:
        geometry = geometry.simplify(simplify)
    return geometry, layer.crs()


def ensure_outlines(processed, raw):
    district_path = processed / 'boundary_sangrur_pre2021.geojson'
    state_path = processed / 'boundary_punjab.geojson'
    if not district_path.exists():
        geometry, crs = pick(raw / 'geoBoundaries-IND-ADM2.geojson', DISTRICT)
        write_outline(geometry, {'name': 'Sangrur (pre-2021 boundary, includes Malerkotla)',
                                 'source': 'geoBoundaries IND ADM2 (Pathways Data, lgdirectory.gov.in)',
                                 'licence': 'ODbL 1.0'}, district_path, crs)
        print(f'Wrote {district_path.name}')
    if not state_path.exists():
        geometry, crs = pick(raw / 'geoBoundaries-IND-ADM1.geojson', STATE, simplify=0.002)
        write_outline(geometry, {'name': 'Punjab', 'source': 'geoBoundaries IND ADM1 (DataMeet, ECI), simplified',
                                 'licence': 'CC BY 2.5 IN'}, state_path, crs)
        print(f'Wrote {state_path.name}')
    return district_path, state_path


# --- Layers ----------------------------------------------------------------------------------------------------
def outline_layer(path, name, colour='#252525', width=0.35):
    layer = QgsVectorLayer(str(path), name, 'ogr')
    layer.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple(
        {'style': 'no', 'outline_color': colour, 'outline_width': str(width)})))
    return layer


def mask_layer(path):
    # White everywhere outside the district, to trim the 1 km squares that cross its edge.
    layer = QgsVectorLayer(str(path), 'Outside the district (mask)', 'ogr')
    inner = QgsSingleSymbolRenderer(QgsFillSymbol.createSimple({'color': '#ffffff', 'outline_style': 'no'}))
    layer.setRenderer(QgsInvertedPolygonRenderer(inner))
    return layer


def burn_map_layer(path, name, band=1, colours=None):
    layer = QgsRasterLayer(str(path), name)
    classes = [QgsPalettedRasterRenderer.Class(v, QColor(colours[v] if colours else c), label)
               for v, c, label in CLASSES]
    layer.setRenderer(QgsPalettedRasterRenderer(layer.dataProvider(), band, classes))
    return layer


def timing_layer(path):
    layer = QgsRasterLayer(str(path), 'When the burn was first seen')
    layer.dataProvider().setUserNoDataValue(2, [QgsRasterRange(0, 0)])   # 0 = never burnt
    ramp = QgsColorRampShader()
    ramp.setColorRampType(DISCRETE)
    ramp.setColorRampItemList([QgsColorRampShader.ColorRampItem(v, QColor(c), label) for v, c, label in TIMING])
    shader = QgsRasterShader()
    shader.setRasterShaderFunction(ramp)
    layer.setRenderer(QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 2, shader))
    return layer


def grid_layer(path):
    layer = QgsVectorLayer(str(path), 'Burnt and missed by VIIRS, share of each 1 km square', 'ogr')
    ranges = [QgsRendererRange(lo, hi, QgsFillSymbol.createSimple({'color': c, 'outline_style': 'no'}), label)
              for lo, hi, c, label in MISSED]
    layer.setRenderer(QgsGraduatedSymbolRenderer('burnt_missed_ha', ranges))
    return layer


def timing_grid_layer(path):
    layer = QgsVectorLayer(str(path), 'Average burn window, 1 km squares', 'ogr')
    root = QgsRuleBasedRenderer.Rule(None)
    for expression, colour, label in TIMING_GRID:
        symbol = QgsFillSymbol.createSimple({'color': colour, 'outline_style': 'no'})
        root.appendChild(QgsRuleBasedRenderer.Rule(symbol, filterExp=expression, label=label))
    layer.setRenderer(QgsRuleBasedRenderer(root))
    return layer


def points_layer(path, name, x, y, subset=None):
    uri = f'{path.as_uri()}?type=csv&delimiter=,&xField={x}&yField={y}&crs=EPSG:4326&detectTypes=yes'
    layer = QgsVectorLayer(uri, name, 'delimitedtext')
    if subset:
        layer.setSubsetString(subset)
    return layer


def style_detections(layer):
    layer.setRenderer(QgsSingleSymbolRenderer(QgsMarkerSymbol.createSimple(
        {'name': 'circle', 'color': '#000000', 'size': '0.7', 'outline_style': 'no'})))
    layer.setOpacity(0.75)


def style_labels(layer):
    categories = [QgsRendererCategory(v, QgsMarkerSymbol.createSimple(
        {'name': 'circle', 'color': c, 'size': '2.2', 'outline_color': '#ffffff', 'outline_width': '0.3'}), label)
        for v, c, label in LABEL_COLOURS]
    layer.setRenderer(QgsCategorizedSymbolRenderer('burnt', categories))


# --- Layouts ---------------------------------------------------------------------------------------------------
def add_label(layout, text, x, y, w, h, fmt):
    item = QgsLayoutItemLabel(layout)
    item.setText(text)
    item.setTextFormat(fmt)
    item.setHAlign(ALIGN_LEFT)
    layout.addLayoutItem(item)
    item.attemptMove(QgsLayoutPoint(x, y, MM))
    item.attemptResize(QgsLayoutSize(w, h, MM))
    return item


def add_map(layout, layers, extent, crs, x, y, w, h, frame=True):
    item = QgsLayoutItemMap(layout)
    # Start smaller than the target: attemptResize() ignores a size equal to the current one, and then the
    # project file would record the map as 0 x 0 mm.
    item.setRect(0, 0, 10, 10)
    layout.addLayoutItem(item)
    item.attemptMove(QgsLayoutPoint(x, y, MM))
    item.attemptResize(QgsLayoutSize(w, h, MM))
    item.setCrs(crs)
    item.setLayers(layers)
    item.setKeepLayerSet(True)
    item.zoomToExtent(extent)
    item.setFrameEnabled(frame)
    return item


def add_legend(layout, linked_map, entries, x, y, columns=1):
    legend = QgsLayoutItemLegend(layout)
    legend.setTitle('')
    legend.setLinkedMap(linked_map)
    if hasattr(legend, 'setSyncMode'):
        legend.setSyncMode(enum('Qgis.LegendSyncMode.Manual'))
    else:
        legend.setAutoUpdateModel(False)
    model = legend.model()
    root = model.rootGroup()
    root.clear()
    for layer, title in entries:
        node = root.addLayer(layer)
        if title is None:
            QgsLegendRenderer.setNodeLegendStyle(node, HIDDEN)
        else:
            node.setCustomProperty('legend/title-label', title)
        nodes = model.layerLegendNodes(node)
        keep = [i for i, n in enumerate(nodes)
                if not str(n.data(Qt.ItemDataRole.DisplayRole) or '').startswith('Band ')]
        if len(keep) < len(nodes):
            QgsMapLayerLegendUtils.setLegendNodeOrder(node, keep)
            model.refreshLayerLegend(node)
    legend.setColumnCount(columns)
    legend.setSplitLayer(True)
    for style, size, bold in ((enum('QgsLegendStyle.Style.Subgroup', 'QgsLegendStyle.Subgroup'), 9, True),
                              (enum('QgsLegendStyle.Style.SymbolLabel', 'QgsLegendStyle.SymbolLabel'), 8.5, False)):
        legend.rstyle(style).setTextFormat(text_format(size, bold))
    legend.setSymbolHeight(4)
    legend.setSymbolWidth(6)
    legend.setFrameEnabled(False)
    layout.addLayoutItem(legend)
    legend.attemptMove(QgsLayoutPoint(x, y, MM))
    legend.adjustBoxSize()
    legend.refresh()
    return legend


def add_scale_bar(layout, linked_map, x, y):
    bar = QgsLayoutItemScaleBar(layout)
    bar.setStyle('Single Box')
    bar.setLinkedMap(linked_map)
    bar.setUnits(KM)
    bar.setUnitLabel('km')
    bar.setNumberOfSegmentsLeft(0)
    bar.setNumberOfSegments(4)
    bar.setUnitsPerSegment(5)
    bar.setHeight(2)
    bar.setTextFormat(text_format(8))
    layout.addLayoutItem(bar)
    bar.attemptMove(QgsLayoutPoint(x, y, MM))
    bar.update()
    return bar


def add_north_arrow(layout, linked_map, x, y):
    arrow = QgsLayoutItemPicture(layout)
    svg = next((Path(p) / 'arrows' / 'NorthArrow_02.svg' for p in QgsApplication.svgPaths()
                if (Path(p) / 'arrows' / 'NorthArrow_02.svg').exists()), None)
    if svg is None:
        return None
    arrow.setPicturePath(str(svg))
    arrow.setLinkedMap(linked_map)
    layout.addLayoutItem(arrow)
    arrow.attemptMove(QgsLayoutPoint(x, y, MM))
    arrow.attemptResize(QgsLayoutSize(9, 14, MM))
    return arrow


def new_layout(project, name):
    for old in [lay for lay in project.layoutManager().printLayouts() if lay.name() == name]:
        project.layoutManager().removeLayout(old)
    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName(name)
    layout.pageCollection().page(0).setPageSize('A4', PORTRAIT)
    project.layoutManager().addLayout(layout)
    return layout


# --- Build -----------------------------------------------------------------------------------------------------
def build():
    root = find_root()
    processed, maps_dir = root / 'data' / 'processed', root / 'maps'
    out_dir = maps_dir / 'qgis'
    out_dir.mkdir(parents=True, exist_ok=True)
    classes_tif = processed / f's2_burn_classes_{SUFFIX}.tif'
    grid_path = processed / f's2_burn_grid_1km_{SUFFIX}.geojson'
    detections_path = processed / f'firms_detections_{SUFFIX}.csv'
    labels_path = processed / f'validation_labels_{SUFFIX}.csv'
    summary_path = processed / f's2_burn_summary_{SUFFIX}.csv'
    accuracy_path = processed / f'validation_accuracy_{SUFFIX}.csv'
    for needed in (classes_tif, grid_path, detections_path, summary_path):
        if not needed.exists():
            raise RuntimeError(f'{needed} is missing: run Notebook 02 for the whole district first.')
    district_path, state_path = ensure_outlines(processed, root / 'data' / 'raw' / 'boundaries')

    project = QgsProject()
    project_file = maps_dir / 'burnt_area.qgz'
    project.setFileName(str(project_file))
    project.writeEntryBool('Paths', '/Absolute', False)
    map_crs = QgsCoordinateReferenceSystem(MAP_CRS)
    project.setCrs(map_crs)
    project.setTitle('Paddy-residue burnt area, Sangrur district, 2025 season')

    burnt = burn_map_layer(classes_tif, 'Burnt area, 2025 season')
    grey = {1: '#f2f2f2', 2: '#d9d9d9', 3: '#d9d9d9', 4: '#d9d9d9', 5: '#d9d9d9'}
    background = burn_map_layer(classes_tif, 'Background: fields harvested in the season', colours=grey)
    timing = timing_layer(classes_tif)
    grid = grid_layer(grid_path)
    timing_grid = timing_grid_layer(grid_path)
    detections = points_layer(detections_path, 'VIIRS fire detections', 'longitude', 'latitude',
                              subset="\"sensor\" LIKE 'VIIRS%' AND lower(to_string(\"inside\")) = 'true'")
    style_detections(detections)
    district = outline_layer(district_path, 'District boundary')
    mask = mask_layer(district_path)
    state = QgsVectorLayer(str(state_path), 'Punjab', 'ogr')
    state.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple(
        {'color': '#f0f0f0', 'outline_color': '#737373', 'outline_width': '0.25'})))
    district_fill = QgsVectorLayer(str(district_path), 'Sangrur (inset)', 'ogr')
    district_fill.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple(
        {'color': '#b2182b', 'outline_style': 'no'})))
    layers = [burnt, background, timing, grid, timing_grid, detections, district, mask, state, district_fill]
    labels = None
    if labels_path.exists():
        labels = points_layer(labels_path, 'Validation points', 'lon', 'lat')
        style_labels(labels)
        layers.append(labels)
    for layer in layers:
        if not layer.isValid():
            raise RuntimeError(f'Layer "{layer.name()}" did not load from {layer.source()}')
    # Layer panel: one group per map, so the canvas isn't a stack of everything. The layouts keep their own
    # layer sets, so which groups are ticked doesn't change the exported maps.
    tree = project.layerTreeRoot()
    groups = [('Context', True, [district]),
              ('Map 1: burnt area', True, [burnt]),
              ('Map 2: missed by VIIRS', False, [detections, mask, grid]),
              ('Map 3: burn timing', False, [timing_grid, timing, background]),
              ('Appendix: validation points', False, [labels] if labels is not None else []),
              ('Inset', False, [district_fill, state])]
    for group_name, visible, members in groups:
        if not members:
            continue
        group = tree.addGroup(group_name)
        for layer in members:
            project.addMapLayer(layer, False)
            group.addLayer(layer)
        group.setItemVisibilityChecked(visible)
        group.setExpanded(visible)

    # Map extent: the burn map's extent (UTM 43N) plus a small margin; inset: Punjab.
    extent = burnt.extent()
    extent.grow(2500)
    # A project saved without QGIS's window has no map view, so QGIS would open it on an empty view. Store the
    # district as the view to open on and as the extent of View > Zoom Full.
    view = project.viewSettings()
    view.setDefaultViewExtent(QgsReferencedRectangle(extent, map_crs))
    if hasattr(view, 'setPresetFullExtent'):
        view.setPresetFullExtent(QgsReferencedRectangle(extent, map_crs))
    state_extent = QgsCoordinateTransform(state.crs(), map_crs, project).transformBoundingBox(state.extent())
    state_extent.grow(8000)

    s = read_summary(summary_path)
    burnt_ha, late_ha = float(s['burnt_ha']), float(s['burnt_unconfirmed_ha'])
    share_burnt, missed = float(s['burnt_share_of_harvested']), float(s['missed_share_viirs_375m'])
    accuracy_note = ''
    if accuracy_path.exists():
        with open(accuracy_path, newline='', encoding='utf-8') as f:
            rows = [r for r in csv.DictReader(f) if r['rule'].startswith('map as reported')
                    and r['scored_on'] == 'all labelled points']
        if rows:
            accuracy_note = (f' Checked against {rows[0]["points"]} labelled points: F1 {float(rows[0]["f1"]):.2f}, '
                             f'overall accuracy {float(rows[0]["overall_accuracy"]):.2f}.')
    today = dt.date.today().strftime('%d %b %Y').lstrip('0')
    credits = ('Contains modified Copernicus Sentinel data 2025. Fire detections: NASA FIRMS (VIIRS 375 m). '
               'District boundary: geoBoundaries (ODbL 1.0); state boundary: geoBoundaries, from DataMeet and the '
               'Election Commission of India (CC BY 2.5 IN). Coordinate reference system: WGS 84 / UTM zone 43N '
               f'(EPSG:32643). Map: {AUTHOR}, {today}.')
    method = ('Method: 5-day Sentinel-2 composites at 20 m. A field that turned green and was then harvested counts '
              'as burnt in the first window with NBR ≤ −0.05, MIRBI ≥ 1.65 and NIR ≤ 0.13.'
              + accuracy_note)

    def page(name, title, subtitle, main_layers, legend_entries, note, legend_columns=2):
        layout = new_layout(project, name)
        add_label(layout, title, 12, 9, 186, 10, text_format(17, bold=True))
        add_label(layout, subtitle, 12, 19, 186, 11, text_format(9.5, colour='#404040'))
        main = add_map(layout, main_layers, extent, map_crs, 12, 31, 186, 188)
        inset = add_map(layout, [district_fill, state], state_extent, map_crs, 156, 33, 40, 40)
        inset.setBackgroundColor(QColor('#ffffff'))
        add_label(layout, 'Sangrur (red) in Punjab', 156, 74, 40, 5, text_format(7, colour='#404040'))
        add_north_arrow(layout, main, 17, 35)
        add_scale_bar(layout, main, 15, 208)
        add_label(layout, note, 12, 221, 186, 10, text_format(9))
        add_legend(layout, main, legend_entries, 11, 232, columns=legend_columns)
        add_label(layout, method + '\n' + credits, 12, 273, 186, 18, text_format(6.5, colour='#404040'))
        return layout

    layouts = [
        ('01_burnt_area_2025', page(
            '01 Burnt area, 2025',
            'Paddy-residue burning in Sangrur, 2025 season',
            'Burnt area mapped from Sentinel-2, 5 Sep to 4 Dec 2025, and whether a VIIRS fire detection fell within '
            '375 m around the time of the burn',
            [district, burnt],
            [(burnt, None), (district, 'District boundary (pre-2021, includes Malerkotla)')],
            f'Confirmed burnt area: {burnt_ha:,.0f} ha, {share_burnt:.1%} of the area harvested in the season. '
            f'{missed:.1%} of it had no VIIRS fire detection within 375 m. Another {late_ha:,.0f} ha first seen '
            'from 19 Nov are unconfirmed.')),
        ('02_missed_by_viirs_1km', page(
            '02 Missed by VIIRS, 1 km squares',
            'Where burning went unseen by fire counts',
            'Burnt area with no VIIRS fire detection within 375 m, as a share of each 1 km square '
            '(confirmed burns, 2025 season), with the VIIRS detections in the district',
            [district, mask, detections, grid],
            [(grid, 'Burnt and missed by VIIRS, % of each 1 km square'), (detections, None),
             (district, 'District boundary')],
            f'{missed:.1%} of the confirmed burnt area ({burnt_ha:,.0f} ha) had no VIIRS detection within 375 m. '
            'The dots are the VIIRS detections that fell inside the district.')),
        ('03_burn_timing', page(
            '03 Burn timing',
            'When fields burned',
            'Average 5-day window in which the confirmed burns of each 1 km square were first seen, 2025 season',
            [district, mask, timing_grid],
            [(timing_grid, 'Average burn window'), (district, 'District boundary')],
            'Burning peaked in the window starting 4 Nov. Burns first seen from 19 Nov are unconfirmed and left out; '
            'the project file also has the burn window of every 20 m pixel.')),
    ]
    if labels is not None:
        counts = {k: 0 for k, _, _ in LABEL_COLOURS}
        with open(labels_path, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                key = row['burnt'].strip().lower()
                counts[key] = counts.get(key, 0) + 1
        layouts.append(('A1_validation_points', page(
            'A1 Validation points',
            'Validation points',
            f'{sum(counts.values())} points drawn at random by mapped class and labelled blind from single-date '
            'Sentinel-2 images at 10 m',
            [district, labels, background],
            [(labels, None), (district, 'District boundary')],
            f'Labels: {counts["yes"]} burnt, {counts["no"]} not burnt, {counts["unsure"]} unsure. Each point was read '
            'twice, by the author and by an AI assistant.', legend_columns=2)))

    for stem, layout in layouts:
        exporter = QgsLayoutExporter(layout)
        image = QgsLayoutExporter.ImageExportSettings()
        image.dpi = DPI
        pdf = QgsLayoutExporter.PdfExportSettings()
        pdf.dpi = DPI
        for result, path in ((exporter.exportToImage(str(out_dir / f'{stem}.png'), image), f'{stem}.png'),
                             (exporter.exportToPdf(str(out_dir / f'{stem}.pdf'), pdf), f'{stem}.pdf')):
            if result != SUCCESS:
                raise RuntimeError(f'Export of {path} failed ({result}).')
        print(f'Exported maps/qgis/{stem}.png and .pdf')
    if not project.write(str(project_file)):
        raise RuntimeError(f'Could not save {project_file}: {project.error()}')
    print(f'Saved {project_file.relative_to(root)} with QGIS {Qgis.version()}. Open it with Project > Open.')
    if Qgis.versionInt() >= 40000:
        print('Note: QGIS 3.x cannot open a project saved by QGIS 4. The committed project is saved with QGIS 3.44 '
              'so that it opens in both; commit a rebuilt burnt_area.qgz only if everyone uses QGIS 4.')


_app = None
if QgsApplication.instance() is None:       # outside QGIS: start a headless QGIS application
    if sys.platform.startswith('linux') and not os.environ.get('DISPLAY'):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    QgsApplication.setPrefixPath(os.environ.get('QGIS_PREFIX_PATH', sys.prefix), True)
    _app = QgsApplication([], False)
    _app.initQgis()
try:
    build()
finally:
    if _app is not None:
        _app.exitQgis()
