"""
REQ 8: Uygulama, albümü kullanıcının seçtiği bir klasöre hem JSON dosyası
       (tüm metadata + tracklist) hem de PNG dosyası (kapak görseli) olarak
       kaydedebilen bir export özelliği sunar.

Bu modül main.py tarafından çağrılır. Klasör seçimi GUI tarafında
filedialog ile yapılır; buraya yalnızca seçilmiş klasör yolu (folder_path)
geçirilir.
"""

import json
import re
from pathlib import Path

from PIL import Image


# DOSYA ADI TEMİZLEME

def _safe_filename(name: str, fallback: str = "album") -> str:
    """
    Albüm adını dosya/klasör adı olarak kullanılabilir hale getirir.
    Windows ve diğer sistemlerde sorun çıkaran karakterleri ( \\ / : * ? " < > | )
    alt çizgi ile değiştirir, baştaki/sondaki boşlukları temizler.

    Parametreler
    ------------
    name     : Temizlenecek ham string (örn. albüm adı "Aegean Rain")
    fallback : İsim boş kalırsa kullanılacak varsayılan ad

    Dönen değer
    -----------
    str  ->  dosya sistemi için güvenli isim (örn. "Aegean_Rain")
    """
    cleaned = re.sub(r'[\\/:*?"<>|]', "_", str(name)).strip()
    cleaned = re.sub(r"\s+", "_", cleaned)          # boşlukları alt çizgiye çevir
    return cleaned if cleaned else fallback


# ALBÜMÜ KAYDETME (JSON + PNG)

def save_album(album_data: dict, cover_image: Image.Image, folder_path: str) -> dict:
    """
    Albümü kullanıcının seçtiği klasöre JSON ve PNG olarak kaydeder.

    Dosya adları albümün adından türetilir (örn. "Aegean_Rain.json" ve
    "Aegean_Rain.png"). Albüm adı yoksa "album" kullanılır. Klasör yoksa
    otomatik olarak oluşturulur.

    Herhangi bir hata durumunda uygulamayı çökertmez; sonucu bir sözlük
    olarak döner (status'a göre GUI kullanıcıya bilgi verebilir).

    Parametreler
    ------------
    album_data  : Tüm metadata + tracklist içeren sözlük
                  (album_name, artist_name, year, label, mood, tags, tracks ...)
    cover_image : Kaydedilecek kapak görseli (PIL Image)
    folder_path : Kullanıcının seçtiği hedef klasör yolu

    Dönen değer
    -----------
    dict  ->  {"success": bool, "json_path": str|None,
               "png_path": str|None, "error": str|None}
    """
    try:
        folder = Path(folder_path)
        folder.mkdir(parents=True, exist_ok=True)

        # Dosya adlarını albüm adından üret
        base_name = _safe_filename(album_data.get("album_name", "album"))
        json_path = folder / f"{base_name}.json"
        png_path  = folder / f"{base_name}.png"

        # 1) Metadata + tracklist -> JSON
        #    ensure_ascii=False  -> Türkçe karakterler bozulmaz
        #    indent=2            -> okunabilir biçim
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(album_data, f, ensure_ascii=False, indent=2)

        # 2) Kapak görseli -> PNG
        #    RGB'ye çevirerek PNG kaydında olası mod hatalarını önle
        cover_image.convert("RGB").save(png_path, "PNG")

        return {
            "success":   True,
            "json_path": str(json_path),
            "png_path":  str(png_path),
            "error":     None,
        }

    except (OSError, ValueError, TypeError) as e:
        # OSError      -> klasör/dosya yazma izni, geçersiz yol vb.
        # ValueError   -> JSON serileştirme hatası
        # TypeError    -> album_data dict değilse / cover_image PIL Image değilse
        print(f"[exporter] Save error: {e}")
        return {
            "success":   False,
            "json_path": None,
            "png_path":  None,
            "error":     str(e),
        }