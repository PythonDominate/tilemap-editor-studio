"""Settings — user config from %APPDATA%/tilemap-editor-studio/settings.toml."""
from __future__ import annotations

import logging
import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

log = logging.getLogger(__name__)
APP_DIR = "tilemap-editor-studio"


@dataclass(slots=True)
class Settings:
    plugin_dirs: list[Path] = field(default_factory=list)
    recent_projects: list[Path] = field(default_factory=list)
    theme: str = "dark"
    grid_visible: bool = True
    autosave_seconds: int = 120


def _config_root() -> Path:
    base = os.environ.get("APPDATA") or str(Path.home())
    return Path(base) / APP_DIR


def load_settings(extra_plugin_dir: Path | None = None) -> Settings:
    root = _config_root()
    root.mkdir(parents=True, exist_ok=True)
    settings = Settings()

    cfg_file = root / "settings.toml"
    if cfg_file.is_file():
        try:
            data = tomllib.loads(cfg_file.read_text(encoding="utf-8"))
            settings.theme = data.get("ui", {}).get("theme", settings.theme)
            settings.grid_visible = data.get("ui", {}).get("grid", settings.grid_visible)
            settings.autosave_seconds = data.get("editor", {}).get("autosave", 120)
            settings.plugin_dirs = [Path(p) for p in data.get("plugins", {}).get("dirs", [])]
        except tomllib.TOMLDecodeError as exc:
            log.warning("settings.toml malformed, using defaults: %s", exc)

    default_plugins = root / "plugins"
    default_plugins.mkdir(exist_ok=True)
    if default_plugins not in settings.plugin_dirs:
        settings.plugin_dirs.append(default_plugins)
    if extra_plugin_dir and extra_plugin_dir not in settings.plugin_dirs:
        settings.plugin_dirs.append(extra_plugin_dir)
    return settings