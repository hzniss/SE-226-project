import sys
from pathlib import Path

# python tests/test_image_services.py çalışınca proje kökü path'te olmalı
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from services.image_service import get_album_cover, get_album_cover_from_data

# When Beyza is ready, the real output will be in this format
MOCK_ALBUM_DATA = {
    "album_name": "Midnight Echoes",
    "artist_name": "Luna Vale",
    "year": 2019,
    "label": "Dreamwave Records",
    "mood_description": "melancholic late-night walk",
    "cover_prompt": "rainy seaside at night, melancholic mood, cinematic album cover art",
    "lastfm_tags": ["indie", "sad", "rain"],
}

image = get_album_cover_from_data(MOCK_ALBUM_DATA, genre="Indie")
image.show()
image.save("test_cover.png")
print("Saved test_cover.png")

empty_test = get_album_cover("", genre="Pop")
print("Empty prompt -> placeholder:", empty_test.size)