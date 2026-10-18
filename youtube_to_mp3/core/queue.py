"""Gestión de la cola de descargas."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from pathlib import Path


class ItemStatus(str, Enum):
    PENDING = "pending"
    FETCHING = "fetching"       # obteniendo info
    DOWNLOADING = "downloading"
    PROCESSING = "processing"   # escribiendo tags
    DONE = "done"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class QueueItem:
    """Representa un ítem en la cola."""
    id: int
    url: str
    title: str = ""
    artist: str = ""
    status: ItemStatus = ItemStatus.PENDING
    progress: float = 0.0
    status_text: str = "En espera"
    error_message: str = ""
    output_path: Optional[Path] = None

    @property
    def display_title(self) -> str:
        if self.title:
            return f"{self.artist} - {self.title}" if self.artist else self.title
        return self.url


class DownloadQueue:
    """Cola ordenada de ítems de descarga."""

    def __init__(self):
        self._items: List[QueueItem] = []
        self._next_id = 1

    def add(self, url: str) -> QueueItem:
        item = QueueItem(id=self._next_id, url=url)
        self._next_id += 1
        self._items.append(item)
        return item

    def add_many(self, urls: List[str]) -> List[QueueItem]:
        return [self.add(u) for u in urls]

    def all(self) -> List[QueueItem]:
        return list(self._items)

    def get(self, item_id: int) -> Optional[QueueItem]:
        for it in self._items:
            if it.id == item_id:
                return it
        return None

    def remove(self, item_id: int) -> None:
        self._items = [it for it in self._items if it.id != item_id]

    def clear(self) -> None:
        self._items.clear()

    def clear_completed(self) -> None:
        self._items = [
            it for it in self._items
            if it.status not in (ItemStatus.DONE, ItemStatus.ERROR, ItemStatus.CANCELLED)
        ]

    def pending_items(self) -> List[QueueItem]:
        return [it for it in self._items if it.status == ItemStatus.PENDING]

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def has_pending(self) -> bool:
        return any(it.status == ItemStatus.PENDING for it in self._items)