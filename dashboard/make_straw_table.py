"""Write data/processed/straw_by_window_sangrur_2025.csv, the table behind the dashboard's straw-buyer view.

For each 1 km square of Notebook 02's grid and each 5-day window of the 2025 season, from the 20 m burn map
(data/processed/s2_burn_classes_sangrur_2025.tif):
- fresh_straw_ha: harvest first seen in this window or the one before (about the last 10 days), and not seen burnt by
  the end of this window. Fields that burned did so a median of 10 days after harvest, so this is straw a buyer could
  still reach. It may also have been baled, ploughed in or removed, which the map can't see.
- burnt_ha: first seen burnt in this window, confirmed (before 19 Nov).
- late_burnt_ha: first seen burnt in this window from 19 Nov, unconfirmed.

Each 1 km square is a block of 50 x 50 pixels from the map's corner, named rRRRcCCC as in the 1 km grid. Squares and
windows with nothing to report are left out. The script checks its window totals against Notebook 02's
s2_burn_by_window_sangrur_2025.csv. Needs rasterio (in the project's environment); downloads nothing.

Run from the project folder:  python dashboard/make_straw_table.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio

P = Path(__file__).resolve().parent.parent / 'data' / 'processed'
MAP, BY_WINDOW = P / 's2_burn_classes_sangrur_2025.tif', P / 's2_burn_by_window_sangrur_2025.csv'
OUT = P / 'straw_by_window_sangrur_2025.csv'
BLOCK, PIXEL_HA = 50, 0.04                 # 50 pixels of 20 m = 1 km; a 20 m pixel is 0.04 ha
FIRST_WINDOW = pd.Timestamp('2025-09-05')  # window 1; windows are numbered from 1 in the map, 0 = none


def per_square(mask):
    """Hectares of `mask` in each 1 km block."""
    rows, cols = -(-mask.shape[0] // BLOCK), -(-mask.shape[1] // BLOCK)
    padded = np.zeros((rows * BLOCK, cols * BLOCK), dtype=np.uint16)
    padded[:mask.shape[0], :mask.shape[1]] = mask
    return padded.reshape(rows, BLOCK, cols, BLOCK).sum(axis=(1, 3)) * PIXEL_HA


def main():
    with rasterio.open(MAP) as src:
        cls, burn, harvest = src.read(1), src.read(2), src.read(3)
    harvested_class = np.isin(cls, (2, 3, 4, 5))
    harvested = harvested_class & (harvest >= 1)
    windows = int(max(burn.max(), harvest.max()))
    tables = []
    for w in range(1, windows + 1):
        unburnt = (burn == 0) | (burn > w)
        layers = {
            'fresh_straw_ha': harvested & ((harvest == w) | (harvest == w - 1)) & unburnt,
            'burnt_ha': (burn == w) & np.isin(cls, (3, 4)),
            'late_burnt_ha': (burn == w) & (cls == 5),
        }
        sums = {name: per_square(mask) for name, mask in layers.items()}
        row, col = np.nonzero(sum(sums.values()) > 0)
        start = (FIRST_WINDOW + pd.to_timedelta(5 * (w - 1), unit='D')).strftime('%Y-%m-%d')
        table = pd.DataFrame({'cell': [f'r{r:03d}c{c:03d}' for r, c in zip(row, col)], 'window': w,
                              'window_start': start})
        for name, values in sums.items():
            table[name] = values[row, col].round(2)
        tables.append(table)
        # Check against Notebook 02's totals for the window.
        expected = pd.read_csv(BY_WINDOW).iloc[w - 1]
        harvested_here = (harvested & (harvest == w)).sum() * PIXEL_HA
        burnt_here = ((burn == w) & np.isin(cls, (3, 4, 5))).sum() * PIXEL_HA
        if abs(harvested_here - expected['harvested_ha']) > 0.5 or abs(burnt_here - expected['burnt_ha']) > 0.5:
            raise SystemExit(f'Window {w}: harvested {harvested_here:.1f} / burnt {burnt_here:.1f} ha, against '
                             f"Notebook 02's {expected['harvested_ha']:.1f} / {expected['burnt_ha']:.1f} ha.")
    out = pd.concat(tables, ignore_index=True)
    out.to_csv(OUT, index=False)
    print(f'{len(out):,} rows, {out["cell"].nunique():,} squares, {windows} windows; totals match Notebook 02.')
    print(out.groupby('window_start')[['fresh_straw_ha', 'burnt_ha', 'late_burnt_ha']].sum().round(0).to_string())
    print('Written to', OUT)


if __name__ == '__main__':
    main()
