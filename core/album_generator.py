"""Orchestrates Gemini metadata, Last.fm tracks, and cover image generation."""

from PIL import Image

import gemini_service
from services.image_service import get_album_cover_from_data
from services.lastfm_service import build_tracklist


def generate_full_album(
    journal_text: str,
    genre: str,
    era: str,
    track_count: int,
) -> tuple[dict, Image.Image]:
    """
    Run the full album pipeline (no GUI).

    Returns
    -------
    album_data : dict with metadata and a ``tracks`` list
    cover      : PIL Image (generated art or placeholder)
    """
    album_data = gemini_service.generate_album_metadata(
        journal_text=journal_text,
        genre=genre,
        era=era,
        track_count=track_count,
    )
    tags = album_data.get("lastfm_tags") or []
    album_data["tracks"] = build_tracklist(tags, track_count)
    cover = get_album_cover_from_data(album_data, genre)
    return album_data, cover
