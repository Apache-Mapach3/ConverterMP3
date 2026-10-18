"""Configuración global de la aplicación."""
from pathlib import Path

APP_NAME = "YT to MP3 Converter"
APP_VERSION = "1.0.0"

# Carpeta por defecto para guardar los MP3
DEFAULT_OUTPUT_DIR = Path.home() / "Music" / "YT_MP3"
DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Formato de audio
AUDIO_FORMAT = "mp3"
AUDIO_QUALITY = "192"  # kbps

# Tiempo de espera para descargas (segundos)
DOWNLOAD_TIMEOUT = 300

# User-Agent para requests
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)