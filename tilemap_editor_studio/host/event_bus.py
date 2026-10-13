"""Tiny synchronous event bus. Thread-safe emit for plugin background work."""
from __future__ import annotations

import logging
import threading
from collections import defaultdict
from collections.abc import Callable
from typing import Any

log = logging.getLogger(__name__)
Handler = Callable[..., None]


class EventBus:
    def __init__(self) -> None:
        self._subs: dict[str, list[Handler]] = defaultdict(list)
        self._lock = threading.RLock()

    def subscribe(self, topic: str, handler: Handler) -> None:
        with self._lock:
            self._subs[topic].append(handler)

    def unsubscribe(self, topic: str, handler: Handler) -> None:
        with self._lock:
            self._subs[topic].remove(handler)

    def emit(self, topic: str, **payload: Any) -> None:
        with self._lock:
            handlers = list(self._subs.get(topic, ()))
        for handler in handlers:
            try:
                handler(**payload)
            except Exception:  # a bad plugin must not take down the host
                log.exception("handler for %r raised", topic)

    def emit_threadsafe(self, topic: str, **payload: Any) -> None:
        # Host mutation must land on the Qt thread; plugins call this from workers.
        from PySide6.QtCore import QMetaObject, Qt, Q_ARG  # local import: optional in headless

        QMetaObject.invokeMethod(
            self, "emit", Qt.QueuedConnection,
            Q_ARG(str, topic),
        )