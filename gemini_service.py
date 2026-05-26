"""
gemini_service.py
-----------------
Kişi 2 — AI / Gemini Developer (Beyza)
Sorumlu requirement: REQ 4

REQ 4: Generate Album butonuna basılınca journal text ve parametreler Gemini'ye
       iletilir. Gemini; album_name, artist_name, year, label, mood_description,
       cover_prompt ve lastfm_tags alanlarını içeren bir JSON nesnesi döner.
       Uygulama bu JSON'u parse eder; Gemini yanıtı markdown code fence içinde
       gelirse bunlar temizlenir. Parse hataları yakalnır.
"""

import json
import google.generativeai as genai

# ─────────────────────────────────────────────
# SABIT — Model adı
# ─────────────────────────────────────────────

GEMINI_MODEL = "gemini-2.5-flash"

# ─────────────────────────────────────────────
# GENRE GÖRSEL STİL TANIMLAMALARI
# (cover_prompt'a eklenir — image_service ile tutarlı)
# ─────────────────────────────────────────────

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

# ─────────────────────────────────────────────
# GEMİNİ YAPILANDIRMA
# ─────────────────────────────────────────────

def configure_gemini(api_key: str) -> None:
    """
    Gemini API'yi verilen key ile yapılandırır.
    Bu fonksiyon uygulama başlarken (main.py veya workflow) bir kez çağrılmalıdır.

    Parametreler
    ------------
    api_key : Google AI Studio'dan alınan Gemini API key
    """
    genai.configure(api_key=api_key)


# ─────────────────────────────────────────────
# MARKDOWN CODE FENCE TEMİZLEME (REQ 4)
# ─────────────────────────────────────────────

def strip_markdown_fences(text: str) -> str:
    """
    Gemini bazen JSON yanıtını ```json ... ``` veya ``` ... ``` içinde döner.
    Bu fonksiyon bu fence'leri temizler ve saf JSON string'ini döner.

    Parametreler
    ------------
    text : Gemini'den gelen ham yanıt string'i

    Dönen değer
    -----------
    str  ->  Fence'lerden arındırılmış JSON string'i
    """
    text = text.strip()
    if text.startswith("```"):
        # İlk ``` satırını at
        text = text.split("```", 1)[1]
        # "json" etiketini at (```json durumu)
        if text.startswith("json"):
            text = text[4:]
        # Kapanış ``` varsa at
        if "```" in text:
            text = text.rsplit("```", 1)[0]
    return text.strip()


# ─────────────────────────────────────────────
# PROMPT OLUŞTURMA
# ─────────────────────────────────────────────

def _build_prompt(journal_text: str, genre: str, era: str, track_count: int) -> str:
    """
    Kullanıcı girdilerini kullanarak Gemini'ye gönderilecek prompt'u oluşturur.
    Prompt, Gemini'den YALNIZCA geçerli JSON döndürmesini ister.

    Dönen JSON şeması:
    {
        "album_name":        string  — yaratıcı/kurgusal albüm adı
        "artist_name":       string  — yaratıcı/kurgusal sanatçı adı
        "year":              string  — albümün kurgusal yayın yılı (era ile uyumlu)
        "label":             string  — kurgusal plak şirketi adı
        "mood_description":  string  — 1-2 cümlelik ruh hali özeti
        "cover_prompt":      string  — görsel üretim servisi için İngilizce prompt
        "lastfm_tags":       array   — 4-6 adet küçük harfli Last.fm tag string'i
    }
    """
    genre_style = GENRE_STYLES.get(genre, "artistic album cover")

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

Journal entry:
\"\"\"{journal_text}\"\"\"
"""
    return prompt


# ─────────────────────────────────────────────
# ALBUM METADATAsı ÜRETME (REQ 4)
# ─────────────────────────────────────────────

def generate_album_metadata(
    journal_text: str,
    genre: str,
    era: str,
    track_count: int,
) -> dict:
    """
    Kullanıcının journal metni ve parametrelerini Gemini'ye gönderir,
    albüm metadata'sını JSON olarak alır, parse eder ve döner.

    Gemini'nin yanıtı markdown code fence içinde gelirse otomatik temizlenir.
    JSON parse hatası oluşursa ValueError fırlatılır; çağıran taraf yakalamalıdır.

    Parametreler
    ------------
    journal_text : Kullanıcının mood/journal metin girişi
    genre        : Seçilen müzik türü (örn. "Indie", "Rock")
    era          : Seçilen dönem (örn. "1990s", "2000s")
    track_count  : Kullanıcının seçtiği şarkı sayısı (6–14)

    Dönen değer
    -----------
    dict içeren şu anahtarlar:
        album_name, artist_name, year, label,
        mood_description, cover_prompt, lastfm_tags

    Hatalar
    -------
    ValueError         — JSON parse başarısız olursa
    RuntimeError       — Gemini API hatası (ağ, kota vb.)
    """
    if not journal_text or not journal_text.strip():
        raise ValueError("Journal text cannot be empty.")

    prompt = _build_prompt(journal_text.strip(), genre, era, track_count)

    try:
        model = genai.GenerativeModel(model_name=GEMINI_MODEL)
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {e}") from e

    # Markdown fence temizleme
    clean_text = strip_markdown_fences(raw_text)

    # JSON parse
    try:
        album_data = json.loads(clean_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Gemini returned invalid JSON.\n"
            f"Parse error: {e}\n"
            f"Raw response:\n{raw_text}"
        ) from e

    # Zorunlu alanları kontrol et; eksikse boş değer koy (uygulamayı çökertme)
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

    # lastfm_tags her zaman liste olmalı
    if not isinstance(album_data["lastfm_tags"], list):
        album_data["lastfm_tags"] = []

    return album_data


# ─────────────────────────────────────────────
# MODÜLÜ DOĞRUDAN ÇALIŞTIRARAK TEST ET
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import os

    api_key = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
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
