"""Widgets personalizados de la UI."""
from PyQt6.QtWidgets import (
    QWidget, QLabel, QTextEdit, QLineEdit, QHBoxLayout,
    QPushButton, QFileDialog, QVBoxLayout
)
from PyQt6.QtCore import pyqtSignal


class UrlInput(QWidget):
    """Área de texto para pegar una o varias URLs (una por línea)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        top = QHBoxLayout()
        self.label = QLabel("Pega una o varias URLs de YouTube (una por línea):")
        top.addWidget(self.label)
        top.addStretch()

        self.paste_btn = QPushButton("📋 Pegar")
        self.paste_btn.clicked.connect(self._paste)
        top.addWidget(self.paste_btn)

        self.clear_btn = QPushButton("✖ Limpiar")
        self.clear_btn.clicked.connect(self._clear)
        top.addWidget(self.clear_btn)

        layout.addLayout(top)

        self.input = QTextEdit()
        self.input.setPlaceholderText(
            "https://www.youtube.com/watch?v=...\n"
            "https://youtu.be/...\n"
            "https://www.youtube.com/shorts/..."
        )
        self.input.setMaximumHeight(110)
        layout.addWidget(self.input)

    def _paste(self):
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        if clipboard:
            text = clipboard.text()
            if text:
                self.input.setPlainText(text.strip())

    def _clear(self):
        self.input.clear()

    def urls(self) -> list[str]:
        """Retorna lista de URLs no vacías, una por línea."""
        raw = self.input.toPlainText()
        return [line.strip() for line in raw.splitlines() if line.strip()]


class FolderPicker(QWidget):
    """Selector de carpeta de destino."""
    folder_changed = pyqtSignal(str)

    def __init__(self, initial: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel("📁 Guardar en:")
        layout.addWidget(self.label)

        self.path_input = QLineEdit(initial)
        self.path_input.setReadOnly(True)
        layout.addWidget(self.path_input, stretch=1)

        self.browse_btn = QPushButton("Elegir...")
        self.browse_btn.clicked.connect(self._browse)
        layout.addWidget(self.browse_btn)

    def _browse(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Seleccionar carpeta", self.path_input.text()
        )
        if folder:
            self.path_input.setText(folder)
            self.folder_changed.emit(folder)

    def path(self) -> str:
        return self.path_input.text()