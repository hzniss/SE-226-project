"""
REQ 1: requests kütüphanesi ile Last.fm Web API'nin tag.gettoptracks endpoint'i kullanılır.
       Gemini'nin önerdiği tag'ler için bu endpoint çağrılır ve birden fazla tag'den
       gelen sonuçlar birleştirilerek çeşitli bir tracklist oluşturulur.

REQ 5: Gemini'den gelen Last.fm tag'leri kullanılarak gerçek şarkılar çekilir.
       Duplicate track'ler filtrelenir.
       Son tracklist kullanıcının istediği track sayısını içerir.
"""

import requests


LASTFM_BASE_URL = "https://ws.audioscrobbler.com/2.0/"
LASTFM_API_KEY  = "54824551b8051a9c61224a773a850084" 


# TEK TAG İÇİN ŞARKI ÇEKME

def fetch_tracks_by_tag(tag: str, limit: int = 20) -> list[dict]:
    """
    Belirtilen tag için Last.fm tag.gettoptracks endpoint'ini çağırır.
    Her şarkı için {'title', 'artist', 'url'} anahtarlarını içeren
    sözlüklerden oluşan bir liste döner.
    Herhangi bir hata durumunda boş liste döner (uygulamayı çökertemez).

    Parametreler
    ------------
    tag   : Last.fm tag string'i (örn. "melancholy", "rainy day")
    limit : Bu tag için istenen maksimum şarkı sayısı (varsayılan: 20)

    Dönen değer
    -----------
    list[dict]  ->  [{"title": "...", "artist": "...", "url": "..."}, ...]
    """
    params = {
        "method":  "tag.gettoptracks",
        "tag":     tag,
        "limit":   limit,
        "api_key": LASTFM_API_KEY,
        "format":  "json",
    }
    headers = {"User-Agent": "AlbumCoverStudio/1.0"}

    try:
        response = requests.get(
            LASTFM_BASE_URL,
            params=params,
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        raw_tracks = data.get("tracks", {}).get("track", [])

        # API bazen tek bir sözlük döner, liste bekliyoruz
        if isinstance(raw_tracks, dict):
            raw_tracks = [raw_tracks]

        tracks = []
        for t in raw_tracks:
            title  = t.get("name", "").strip()
            artist = ""
            # artist alanı iç içe sözlük olarak gelir: {"name": "...", ...}
            artist_field = t.get("artist", {})
            if isinstance(artist_field, dict):
                artist = artist_field.get("name", "").strip()
            elif isinstance(artist_field, str):
                artist = artist_field.strip()

            url = t.get("url", "").strip()

            # Eksik veya boş veri içeren şarkıları atla
            if title and artist and url:
                tracks.append({"title": title, "artist": artist, "url": url})

        return tracks

    except requests.exceptions.Timeout:
        print(f"[LastFM] Tag '{tag}' için istek zaman aşımına uğradı.")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"[LastFM] Tag '{tag}' için HTTP hatası: {e}")
        return []
    except requests.exceptions.ConnectionError:
        print(f"[LastFM] Tag '{tag}' için bağlantı hatası. İnternet bağlantısını kontrol et.")
        return []
    except (KeyError, ValueError) as e:
        print(f"[LastFM] Tag '{tag}' için yanıt ayrıştırılamadı: {e}")
        return []


# BİRDEN FAZLA TAG'DEN TRACKLIST OLUŞTURMA


def build_tracklist(tags: list[str], track_count: int) -> list[dict]:
    """
    Gemini'den gelen tag listesindeki her tag için Last.fm'den şarkı çeker,
    sonuçları birleştirir, duplicate'leri temizler ve
    kullanıcının istediği sayıda şarkı döner.

    Duplicate tespiti: "title — artist" çifti büyük/küçük harf duyarsız olarak karşılaştırılır.

    Eğer tüm tag'lerden toplanan benzersiz şarkı sayısı track_count'tan azsa,
    mevcut tüm benzersiz şarkılar döner (uygulama hata vermez).

    Parametreler
    ------------
    tags        : Gemini'nin ürettiği Last.fm tag string'lerinin listesi
    track_count : Kullanıcının seçtiği şarkı sayısı (6-14 arası)

    Dönen değer
    -----------
    list[dict]  ->  track_count kadar {"title": "...", "artist": "...", "url": "..."} listesi
    """
    if not tags:
        return []

    # Her tag için kaç şarkı isteyeceğimizi belirle.
    # Daha fazla çekerek duplicate'lerden sonra yeterli şarkı kalsın.
    per_tag_limit = max(20, track_count * 3)

    all_tracks   = []   # Tüm tag'lerden ham şarkı listesi
    seen_keys    = set()  # Duplicate kontrolü için "title|artist" küçük harf seti
    unique_tracks = []   # Duplicate'ler temizlenmiş son liste

    for tag in tags:
        fetched = fetch_tracks_by_tag(tag, limit=per_tag_limit)
        all_tracks.extend(fetched)

    # Duplicate filtreleme
    for track in all_tracks:
        # Karşılaştırma anahtarı: büyük/küçük harf duyarsız "başlık|sanatçı"
        key = f"{track['title'].lower()}|{track['artist'].lower()}"
        if key not in seen_keys:
            seen_keys.add(key)
            unique_tracks.append(track)

    # İstenen sayıda şarkıyı döndür; yeterliyse kırp, değilse mevcut olanları ver
    return unique_tracks[:track_count]


# MODÜLÜ DOĞRUDAN ÇALIŞTIRARAK TEST ET


if __name__ == "__main__":
    # Hızlı smoke test — gerçek API key ile çalışır
    test_tags = ["melancholy", "rainy day", "indie"]
    result = build_tracklist(test_tags, track_count=8)

    print(f"\n{'─'*50}")
    print(f"  {len(result)} şarkı döndü")
    print(f"{'─'*50}")
    for i, t in enumerate(result, 1):
        print(f"  {i:>2}. {t['title']} — {t['artist']}")
        print(f"      {t['url']}")
    print(f"{'─'*50}\n")