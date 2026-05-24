import sys
from pathlib import Path

# python tests/test_exporter.py çalışınca proje kökü path'te olmalı
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from PIL import Image
from core.exporter import save_album

# Gemini çıktı formatıyla eşleşen sahte albüm verisi (bkz. core/album_generator.py)
MOCK_ALBUM_DATA = {
    "album_name":   "Ege Yağmuru",
    "artist_name":  "Mavi Sesler",
    "year":         2007,
    "label":        "Hayali Plak",
    "mood":         "Hüzünlü anılar, yağmurla ıslanmış bir esintide süzülür.",
    "lastfm_tags":  ["classical", "neoclassical", "ambient", "melancholic"],
    "tracks": [
        {"title": "Uykusuz Her Gece", "artist": "Teoman", "url": "https://last.fm/..."},
        {"title": "Cambaz", "artist": "Mor ve Ötesi", "url": "https://last.fm/..."},
        {"title": "Ben Böyleyim", "artist": "Athena", "url": "https://last.fm/..."},
    ],
}

# Sahte kapak görseli (Pollinations'a bağlanmadan test etmek için)
mock_cover = Image.new("RGB", (600, 600), color=(60, 90, 120))

# Başarılı kaydetme testi
result = save_album(MOCK_ALBUM_DATA, mock_cover, folder_path="./test_export")
assert result["success"], f"Save failed: {result['error']}"
assert Path(result["json_path"]).exists(), "JSON file was not created"
assert Path(result["png_path"]).exists(),  "PNG file was not created"
print(f"JSON saved -> {result['json_path']}")
print(f"PNG  saved -> {result['png_path']}")

# Dosya adı temizleme testi - özel karakterli albüm adı
special_album = {**MOCK_ALBUM_DATA, "album_name": "Test: Album/Name?"}
result2 = save_album(special_album, mock_cover, folder_path="./test_export")
assert result2["success"], f"Special character test failed: {result2['error']}"
print(f"Special character test passed -> {Path(result2['json_path']).name}")

print("All tests passed.")