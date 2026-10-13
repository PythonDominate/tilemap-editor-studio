"""Undo/redo stack. Command pattern — each edit is a reversible op."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


class Command(Protocol):
    label: str
    def apply(self) -> None: ...
    def revert(self) -> None: ...


@dataclass(slots=True)
class PaintCommand:
    """Single-tile paint. Kept small; batch paints use PaintBatchCommand."""
    label: str
    layer_data: np.ndarray
    x: int
    y: int
    new_id: int
    _old_id: int = -1

    def apply(self) -> None:
        self._old_id = int(self.layer_data[self.y, self.x])
        self.layer_data[self.y, self.x] = self.new_id

    def revert(self) -> None:
        self.layer_data[self.y, self.x] = self._old_id


class UndoStack:
    def __init__(self, limit: int = 512) -> None:
        self._done: list[Command] = []
        self._undone: list[Command] = []
        self._limit = limit

    def push(self, command: Command) -> None:
        command.apply()
        self._done.append(command)
        self._undone.clear()
        if len(self._done) > self._limit:
            self._done.pop(0)

    def undo(self) -> bool:
        if not self._done:
            return False
        cmd = self._done.pop()
        cmd.revert()
        self._undone.append(cmd)
        return True

    def redo(self) -> bool:
        if not self._undone:
            return False
        cmd = self._undone.pop()
        cmd.apply()
        self._done.append(cmd)
        return True