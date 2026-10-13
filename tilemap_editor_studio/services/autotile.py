"""Wang / blob-47 autotiling. Bitmask from 8 neighbours → tile index via table."""
from __future__ import annotations

from collections.abc import Callable

import numpy as np

from tilemap_editor_studio.models.tilemap import EMPTY_TILE, TileLayer

# Neighbour bit order: N, NE, E, SE, S, SW, W, NW
_NEIGHBOURS = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]


def neighbour_mask(layer: TileLayer, x: int, y: int, filled: int) -> int:
    mask = 0
    for bit, (dx, dy) in enumerate(_NEIGHBOURS):
        nx, ny = x + dx, y + dy
        if 0 <= nx < layer.width and 0 <= ny < layer.height:
            if layer.get(nx, ny) != EMPTY_TILE:
                mask |= 1 << bit
    return mask


def apply_wang_autotile(
    layer: TileLayer,
    table: dict[int, int],
    is_filled: Callable[[int], bool] | None = None,
) -> int:
    """Recompute every non-empty tile's id from its 8-neighbour mask.

    Returns count of tiles changed. `is_filled` defaults to "not empty".
    """
    filled = is_filled or (lambda tid: tid != EMPTY_TILE)
    changed = 0
    snapshot = layer.data.copy()
    ys, xs = np.where(snapshot != EMPTY_TILE)
    for y, x in zip(ys.tolist(), xs.tolist()):
        mask = neighbour_mask(layer, x, y, filled(snapshot[y, x]))
        new_id = table.get(mask, snapshot[y, x])
        if new_id != snapshot[y, x]:
            layer.data[y, x] = new_id
            changed += 1
    return changed