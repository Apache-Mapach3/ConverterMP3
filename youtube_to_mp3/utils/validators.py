import re

YOUTUBE_REGEX = re.compile(
    r"^(https?://)?(www\.)?(youtube\.com/watch\?v=[\w-]+|"
    r"youtu\.be/[\w-]+|"
    r"youtube\.com/shorts/[\w-]+)",
    re.IGNORECASE,
)

# NUEVO: Regex para playlists de Spotify
SPOTIFY_PLAYLIST_REGEX = re.compile(
    r"^https://open\.spotify\.com/playlist/[a-zA-Z0-9]+",
    re.IGNORECASE
)

def is_valid_youtube_url(url: str) -> bool:
    if not url or not isinstance(url, str):
        return False
    return bool(YOUTUBE_REGEX.match(url.strip()))

# NUEVO: Validador de Spotify
def is_valid_spotify_playlist_url(url: str) -> bool:
    if not url or not isinstance(url, str):
        return False
    return bool(SPOTIFY_PLAYLIST_REGEX.match(url.strip()))

def normalize_url(url: str) -> str:
    url = url.strip()
    if url.startswith("youtu.be/"):
        url = "https://" + url
    elif not url.startswith("http"):
        url = "https://" + url
    return url