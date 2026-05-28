import requests


LASTFM_BASE_URL = "https://ws.audioscrobbler.com/2.0/"
MAX_TAG_PAGES = 3
LASTFM_API_KEY = None


def configure_lastfm(api_key: str) -> None:
    global LASTFM_API_KEY
    LASTFM_API_KEY = api_key



def fetch_tracks_by_tag(tag: str, limit: int = 50, page: int = 1) -> list[dict]:
    if not LASTFM_API_KEY:
        raise RuntimeError("Last.fm API key is not configured.")

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

        
        if isinstance(raw_tracks, dict):
            raw_tracks = [raw_tracks]

        tracks = []
        for t in raw_tracks:
            title  = t.get("name", "").strip()
            artist = ""
           
            artist_field = t.get("artist", {})
            if isinstance(artist_field, dict):
                artist = artist_field.get("name", "").strip()
            elif isinstance(artist_field, str):
                artist = artist_field.strip()

            url = t.get("url", "").strip()

           
            if title and artist and url:
                tracks.append({"title": title, "artist": artist, "url": url})

        return tracks

    except requests.exceptions.Timeout:
        print(f"[LastFM] Request timed out for tag '{tag}'.")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"[LastFM] HTTP error for tag '{tag}': {e}")
        return []
    except requests.exceptions.ConnectionError:
        print(f"[LastFM] Connection error for tag '{tag}'. Check your internet connection.")
        return []
    except (KeyError, ValueError) as e:
        print(f"[LastFM] Failed to parse response for tag '{tag}': {e}")
        return []


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



if __name__ == "__main__":
    import os

    configure_lastfm(os.environ.get("LASTFM_API_KEY", ""))

    test_tags = ["melancholy", "rainy day", "indie"]
    result = build_tracklist(test_tags, track_count=8, genre="Indie")

    print(f"\n{'─'*50}")
    print(f"  {len(result)} tracks returned")
    print(f"{'─'*50}")
    for i, t in enumerate(result, 1):
        print(f"  {i:>2}. {t['title']} — {t['artist']}")
        print(f"      {t['url']}")
    print(f"{'─'*50}\n")
