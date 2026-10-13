"""Pixel <-> tile coordinate conversion for the editor canvas."""
from __future__ import annotations


def pixel_to_tile(px: int, py: int, tile_size: int, zoom: float = 1.0) -> tuple[int, int]:
    return int(px / (tile_size * zoom)), int(py / (tile_size * zoom))


def tile_to_pixel(tx: int, ty: int, tile_size: int, zoom: float = 1.0) -> tuple[int, int]:
    return int(tx * tile_size * zoom), int(ty * tile_size * zoom)


def snap_to_grid(value: float, step: int) -> int:
    return int(round(value / step) * step)
</｜｜DSML｜｜ parameter>
</｜｜DSML｜｜ invoke>
</｜｜DSML｜｜ calls>