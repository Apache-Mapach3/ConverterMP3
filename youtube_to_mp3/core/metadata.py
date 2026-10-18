"""Escritura de metadatos ID3 en archivos MP3."""
from pathlib import Path
from typing import Optional
import requests
from mutagen.mp3 import MP3
from mutagen.id3 import (
    ID3, TIT2, TPE1, TALB, APIC, ID3NoHeaderError
)
from PIL import Image
import io

from config import USER_AGENT


def download_cover(thumbnail_url: str, target_size: tuple = (600, 600)) -> Optional[bytes]:
    """Descarga la carátula y la redimensiona."""
    if not thumbnail_url:
        return None
    try:
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(thumbnail_url, headers=headers, timeout=20)
        resp.raise_for_status()

        # Redimensionar con Pillow
        img = Image.open(io.BytesIO(resp.content))
        img = img.convert("RGB")
        img.thumbnail(target_size, Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=90)
        return buffer.getvalue()
    except Exception as e:
        print(f"[metadata] Error descargando carátula: {e}")
        return None


def write_tags(
    mp3_path: Path,
    title: str,
    artist: str,
    album: Optional[str] = None,
    cover_data: Optional[bytes] = None,
) -> None:
    """Escribe tags ID3v2 al archivo MP3."""
    try:
        audio = MP3(mp3_path, ID3=ID3)
    except ID3NoHeaderError:
        audio = MP3(mp3_path)
        audio.add_tags()

    tags = audio.tags
    if tags is None:
        audio.add_tags()
        tags = audio.tags

    tags.delall("TIT2")
    tags.add(TIT2(encoding=3, text=title))

    tags.delall("TPE1")
    tags.add(TPE1(encoding=3, text=artist))

    tags.delall("TALB")
    tags.add(TALB(encoding=3, text=album or title))

    if cover_data:
        tags.delall("APIC")
        tags.add(
            APIC(
                encoding=3,
                mime="image/jpeg",
                type=3,  # Front cover
                desc="Cover",
                data=cover_data,
            )
        )

    audio.save(v2_version=3)