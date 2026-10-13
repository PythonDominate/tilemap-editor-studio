"""Read/write .tmap project files. JSON container, numpy arrays as base64 int32."""
from __future__ import annotations

import base64
import json
import logging
from pathlib import Path

import numpy as np

from tilemap_editor_studio.models.tilemap import TileLayer, TileMap

log = logging.getLogger(__name__)
FORMAT_VERSION = 3


def _encode_layer(layer: TileLayer) -> dict:
    return {
        "name": layer.name,
        "width": layer.width,
        "height": layer.height,
        "visible": layer.visible,
        "opacity": layer.opacity,
        "data_b64": base64.b64encode(layer.data.astype("<i4").tobytes()).decode("ascii"),
    }


def _decode_layer(blob: dict) -> TileLayer:
    raw = base64.b64decode(blob["data_b64"])
    arr = np.frombuffer(raw, dtype="<i4").reshape(blob["height"], blob["width"]).copy()
    return TileLayer(
        name=blob["name"], width=blob["width"], height=blob["height"],
        data=arr, visible=blob.get("visible", True), opacity=blob.get("opacity", 1.0),
    )


def save_project(tilemap: TileMap, path: Path) -> None:
    payload = {
        "format": "tmap",
        "version": FORMAT_VERSION,
        "size": list(tilemap.size),
        "tile_size": tilemap.tile_size,
        "tilesets": tilemap.tilesets,
        "properties": tilemap.properties,
        "layers": [_encode_layer(l) for l in tilemap.layers],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    log.info("saved %s (%d layers)", path.name, len(tilemap.layers))


def load_project(path: Path) -> TileMap:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("format") != "tmap":
        raise ValueError(f"{path.name}: not a tmap project")
    version = payload.get("version", 0)
    if version > FORMAT_VERSION:
        raise ValueError(f"{path.name}: format v{version} newer than host v{FORMAT_VERSION}")
    tilemap = TileMap(
        size=tuple(payload["size"]),
        tile_size=payload.get("tile_size", 16),
        tilesets=list(payload.get("tilesets", [])),
        properties=dict(payload.get("properties", {})),
        source_path=path,
    )
    tilemap.layers = [_decode_layer(b) for b in payload.get("layers", [])]
    return tilemap