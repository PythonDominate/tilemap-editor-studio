"""Tileset metadata — image path, tile size, margin/spacing, autotile hints."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class Tileset:
    name: str
    image_path: Path
    tile_size: int
    margin: int = 0
    spacing: int = 0
    columns: int = 0
    tile_count: int = 0
    autotile: str | None = None  # "wang" | "blob47" | None
    tags: dict[int, list[str]] = field(default_factory=dict)

    def tile_rect(self, tile_id: int) -> tuple[int, int, int, int]:
        """Pixel rect (x, y, w, h) of tile_id inside the tileset image."""
        cols = self.columns or 1
        col = tile_id % cols
        row = tile_id // cols
        x = self.margin + col * (self.tile_size + self.spacing)
        y = self.margin + row * (self.tile_size + self.spacing)
        return x, y, self.tile_size, self.tile_size