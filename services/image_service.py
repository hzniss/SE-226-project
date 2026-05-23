import io
from typing import Optional
from urllib.parse import quote

import requests
from PIL import Image


GENRE_STYLES = {
    "Pop":         "vibrant colors, glossy aesthetic, modern pop album cover",
    "Rock":        "dark tones, gritty texture, electric energy, rock album cover",
    "Hip-Hop / Rap": "urban landscape, bold typography, street art style",
    "Electronic":  "neon lights, futuristic, glitch art, digital aesthetic",
    "Indie":       "lo-fi, warm film grain, vintage texture, indie aesthetic",
    "R&B / Soul":  "smooth gradients, warm tones, soulful mood",
    "Jazz":        "smoky atmosphere, noir lighting, classic jazz club feel",
    "Metal":       "dark, aggressive, gothic elements, metal album art",
    "Türk Pop":    "modern, colorful, Mediterranean warmth",
    "Klasik":      "elegant, orchestral hall, timeless classical aesthetic",
}

POLLINATIONS_BASE = "https://image.pollinations.ai/prompt/"

# JSON key for the cover prompt in Gemini album metadata (see gemini_service).
COVER_PROMPT_KEY = "cover_prompt"


# Combines Gemini's cover prompt with the selected genre's visual style.
def build_full_prompt(cover_prompt: str, genre: str) -> str:
    style = GENRE_STYLES.get(genre, "artistic album cover")
    return f"{cover_prompt}, {style}, square format, high quality"


# Fetches album cover art from Pollinations.ai. Returns None on network or parse errors.
def generate_cover_image(cover_prompt: str, genre: str) -> Optional[Image.Image]:
    full_prompt = build_full_prompt(cover_prompt, genre)
    encoded = quote(full_prompt)
    url = f"{POLLINATIONS_BASE}{encoded}?width=600&height=600&nologo=true"

    try:
        response = requests.get(url, timeout=90)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content)).convert("RGB")
        return image
    except requests.exceptions.Timeout:
        print("[image_service] Timeout: Pollinations yanıt vermedi.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[image_service] İstek hatası: {e}")
        return None
    except Exception as e:
        print(f"[image_service] Görsel işleme hatası: {e}")
        return None


# Main entry point for workflow/GUI. Always returns a PIL Image (real cover or placeholder).
def get_album_cover(cover_prompt: str, genre: str) -> Image.Image:
    if not cover_prompt or not str(cover_prompt).strip():
        return get_placeholder_image()
    image = generate_cover_image(str(cover_prompt).strip(), genre)
    return image if image is not None else get_placeholder_image()


# Builds cover from parsed Gemini metadata and the genre selected in the GUI.
def get_album_cover_from_data(album_data: dict, genre: str) -> Image.Image:
    cover_prompt = album_data.get(COVER_PROMPT_KEY, "")
    return get_album_cover(cover_prompt, genre)


# Returns a neutral gray image when generation fails or the prompt is empty.
def get_placeholder_image(size: tuple = (600, 600)) -> Image.Image:
    img = Image.new("RGB", size, color=(40, 40, 40))
    return img


# Resizes a PIL image and converts it to a Tkinter PhotoImage for display.
def pil_to_tkinter(image: Image.Image, size: tuple = (300, 300)):
    from PIL import ImageTk
    image_resized = image.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(image_resized)