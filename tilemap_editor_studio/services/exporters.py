"""Export pipeline: PNG render, Tiled .tmx, JSON for engine import."""
from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
from PIL import Image

from tilemap_editor_studio.models.tilemap import EMPTY_TILE, TileMap

log = logging.getLogger(__name__)


def export_png(tilemap: TileMap, tileset_image: Image.Image, out: Path) -> None:
    width, height = tilemap.size
    ts = tilemap.tile_size
    canvas = Image.new("RGBA", (width * ts, height * ts), (0, 0, 0, 0))
    cols = max(1, tileset_image.width // ts)
    for layer in tilemap.layers:
        if not layer.visible:
            continue
        ys, xs = np.where(layer.data != EMPTY_TILE)
        for y, x in zip(ys.tolist(), xs.tolist()):
            tid = layer.get(x, y)
            sx, sy = (tid % cols) * ts, (tid // cols) * ts
            tile = tileset_image.crop((sx, sy, sx + ts, sy + ts))
            canvas.alpha_composite(tile, (x * ts, y * ts))
    canvas.save(out)
    log.info("exported PNG %s", out.name)


def export_json(tilemap: TileMap, out: Path) -> None:
    payload = {
        "size": list(tilemap.size),
        "tileSize": tilemap.tile_size,
        "layers": [
            {"name": l.name, "data": l.data.flatten().tolist()} for l in tilemap.layers
        ],
    }
    out.write_text(json.dumps(payload), encoding="utf-8")
    log.info("exported JSON %s", out.name)