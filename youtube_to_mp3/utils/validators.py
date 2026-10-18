"""Validadores de URLs de YouTube."""
import re


YOUTUBE_REGEX = re.compile(
    r"^(https?://)?(www\.)?(youtube\.com/watch\?v=[\w-]+|"
    r"youtu\.be/[\w-]+|"
    r"youtube\.com/shorts/[\w-]+)",
    re.IGNORECASE,
)


def is_valid_youtube_url(url: str) -> bool:
    """Verifica si la URL es válida de YouTube."""
    if not url or not isinstance(url, str):
        return False
    return bool(YOUTUBE_REGEX.match(url.strip()))


def normalize_url(url: str) -> str:
    """Normaliza la URL (quita espacios, asegura https)."""
    url = url.strip()
    if url.startswith("youtu.be/"):
        url = "https://" + url
    elif not url.startswith("http"):
        url = "https://" + url
    return url