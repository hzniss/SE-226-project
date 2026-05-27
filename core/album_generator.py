"""
REQ 9 (akış kısmı): Gemini metadata üretimi, Last.fm şarkı çekme ve kapak
       görseli oluşturma adımlarını tek bir pipeline'da sıralar. Her adımdan
       önce status_callback ile GUI'ye ilerleme mesajı gönderilir (varsa).

Bu modül app.py içindeki WorkerThread tarafından arka plan thread'inde çağrılır.
"""

from PIL import Image

from services import gemini_service
from services.image_service import get_album_cover_from_data
from services.lastfm_service import build_tracklist


# TÜM ALBÜM PIPELINE'I (METADATA + TRACKLIST + KAPAK)

def generate_full_album(
    journal_text: str,
    genre: str,
    era: str,
    track_count: int,
    status_callback=None,
) -> tuple[dict, Image.Image]:
    """
    Albümün tüm üretim akışını (GUI'siz) çalıştırır.

    Parametreler
    ------------
    journal_text    : Kullanıcının mood/journal metin girişi
    genre           : Seçilen müzik türü (örn. "Indie")
    era             : Seçilen dönem (örn. "2000s")
    track_count     : İstenen şarkı sayısı (6-14)
    status_callback : (opsiyonel) Her adımda çağrılan, str mesaj alan fonksiyon.
                      WorkerThread tarafından sağlanır; None ise mesaj gönderilmez.

    Dönen değer
    -----------
    tuple  ->  (album_data: dict, cover: PIL.Image)
               album_data metadata + "tracks" listesini içerir.
    """
    # status_callback verilmemişse hiçbir şey yapmayan güvenli sarmalayıcı
    def _status(msg):
        if status_callback is not None:
            status_callback(msg)

    # 1) Gemini'den albüm metadata'sı + Last.fm tag'leri (REQ 4)
    _status("Gemini is thinking...")
    album_data = gemini_service.generate_album_metadata(
        journal_text=journal_text,
        genre=genre,
        era=era,
        track_count=track_count,
    )

    # 2) Tag'lerden gerçek şarkılarla tracklist oluştur (REQ 1, REQ 5)
    _status("Fetching tracks...")
    tags = album_data.get("lastfm_tags") or []
    album_data["tracks"] = build_tracklist(tags, track_count, genre=genre)

    # 3) Kapak görselini üret (REQ 6)
    _status("Generating cover...")
    cover = get_album_cover_from_data(album_data, genre)

    return album_data, cover
