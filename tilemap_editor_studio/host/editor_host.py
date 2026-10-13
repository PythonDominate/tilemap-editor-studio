"""EditorHost — owns the open document, the plugin registry, and the event bus.

Concurrency: all mutation happens on the Qt main thread. Plugins that need
background work must marshal results back via `host.bus.emit_threadsafe`.
"""
from __future__ import annotations

import logging
from pathlib import Path

from tilemap_editor_studio.config.settings import Settings
from tilemap_editor_studio.host.event_bus import EventBus
from tilemap_editor_studio.models.tilemap import TileMap
from tilemap_editor_studio.plugins.registry import PluginRegistry
from tilemap_editor_studio.services.project_io import load_project, save_project

log = logging.getLogger(__name__)


class EditorHost:
    def __init__(self, registry: PluginRegistry, settings: Settings) -> None:
        self.registry = registry
        self.settings = settings
        self.bus = EventBus()
        self.document: TileMap | None = None
        self._dirty = False

    def open_project(self, path: Path) -> TileMap:
        self.document = load_project(path)
        self._dirty = False
        self.bus.emit("project.opened", path=str(path), size=self.document.size)
        log.info("opened %s (%dx%d tiles)", path.name, *self.document.size)
        return self.document

    def save_project(self, path: Path | None = None) -> None:
        if self.document is None:
            raise RuntimeError("no document open")
        target = path or self.document.source_path
        if target is None:
            raise RuntimeError("no target path; supply one")
        save_project(self.document, target)
        self._dirty = False
        self.bus.emit("project.saved", path=str(target))

    def mark_dirty(self) -> None:
        self._dirty = True

    def run_headless(self) -> int:
        """Validate the loaded document + all registered plugins. Returns exit code."""
        if self.document is None:
            log.error("headless mode requires a project path")
            return 2
        errors = self.registry.validate_all(self.document)
        for err in errors:
            log.error("plugin validation: %s", err)
        return 1 if errors else 0