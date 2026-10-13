"""TileMap — the document model. Grid of tile indices, layers, tileset refs."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

import numpy as np

EMPTY_TILE = -1


@dataclass(slots=True)
class TileLayer:
    name: str
    width: int
    height: int
    data: np.ndarray  # shape (height, width), dtype int32; -1 = empty
    visible: bool = True
    opacity: float = 1.0

    @classmethod
    def blank(cls, name: str, width: int, height: int) -> "TileLayer":
        return cls(name=name, width=width, height=height,
                   data=np.full((height, width), EMPTY_TILE, dtype=np.int32))

    def set(self, x: int, y: int, tile_id: int) -> None:
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError(f"({x},{y}) outside layer {self.name} {self.width}x{self.height}")
        self.data[y, x] = tile_id

    def get(self, x: int, y: int) -> int:
        return int(self.data[y, x])


@dataclass(slots=True)
class TileMap:
    size: tuple[int, int]  # (width, height) in tiles
    tile_size: int = 16
    layers: list[TileLayer] = field(default_factory=list)
    tilesets: list[str] = field(default_factory=list)
    properties: dict[str, str] = field(default_factory=dict)
    source_path: Path | None = None

    def add_layer(self, name: str, *, index: int | None = None) -> TileLayer:
        layer = TileLayer.blank(name, *self.size)
        if index is None:
            self.layers.append(layer)
        else:
            self.layers.insert(index, layer)
        return layer

    def layer(self, name: str) -> TileLayer:
        for layer in self.layers:
            if layer.name == name:
                return layer
        raise KeyError(name)

    def iter_tiles(self) -> Iterator[tuple[int, int, int, int]]:
        """Yields (layer_index, x, y, tile_id) for non-empty tiles only."""
        for li, layer in enumerate(self.layers):
            ys, xs = np.where(layer.data != EMPTY_TILE)
            for y, x in zip(ys.tolist(), xs.tolist()):
                yield li, x, y, layer.get(x, y)