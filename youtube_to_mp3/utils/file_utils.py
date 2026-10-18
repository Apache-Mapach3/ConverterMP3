"""Utilidades para manejo de archivos."""
import re
from pathlib import Path


def sanitize_filename(name: str, max_length: int = 150) -> str:
    """Limpia un nombre para que sea válido como archivo."""
    if not name:
        return "unknown"
    # Eliminar caracteres inválidos
    name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "", name)
    # Reemplazar espacios múltiples
    name = re.sub(r"\s+", " ", name).strip()
    # Cortar si es muy largo
    if len(name) > max_length:
        name = name[:max_length].rstrip()
    return name or "unknown"


def ensure_unique_path(path: Path) -> Path:
    """Si el archivo ya existe, agrega un sufijo numérico."""
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 1
    while True:
        new_path = parent / f"{stem} ({counter}){suffix}"
        if not new_path.exists():
            return new_path
        counter += 1