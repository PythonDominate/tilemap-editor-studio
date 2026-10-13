"""Shared contracts every plugin implements. Stable ABI for third-party extensions."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from tilemap_editor_studio.models.tilemap import TileMap


@dataclass(frozen=True, slots=True)
class PluginManifest:
    name: str
    version: str
    api_version: str
    author: str = "unknown"
    description: str = ""
    entry_point: str = ""
    capabilities: tuple[str, ...] = field(default_factory=tuple)


@runtime_checkable
class TilemapPlugin(Protocol):
    manifest: PluginManifest

    def on_load(self, host: Any) -> None: ...
    def on_unload(self) -> None: ...
    def validate(self, document: TileMap) -> list[str]: ...


class PluginBase(ABC):
    """Optional base class — plugins may implement the Protocol directly."""

    manifest: PluginManifest

    @abstractmethod
    def on_load(self, host: Any) -> None: ...

    def on_unload(self) -> None:
        return None

    def validate(self, document: TileMap) -> list[str]:
        return []


class PluginAPIError(RuntimeError):
    """Raised by the loader when a plugin violates the contract."""