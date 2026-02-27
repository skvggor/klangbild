from pathlib import Path
from mutagen.id3 import ID3
from mutagen._util import MutagenError


def read_id3_tags(audio_path: str) -> tuple[str, str, str]:
    stem = Path(audio_path).stem
    title, artist, album = stem, "", ""
    try:
        tags = ID3(audio_path)
        if tags.get("TIT2"):
            title = str(tags["TIT2"].text[0]).strip() or stem
        if tags.get("TPE1"):
            artist = str(tags["TPE1"].text[0]).strip()
        if tags.get("TALB"):
            album = str(tags["TALB"].text[0]).strip()
    except MutagenError:
        pass
    return title, artist, album
