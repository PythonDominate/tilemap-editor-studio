"""Windows entry point. Wires host + plugin loader + GUI shell."""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from tilemap_editor_studio.host.editor_host import EditorHost
from tilemap_editor_studio.plugins.loader import PluginLoader
from tilemap_editor_studio.plugins.registry import PluginRegistry
from tilemap_editor_studio.config.settings import load_settings


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tilemap-studio")
    parser.add_argument("project", nargs="?", type=Path, help="path to .tmap project")
    parser.add_argument("--plugin-dir", type=Path, default=None)
    parser.add_argument("--no-gui", action="store_true", help="headless: run validation only")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    _configure_logging(args.verbose)
    settings = load_settings(args.plugin_dir)

    registry = PluginRegistry()
    loader = PluginLoader(registry, settings.plugin_dirs)
    loader.discover_and_load()

    host = EditorHost(registry=registry, settings=settings)
    if args.project:
        host.open_project(args.project)

    if args.no_gui:
        return host.run_headless()

    from tilemap_editor_studio.gui.main_window import MainWindow  # lazy: Qt import cost

    return MainWindow(host).run()


if __name__ == "__main__":
    sys.exit(main())