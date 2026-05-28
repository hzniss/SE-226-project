import io
from typing import Optional
from urllib.parse import quote

import requests
from PIL import Image, ImageDraw
from services.gemini_service import GENRE_STYLES

POLLINATIONS_BASE = "https://image.pollinations.ai/prompt/"
POLLINATIONS_HEADERS = {"User-Agent": "AlbumCoverStudio/1.0"}

# Primary JSON key from gemini_service; alternates tried if missing.
COVER_PROMPT_KEY = "cover_prompt"


# Reads cover prompt from Gemini album_data.
def extract_cover_prompt(album_data: dict) -> str:
    if not album_data:
        return ""
    value = album_data.get(COVER_PROMPT_KEY, "")
    return str(value).strip() if value and str(value).strip() else ""


def _get_genre_style(genre: str) -> str:
    return GENRE_STYLES.get((genre or "").strip(), "artistic album cover")


# Combines Gemini's cover prompt with the chosen genre style description.
def build_full_prompt(cover_prompt: str, genre: str) -> str:
    genre_style = _get_genre_style(genre)
    return f"{cover_prompt}, {genre_style}, square format, high quality"


# Fetches album cover art from Pollinations.ai. Returns None on network or parse errors.
def generate_cover_image(cover_prompt: str, genre: str) -> Optional[Image.Image]:
    full_prompt = build_full_prompt(cover_prompt, genre)
    encoded = quote(full_prompt)
    url = f"{POLLINATIONS_BASE}{encoded}?width=600&height=600&nologo=true"

    try:
        response = requests.get(url, headers=POLLINATIONS_HEADERS, timeout=90)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content)).convert("RGB")
        return image
    except requests.exceptions.Timeout:
        print("[image_service] Timeout: Pollinations didn't respond.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[image_service] Request error: {e}")
        return None
    except Exception as e:
        print(f"[image_service] Image processing error: {e}")
        return None


# Main entry point for workflow/GUI. Always returns a PIL Image (real cover or placeholder).
def get_album_cover(cover_prompt: str, genre: str) -> Image.Image:
    if not cover_prompt or not str(cover_prompt).strip():
        return get_placeholder_image()
    image = generate_cover_image(str(cover_prompt).strip(), genre)
    return image if image is not None else get_placeholder_image()


# Builds cover from parsed Gemini metadata.
# Workflow: cover = get_album_cover_from_data(album_data, genre)
#           result_panel.set_cover_image(cover)  # main thread via root.after
#           save_album(album_data, cover, folder_path)  # core.exporter
def get_album_cover_from_data(album_data: dict, genre: str) -> Image.Image:
    return get_album_cover(extract_cover_prompt(album_data), genre)


# Returns a neutral gray image when generation fails or the prompt is empty.
def get_placeholder_image(size: tuple = (600, 600)) -> Image.Image:
    img = Image.new("RGB", size, color=(40, 40, 40))
    draw = ImageDraw.Draw(img)
    draw.text((size[0] // 2 - 70, size[1] // 2 - 8), "Cover unavailable", fill=(130, 130, 130))
    return img


# Resizes a PIL image and converts it to a Tkinter PhotoImage for display.
def pil_to_tkinter(image: Image.Image, size: tuple = (300, 300)):
    from PIL import ImageTk
    image_resized = image.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(image_resized)
