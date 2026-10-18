"""Descarga y conversión de audio a MP3 (versión optimizada con cancelación robusta)."""
from pathlib import Path
from typing import Callable, Optional
import os
import glob
import yt_dlp

from config import DEFAULT_OUTPUT_DIR, AUDIO_QUALITY
from core.youtube import VideoInfo, extract_video_info
from core.metadata import download_cover, write_tags
from utils.file_utils import sanitize_filename, ensure_unique_path


class DownloadCancelledError(Exception):
    """Excepción personalizada para cancelaciones limpias."""
    pass


class Downloader:
    """Orquesta la descarga de audio y aplicación de metadatos."""

    def __init__(
        self,
        output_dir: Optional[Path] = None,
        on_progress: Optional[Callable[[int, str, float], None]] = None,
        on_status: Optional[Callable[[int, str], None]] = None,
    ):
        self.output_dir = output_dir or DEFAULT_OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.on_progress = on_progress
        self.on_status = on_status
        self._cancelled = False
        self._current_item_id: Optional[int] = None

    def set_current_item(self, item_id: int) -> None:
        self._current_item_id = item_id

    def cancel(self) -> None:
        self._cancelled = True

    def _check_cancelled(self) -> None:
        """Lanza excepción si se canceló."""
        if self._cancelled:
            raise DownloadCancelledError("Descarga cancelada por el usuario")

    def _status(self, msg: str) -> None:
        if self.on_status and self._current_item_id is not None:
            self.on_status(self._current_item_id, msg)

    def _progress_hook(self, d: dict) -> None:
        self._check_cancelled()

        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            if total > 0:
                percent = (downloaded / total) * 100
                if self.on_progress and self._current_item_id is not None:
                    self.on_progress(
                        self._current_item_id,
                        d.get("_percent_str", f"{percent:.1f}%"),
                        percent,
                    )
        elif d.get("status") == "finished":
            if self.on_progress and self._current_item_id is not None:
                self.on_progress(self._current_item_id, "100%", 100.0)
            self._status("Procesando audio...")

    def _get_ffmpeg_path(self) -> Optional[str]:
        """Detecta automáticamente la carpeta de ffmpeg local."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ffmpeg_folders = glob.glob(os.path.join(base_dir, "ffmpeg", "ffmpeg-*"))
        if ffmpeg_folders:
            return os.path.join(ffmpeg_folders[0], "bin")
        return None

    @staticmethod
    def _aria2_available() -> bool:
        """Verifica si aria2c está disponible en el sistema."""
        import shutil
        return shutil.which("aria2c") is not None

    def download(self, url: str) -> Path:
        """Descarga el audio optimizado, convierte a MP3 y aplica metadatos."""
        self._cancelled = False
        self._check_cancelled()
        
        self._status("Obteniendo información del video...")
        info: VideoInfo = extract_video_info(url)
        self._check_cancelled()

        filename = sanitize_filename(f"{info.artist} - {info.title}")
        temp_path = self.output_dir / f"{filename}.%(ext)s"

        self._status("Descargando audio (modo rápido)...")
        ffmpeg_path = self._get_ffmpeg_path()

        ydl_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "concurrent_fragment_downloads": 16,
            "external_downloader": "aria2c" if self._aria2_available() else None,
            "external_downloader_args": {
                "aria2c": ["-x", "16", "-k", "1M", "-j", "16", "--console-log-level=warn"]
            } if self._aria2_available() else None,
            "ffmpeg_location": ffmpeg_path,
            "postprocessor_args": {
                "FFmpegExtractAudio": [
                    "-vn", "-threads", "0", "-codec:a", "libmp3lame",
                    "-b:a", f"{AUDIO_QUALITY}k", "-q:a", "2",
                ]
            },
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": AUDIO_QUALITY,
                }
            ],
            "outtmpl": str(temp_path),
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [self._progress_hook],
            "noplaylist": True,
            "retries": 5,
            "fragment_retries": 10,
            "socket_timeout": 30,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([info.webpage_url])

        self._check_cancelled()

        generated = self.output_dir / f"{filename}.mp3"
        final_path = ensure_unique_path(generated)
        if generated.exists() and generated != final_path:
            generated.rename(final_path)

        self._status("Descargando carátula...")
        cover_data = download_cover(info.thumbnail_url)
        self._check_cancelled()

        self._status("Escribiendo metadatos...")
        write_tags(
            mp3_path=final_path,
            title=info.title,
            artist=info.artist,
            album=info.title,
            cover_data=cover_data,
        )

        self._status("Completado ✓")
        return final_path