"""
REQ 1: requests kütüphanesi ile Last.fm Web API'nin tag.gettoptracks endpoint'i kullanılır.
       Gemini'nin önerdiği tag'ler için bu endpoint çağrılır ve birden fazla tag'den
       gelen sonuçlar birleştirilerek çeşitli bir tracklist oluşturulur.

REQ 5: Gemini'den gelen Last.fm tag'leri kullanılarak gerçek şarkılar çekilir.
       Duplicate track'ler filtrelenir.
       Son tracklist kullanıcının istediği track sayısını içerir.
"""

import requests
from config import LASTFM_API_KEY


LASTFM_BASE_URL = "https://ws.audioscrobbler.com/2.0/"
MAX_TAG_PAGES = 5



# TEK TAG İÇİN ŞARKI ÇEKME

def fetch_tracks_by_tag(tag: str, limit: int = 50, page: int = 1) -> list[dict]:
    """
    Belirtilen tag için Last.fm tag.gettoptracks endpoint'ini çağırır.
    Her şarkı için {'title', 'artist', 'url'} anahtarlarını içeren
    sözlüklerden oluşan bir liste döner.
    Herhangi bir hata durumunda boş liste döner (uygulamayı çökertemez).

    Parametreler
    ------------
    tag   : Last.fm tag string'i (örn. "melancholy", "rainy day")
    limit : Bu tag için istenen maksimum şarkı sayısı
    page  : Last.fm sonuç sayfası

    Dönen değer
    -----------
    list[dict]  ->  [{"title": "...", "artist": "...", "url": "..."}, ...]
    """
    params = {
        "method":  "tag.gettoptracks",
        "tag":     tag,
        "limit":   limit,
        "page":    page,
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


def _normalize_tag(tag: str) -> str:
    return " ".join((tag or "").strip().lower().replace("/", " ").split())


def _derive_fallback_tags(genre: str) -> list[str]:
    normalized = _normalize_tag(genre)
    if not normalized:
        return []

    fallbacks = [normalized]
    fallback_map = {
        "hip hop rap": ["hip hop", "rap"],
        "r&b soul": ["r&b", "soul"],
        "turk pop": ["turkish pop", "pop"],
        "klasik": ["classical"],
    }
    fallbacks.extend(fallback_map.get(normalized, []))
    return fallbacks


def build_tracklist(tags: list[str], track_count: int, genre: str = "") -> list[dict]:
    """
    Gemini'den gelen tag listesindeki her tag için Last.fm'den şarkı çeker,
    sonuçları birleştirir, duplicate'leri temizler ve
    kullanıcının istediği sayıda şarkı döner.

    Duplicate tespiti: "title — artist" çifti büyük/küçük harf duyarsız olarak karşılaştırılır.

    Parametreler
    ------------
    tags        : Gemini'nin ürettiği Last.fm tag string'lerinin listesi
    track_count : Kullanıcının seçtiği şarkı sayısı (6-14 arası)
    genre       : Gerekirse fallback tag üretmek için seçilen müzik türü

    Dönen değer
    -----------
    list[dict]  ->  track_count kadar {"title": "...", "artist": "...", "url": "..."} listesi
    """
    normalized_tags = []
    seen_tag_names = set()
    for raw_tag in tags:
        tag = _normalize_tag(raw_tag)
        if tag and tag not in seen_tag_names:
            seen_tag_names.add(tag)
            normalized_tags.append(tag)

    for fallback_tag in _derive_fallback_tags(genre):
        if fallback_tag not in seen_tag_names:
            seen_tag_names.add(fallback_tag)
            normalized_tags.append(fallback_tag)

    if not normalized_tags:
        return []

    per_tag_limit = max(50, track_count * 4)
    seen_track_keys = set()
    unique_tracks = []

    for page in range(1, MAX_TAG_PAGES + 1):
        added_this_page = 0

        for tag in normalized_tags:
            fetched = fetch_tracks_by_tag(tag, limit=per_tag_limit, page=page)
            for track in fetched:
                key = f"{track['title'].lower()}|{track['artist'].lower()}"
                if key in seen_track_keys:
                    continue

                seen_track_keys.add(key)
                unique_tracks.append(track)
                added_this_page += 1

                if len(unique_tracks) >= track_count:
                    return unique_tracks[:track_count]

        if added_this_page == 0:
            break

    print(
        f"[LastFM] Only found {len(unique_tracks)} unique tracks "
        f"for requested count {track_count}."
    )
    return unique_tracks[:track_count]


# MODÜLÜ DOĞRUDAN ÇALIŞTIRARAK TEST ET


if __name__ == "__main__":
    # Hızlı smoke test — gerçek API key ile çalışır
    test_tags = ["melancholy", "rainy day", "indie"]
    result = build_tracklist(test_tags, track_count=8, genre="Indie")

    print(f"\n{'─'*50}")
    print(f"  {len(result)} şarkı döndü")
    print(f"{'─'*50}")
    for i, t in enumerate(result, 1):
        print(f"  {i:>2}. {t['title']} — {t['artist']}")
        print(f"      {t['url']}")
    print(f"{'─'*50}\n")
