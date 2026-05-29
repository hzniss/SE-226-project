import json
import google.generativeai as genai

GEMINI_MODEL = "gemini-2.5-flash"

GENRE_STYLES = {
    "Pop":           "vibrant colors, glossy aesthetic, modern pop album cover",
    "Rock":          "dark tones, gritty texture, electric energy, rock album cover",
    "Hip-Hop / Rap": "urban landscape, bold typography, street art style",
    "Electronic":    "neon lights, futuristic, glitch art, digital aesthetic",
    "Indie":         "lo-fi, warm film grain, vintage texture, indie aesthetic",
    "R&B / Soul":    "smooth gradients, warm tones, soulful mood",
    "Jazz":          "smoky atmosphere, noir lighting, classic jazz club feel",
    "Metal":         "dark, aggressive, gothic elements, metal album art",
    "Türk Pop":      "modern, colorful, Mediterranean warmth",
    "Klasik":        "elegant, orchestral hall, timeless classical aesthetic",
}

def configure_gemini(api_key: str) -> None:
    genai.configure(api_key=api_key)


def strip_markdown_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 1)[1]
        if text.startswith("json"):
            text = text[4:]
        if "```" in text:
            text = text.rsplit("```", 1)[0]
    return text.strip()


def _get_tag_guidance(genre: str) -> str:
    if genre == "Türk Pop":
        return (
            '- For "Türk Pop", prioritize Turkish-pop-oriented Last.fm tags such as '
            '"turkish pop", "turkish", and related Turkish music tags; avoid broad '
            'international tags unless they are clearly necessary.'
        )
    return ""


def _build_prompt(journal_text: str, genre: str, era: str, track_count: int) -> str:
    genre_style = GENRE_STYLES.get(genre, "artistic album cover")
    tag_guidance = _get_tag_guidance(genre)

    prompt = f"""You are a creative music curator AI. Based on the journal entry below,
generate a completely FICTIONAL album concept. The album, artist, year, and label
you create are imaginary — they do not correspond to any real release.

Return ONLY valid JSON with exactly this schema (no extra fields, no markdown):
{{
  "album_name":       "string — creative fictional album title",
  "artist_name":      "string — creative fictional artist name",
  "year":             "string — fictional release year matching the {era} era",
  "label":            "string — fictional record label name",
  "mood_description": "string — 1-2 sentence mood summary",
  "cover_prompt":     "string — English image generation prompt for the album cover, inspired by the journal entry and the visual style: {genre_style}",
  "lastfm_tags":      ["array of 4 to 6 lowercase Last.fm-compatible tag strings that match the mood and {genre} genre"]
}}

Constraints:
- Music genre: {genre}
- Era: {era}
- Tracklist will contain {track_count} real songs fetched separately; do NOT include track names in your JSON.
- The cover_prompt must be vivid and descriptive, suitable for an AI image generator.
- lastfm_tags must be real Last.fm tags (e.g. "melancholy", "rainy day", "indie", "dream pop").
{tag_guidance}

Journal entry:
\"\"\"{journal_text}\"\"\"
"""
    return prompt


def generate_album_metadata(
    journal_text: str,
    genre: str,
    era: str,
    track_count: int,
) -> dict:
    if not journal_text or not journal_text.strip():
        raise ValueError("Journal text cannot be empty.")

    prompt = _build_prompt(journal_text.strip(), genre, era, track_count)

    try:
        model = genai.GenerativeModel(model_name=GEMINI_MODEL)
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {e}") from e

    clean_text = strip_markdown_fences(raw_text)

    try:
        album_data = json.loads(clean_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Gemini returned invalid JSON.\n"
            f"Parse error: {e}\n"
            f"Raw response:\n{raw_text}"
        ) from e

    required_keys = {
        "album_name": "Unknown Album",
        "artist_name": "Unknown Artist",
        "year": "2000",
        "label": "Independent",
        "mood_description": "",
        "cover_prompt": "",
        "lastfm_tags": [],
    }
    for key, default in required_keys.items():
        if key not in album_data or album_data[key] is None:
            album_data[key] = default

    if not isinstance(album_data["lastfm_tags"], list):
        album_data["lastfm_tags"] = []

    return album_data


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import GEMINI_API_KEY as api_key
    configure_gemini(api_key)

    test_journal = (
        "I was looking at the sea in Izmir. It was raining softly, "
        "and an old song was playing through my headphones. "
        "I felt both peaceful and melancholic."
    )

    print("Sending journal to Gemini...")
    try:
        result = generate_album_metadata(
            journal_text=test_journal,
            genre="Indie",
            era="2000s",
            track_count=8,
        )
        print("\n── Gemini Album Metadata ──────────────────────")
        for key, value in result.items():
            print(f"  {key:20s}: {value}")
        print("───────────────────────────────────────────────\n")
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}")
