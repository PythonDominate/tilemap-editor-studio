"""Discovers plugins from disk + entry points, enforces API version, registers them."""
from __future__ import annotations

import importlib.metadata as md
import importlib.util
import logging
import sys
from pathlib import Path

from tilemap_editor_studio.plugins.contracts import (
    PluginAPIError,
    PluginBase,
    PluginManifest,
    TilemapPlugin,
)
from tilemap_editor_studio.plugins.registry import PluginRegistry

log = logging.getLogger(__name__)
SUPPORTED_API = "1.x"


def _api_compatible(version: str) -> bool:
    return version.split(".")[0] == SUPPORTED_API.split(".")[0]


class PluginLoader:
    def __init__(self, registry: PluginRegistry, plugin_dirs: list[Path]) -> None:
        self.registry = registry
        self.plugin_dirs = plugin_dirs

    def discover_and_load(self) -> None:
        self._load_entry_points()
        for directory in self.plugin_dirs:
            self._load_directory(directory)

    def _load_entry_points(self) -> None:
        for ep in md.entry_points(group="tilemap_studio.plugins"):
            try:
                cls = ep.load()
                self._instantiate_and_register(cls, source=f"entry_point:{ep.name}")
            except Exception as exc:
                log.warning("entry point %s failed to load: %s", ep.name, exc)

    def _load_directory(self, directory: Path) -> None:
        if not directory.is_dir():
            return
        for plugin_file in sorted(directory.glob("*/plugin.py")):
            self._load_file(plugin_file)

    def _load_file(self, plugin_file: Path) -> None:
        module_name = f"tilemap_plugin_{plugin_file.parent.name}"
        spec = importlib.util.spec_from_file_location(module_name, plugin_file)
        if spec is None or spec.loader is None:
            log.warning("cannot build spec for %s", plugin_file)
            return
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
        except Exception as exc:
            log.warning("plugin %s raised on import: %s", plugin_file.parent.name, exc)
            return
        for attr in dir(module):
            obj = getattr(module, attr)
            if isinstance(obj, type) and issubclass(obj, PluginBase) and obj is not PluginBase:
                self._instantiate_and_register(obj, source=str(plugin_file))

    def _instantiate_and_register(self, cls: type, source: str) -> None:
        instance = cls()
        if not isinstance(instance, TilemapPlugin):
            raise PluginAPIError(f"{cls.__name__} does not satisfy TilemapPlugin")
        manifest: PluginManifest = instance.manifest
        if not _api_compatible(manifest.api_version):
            raise PluginAPIError(
                f"{manifest.name} targets API {manifest.api_version}, host supports {SUPPORTED_API}"
            )
        self.registry.register(instance, source=source)