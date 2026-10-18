"""Extracción de información de videos de YouTube."""
from dataclasses import dataclass
from typing import Optional
import yt_dlp


@dataclass
class VideoInfo:
    """Información relevante de un video."""
    url: str
    video_id: str
    title: str
    artist: str
    thumbnail_url: Optional[str]
    duration: int  # segundos
    webpage_url: str


def extract_video_info(url: str) -> VideoInfo:
    """Extrae metadatos del video sin descargarlo."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "skip_download": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    if info is None:
        raise ValueError("No se pudo obtener información del video.")

    title = info.get("title") or "Sin título"
    # Artista: priorizar el campo 'artist', luego 'uploader', luego 'channel'
    artist = (
        info.get("artist")
        or info.get("uploader")
        or info.get("channel")
        or "Desconocido"
    )
    # Intentar separar "Artista - Título" si viene así
    if " - " in title and artist in ("Desconocido", info.get("uploader")):
        parts = title.split(" - ", 1)
        if len(parts) == 2:
            artist = parts[0].strip()
            title = parts[1].strip()

    return VideoInfo(
        url=url,
        video_id=info.get("id", "unknown"),
        title=title,
        artist=artist,
        thumbnail_url=info.get("thumbnail"),
        duration=int(info.get("duration") or 0),
        webpage_url=info.get("webpage_url", url),
    )