"""Ventana principal de la aplicación."""
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTextEdit, QMessageBox, QGroupBox, QStatusBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QFont, QDesktopServices

from config import APP_NAME, APP_VERSION, DEFAULT_OUTPUT_DIR
from core.downloader import Downloader, DownloadCancelledError
from core.queue import DownloadQueue, ItemStatus
from core.youtube import extract_video_info
from utils.validators import is_valid_youtube_url, normalize_url
from ui.widgets import UrlInput, FolderPicker
from ui.queue_view import QueueView


class QueueWorker(QThread):
    """Procesa la cola secuencialmente en segundo plano."""
    item_status = pyqtSignal(int, str)
    item_progress = pyqtSignal(int, str, float)
    item_state = pyqtSignal(int, object)
    item_title = pyqtSignal(int, str)
    item_done = pyqtSignal(int, str)
    item_error = pyqtSignal(int, str)
    queue_finished = pyqtSignal()

    def __init__(self, queue: DownloadQueue, output_dir: Path):
        super().__init__()
        self.queue = queue
        self.output_dir = output_dir
        self.downloader: Downloader | None = None
        self._cancelled = False

    def run(self):
        try:
            self.downloader = Downloader(
                output_dir=self.output_dir,
                on_progress=lambda iid, txt, pct: self.item_progress.emit(iid, txt, pct),
                on_status=lambda iid, msg: self.item_status.emit(iid, msg),
            )

            while self.queue.has_pending() and not self._cancelled:
                pending = self.queue.pending_items()
                if not pending:
                    break
                item = pending[0]
                self._process_item(item)

            # Si se canceló, marcar TODO lo pendiente/activo como CANCELLED
            if self._cancelled:
                for it in self.queue.all():
                    if it.status in (ItemStatus.PENDING, ItemStatus.FETCHING,
                                     ItemStatus.DOWNLOADING, ItemStatus.PROCESSING):
                        it.status = ItemStatus.CANCELLED
                        self.item_state.emit(it.id, ItemStatus.CANCELLED)
                        self.item_status.emit(it.id, "Cancelado")
        finally:
            # 🔑 CLAVE: siempre emitir queue_finished, incluso si hay excepción
            self.queue_finished.emit()

    def _process_item(self, item):
        item_id = item.id
        try:
            self.item_state.emit(item_id, ItemStatus.FETCHING)
            self.item_status.emit(item_id, "Obteniendo información...")
            self.downloader.set_current_item(item_id)

            info = extract_video_info(item.url)
            item.title = info.title
            item.artist = info.artist
            display = f"{info.artist} - {info.title}" if info.artist else info.title
            self.item_title.emit(item_id, display)

            self.item_state.emit(item_id, ItemStatus.DOWNLOADING)
            self.item_status.emit(item_id, "Descargando audio...")
            final_path = self.downloader.download(item.url)

            item.status = ItemStatus.DONE
            item.output_path = final_path
            self.item_state.emit(item_id, ItemStatus.DONE)
            self.item_done.emit(item_id, str(final_path))

        except DownloadCancelledError:
            # Cancelación limpia
            item.status = ItemStatus.CANCELLED
            self.item_state.emit(item_id, ItemStatus.CANCELLED)
            self.item_status.emit(item_id, "Cancelado")
            raise  # Re-lanzar para salir del bucle while

        except Exception as e:
            if self._cancelled:
                item.status = ItemStatus.CANCELLED
                self.item_state.emit(item_id, ItemStatus.CANCELLED)
                self.item_status.emit(item_id, "Cancelado")
            else:
                item.status = ItemStatus.ERROR
                item.error_message = str(e)
                self.item_state.emit(item_id, ItemStatus.ERROR)
                self.item_error.emit(item_id, str(e))

    def cancel(self):
        self._cancelled = True
        if self.downloader:
            self.downloader.cancel()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(780, 640)
        self.queue = DownloadQueue()
        self.worker: QueueWorker | None = None
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(10)
        root.setContentsMargins(16, 16, 16, 16)

        title = QLabel(f"🎵 {APP_NAME}")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        subtitle = QLabel("Convierte videos de YouTube a MP3 con carátula y metadatos")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: gray;")
        root.addWidget(subtitle)

        url_group = QGroupBox("1. URLs de YouTube")
        url_layout = QVBoxLayout(url_group)
        self.url_input = UrlInput()
        url_layout.addWidget(self.url_input)
        root.addWidget(url_group)

        folder_group = QGroupBox("2. Carpeta de destino")
        folder_layout = QVBoxLayout(folder_group)
        self.folder_picker = FolderPicker(str(DEFAULT_OUTPUT_DIR))
        folder_layout.addWidget(self.folder_picker)
        root.addWidget(folder_group)

        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("➕ Agregar a la cola")
        self.add_btn.setMinimumHeight(38)
        self.add_btn.clicked.connect(self._add_to_queue)
        btn_row.addWidget(self.add_btn)

        self.start_btn = QPushButton("▶  Iniciar cola")
        self.start_btn.setMinimumHeight(38)
        self.start_btn.setStyleSheet(
            "QPushButton { background-color: #ff0000; color: white; "
            "font-weight: bold; font-size: 14px; border-radius: 6px; }"
            "QPushButton:hover { background-color: #cc0000; }"
            "QPushButton:disabled { background-color: #888; }"
        )
        self.start_btn.clicked.connect(self._start_queue)
        btn_row.addWidget(self.start_btn)

        self.cancel_btn = QPushButton("⏹ Cancelar")
        self.cancel_btn.setMinimumHeight(38)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel_queue)
        btn_row.addWidget(self.cancel_btn)

        self.clear_btn = QPushButton("🧹 Limpiar completados")
        self.clear_btn.setMinimumHeight(38)
        self.clear_btn.clicked.connect(self._clear_completed)
        btn_row.addWidget(self.clear_btn)
        root.addLayout(btn_row)

        queue_group = QGroupBox("3. Cola de descargas")
        queue_layout = QVBoxLayout(queue_group)
        self.queue_view = QueueView()
        self.queue_view.remove_requested.connect(self._remove_item)
        queue_layout.addWidget(self.queue_view)
        root.addWidget(queue_group, stretch=1)

        log_group = QGroupBox("Registro")
        log_layout = QVBoxLayout(log_group)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(110)
        log_layout.addWidget(self.log)
        root.addWidget(log_group)

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Listo")

    def _add_to_queue(self):
        urls_raw = self.url_input.urls()
        if not urls_raw:
            QMessageBox.warning(self, "Sin URLs", "Pega al menos una URL de YouTube.")
            return

        added = 0
        invalid = 0
        for raw in urls_raw:
            if is_valid_youtube_url(raw):
                url = normalize_url(raw)
                item = self.queue.add(url)
                self.queue_view.add_item(item.id, url)
                added += 1
            else:
                invalid += 1
                self._log(f"  ⚠ URL inválida ignorada: {raw}")

        if invalid:
            QMessageBox.information(
                self, "URLs inválidas",
                f"Se agregaron {added} URLs.\n{invalid} URLs inválidas fueron ignoradas."
            )
        self.url_input.input.clear()
        self.statusBar().showMessage(f"{added} ítem(s) agregado(s) a la cola")

    def _remove_item(self, item_id: int):
        self.queue.remove(item_id)
        self.queue_view.remove_item(item_id)
        self._log(f"  · Ítem #{item_id} removido de la cola")

    def _clear_completed(self):
        done_ids = [
            it.id for it in self.queue.all()
            if it.status in (ItemStatus.DONE, ItemStatus.ERROR, ItemStatus.CANCELLED)
        ]
        for iid in done_ids:
            self.queue_view.remove_item(iid)
        self.queue.clear_completed()
        self._log(f"  · Limpiados {len(done_ids)} ítem(s)")

    def _start_queue(self):
        if not self.queue.has_pending():
            QMessageBox.information(self, "Cola vacía", "No hay ítems pendientes.")
            return

        output_dir = Path(self.folder_picker.path())
        self._set_running_ui(True)
        self._log("▶ Iniciando cola de descargas...")

        self.worker = QueueWorker(self.queue, output_dir)
        self.worker.item_status.connect(self._on_item_status)
        self.worker.item_progress.connect(self._on_item_progress)
        self.worker.item_state.connect(self._on_item_state)
        self.worker.item_title.connect(self._on_item_title)
        self.worker.item_done.connect(self._on_item_done)
        self.worker.item_error.connect(self._on_item_error)
        self.worker.queue_finished.connect(self._on_queue_finished)
        self.worker.start()

    def _cancel_queue(self):
        if self.worker:
            self.worker.cancel()
            self.cancel_btn.setEnabled(False)
            self.statusBar().showMessage("Cancelando...")
            self._log("⏹ Cancelando cola...")

    def _set_running_ui(self, running: bool):
        self.add_btn.setEnabled(not running)
        self.start_btn.setEnabled(not running)
        self.cancel_btn.setEnabled(running)
        self.clear_btn.setEnabled(not running)

    def _on_item_status(self, item_id: int, msg: str):
        item = self.queue.get(item_id)
        if item:
            item.status_text = msg
        self.queue_view.update_status(item_id, ItemStatus.DOWNLOADING, msg)
        self.statusBar().showMessage(f"#{item_id}: {msg}")

    def _on_item_progress(self, item_id: int, text: str, percent: float):
        item = self.queue.get(item_id)
        if item:
            item.progress = percent
        self.queue_view.update_progress(item_id, percent, text)

    def _on_item_state(self, item_id: int, state: ItemStatus):
        item = self.queue.get(item_id)
        if item:
            item.status = state
        self.queue_view.update_status(item_id, state)

    def _on_item_title(self, item_id: int, display_title: str):
        item = self.queue.get(item_id)
        if item:
            item.title = display_title
        self.queue_view.update_title(item_id, display_title)

    def _on_item_done(self, item_id: int, path: str):
        self._log(f"  ✓ #{item_id} → {path}")
        item = self.queue.get(item_id)
        if item:
            item.output_path = Path(path)

    def _on_item_error(self, item_id: int, msg: str):
        self._log(f"  ✗ #{item_id}: {msg}")

    def _on_queue_finished(self):
        self._set_running_ui(False)
        self.worker = None  # 🔑 Liberar referencia al worker
        
        done = sum(1 for it in self.queue.all() if it.status == ItemStatus.DONE)
        errors = sum(1 for it in self.queue.all() if it.status == ItemStatus.ERROR)
        cancelled = sum(1 for it in self.queue.all() if it.status == ItemStatus.CANCELLED)
        
        self.statusBar().showMessage(
            f"Cola finalizada: {done} completados, {errors} errores, {cancelled} cancelados"
        )
        self._log(f"▶ Cola finalizada: {done} OK, {errors} errores, {cancelled} cancelados")

        if done > 0:
            first_done = next(
                (it for it in self.queue.all() if it.status == ItemStatus.DONE), None
            )
            if first_done and first_done.output_path:
                reply = QMessageBox.question(
                    self, "¿Abrir carpeta?",
                    f"{done} archivo(s) descargado(s).\n\n¿Abrir la carpeta de destino?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    QDesktopServices.openUrl(
                        QUrl.fromLocalFile(str(first_done.output_path.parent))
                    )

    def _log(self, msg: str):
        self.log.append(msg)