"""Vista de la cola de descargas."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QAbstractItemView, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from core.queue import ItemStatus


STATUS_LABELS = {
    ItemStatus.PENDING: "⏳ En espera",
    ItemStatus.FETCHING: "🔍 Obteniendo info...",
    ItemStatus.DOWNLOADING: "⬇️ Descargando",
    ItemStatus.PROCESSING: "🏷️ Procesando...",
    ItemStatus.DONE: "✅ Completado",
    ItemStatus.ERROR: "❌ Error",
    ItemStatus.CANCELLED: "⏹️ Cancelado",
}

STATUS_COLORS = {
    ItemStatus.PENDING: "#888",
    ItemStatus.FETCHING: "#2196F3",
    ItemStatus.DOWNLOADING: "#FF9800",
    ItemStatus.PROCESSING: "#9C27B0",
    ItemStatus.DONE: "#4CAF50",
    ItemStatus.ERROR: "#F44336",
    ItemStatus.CANCELLED: "#777",
}


class QueueView(QWidget):
    """Tabla que muestra la cola de descargas."""
    remove_requested = pyqtSignal(int)  # item_id

    COL_TITLE = 0
    COL_STATUS = 1
    COL_PROGRESS = 2
    COL_ACTION = 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows_by_id: dict[int, int] = {}
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Canción", "Estado", "Progreso", ""])
        self.table.horizontalHeader().setSectionResizeMode(
            self.COL_TITLE, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            self.COL_STATUS, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            self.COL_PROGRESS, QHeaderView.ResizeMode.Fixed
        )
        self.table.horizontalHeader().setSectionResizeMode(
            self.COL_ACTION, QHeaderView.ResizeMode.Fixed
        )
        self.table.setColumnWidth(self.COL_PROGRESS, 160)
        self.table.setColumnWidth(self.COL_ACTION, 80)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.cellClicked.connect(self._on_cell_clicked)
        layout.addWidget(self.table)

    def add_item(self, item_id: int, display_title: str) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        self._rows_by_id[item_id] = row

        # Título
        title_item = QTableWidgetItem(display_title)
        title_item.setToolTip(display_title)
        self.table.setItem(row, self.COL_TITLE, title_item)

        # Estado
        status_item = QTableWidgetItem(STATUS_LABELS[ItemStatus.PENDING])
        status_item.setForeground(QColor(STATUS_COLORS[ItemStatus.PENDING]))
        self.table.setItem(row, self.COL_STATUS, status_item)

        # Progreso (barra)
        progress = QProgressBar()
        progress.setMinimum(0)
        progress.setMaximum(100)
        progress.setValue(0)
        progress.setTextVisible(True)
        self.table.setCellWidget(row, self.COL_PROGRESS, progress)

        # Botón quitar
        btn = QPushButton("✖")
        btn.setToolTip("Quitar de la cola")
        btn.setProperty("item_id", item_id)
        btn.clicked.connect(lambda: self.remove_requested.emit(item_id))
        self.table.setCellWidget(row, self.COL_ACTION, btn)

    def update_status(self, item_id: int, status: ItemStatus, text: str = "") -> None:
        row = self._rows_by_id.get(item_id)
        if row is None:
            return
        label = text or STATUS_LABELS.get(status, str(status))
        item = self.table.item(row, self.COL_STATUS)
        if item:
            item.setText(label)
            item.setForeground(QColor(STATUS_COLORS.get(status, "#888")))

    def update_progress(self, item_id: int, percent: float, text: str = "") -> None:
        row = self._rows_by_id.get(item_id)
        if row is None:
            return
        bar = self.table.cellWidget(row, self.COL_PROGRESS)
        if isinstance(bar, QProgressBar):
            bar.setValue(int(percent))
            if text:
                bar.setFormat(text.strip())

    def update_title(self, item_id: int, display_title: str) -> None:
        row = self._rows_by_id.get(item_id)
        if row is None:
            return
        item = self.table.item(row, self.COL_TITLE)
        if item:
            item.setText(display_title)
            item.setToolTip(display_title)

    def remove_item(self, item_id: int) -> None:
        row = self._rows_by_id.pop(item_id, None)
        if row is not None:
            self.table.removeRow(row)
            # Re-indexar filas
            self._rows_by_id = {
                iid: self.table.rowCount() - 1 - i
                for i, iid in enumerate(reversed(list(self._rows_by_id.keys())))
            }
            # Reconstruir índice correctamente
            self._rows_by_id = {}
            for r in range(self.table.rowCount()):
                btn = self.table.cellWidget(r, self.COL_ACTION)
                if btn:
                    iid = btn.property("item_id")
                    if iid is not None:
                        self._rows_by_id[iid] = r

    def clear(self) -> None:
        self.table.setRowCount(0)
        self._rows_by_id.clear()

    def _on_cell_clicked(self, row: int, col: int):
        # Manejo adicional si se necesita (actualmente los botones tienen su propia señal)
        pass