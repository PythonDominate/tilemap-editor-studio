"""Registry of loaded plugins. Lookup by name, capability, or manifest."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from tilemap_editor_studio.models.tilemap import TileMap
from tilemap_editor_studio.plugins.contracts import PluginAPIError, TilemapPlugin

log = logging.getLogger(__name__)


@dataclass(slots=True)
class RegisteredPlugin:
    plugin: TilemapPlugin
    source: str


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, RegisteredPlugin] = {}

    def register(self, plugin: TilemapPlugin, source: str) -> None:
        name = plugin.manifest.name
        if name in self._plugins:
            raise PluginAPIError(f"duplicate plugin name: {name}")
        self._plugins[name] = RegisteredPlugin(plugin=plugin, source=source)
        log.info("registered plugin %s v%s (%s)", name, plugin.manifest.version, source)

    def get(self, name: str) -> TilemapPlugin:
        return self._plugins[name].plugin

    def by_capability(self, capability: str) -> list[TilemapPlugin]:
        return [
            r.plugin for r in self._plugins.values()
            if capability in r.plugin.manifest.capabilities
        ]

    def all(self) -> list[TilemapPlugin]:
        return [r.plugin for r in self._plugins.values()]

    def validate_all(self, document: TileMap) -> list[str]:
        errors: list[str] = []
        for record in self._plugins.values():
            try:
                errors.extend(record.plugin.validate(document))
            except Exception as exc:
                errors.append(f"{record.plugin.manifest.name}: validate() raised {exc!r}")
        return errors