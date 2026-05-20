import requests
from PIL import Image
import io
from urllib.parse import quote


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


def build_full_prompt(cover_prompt: str, genre: str) -> str:

    style = GENRE_STYLES.get(genre, "artistic album cover")
    return f"{cover_prompt}, {style}, square format, high quality"


def generate_cover_image(cover_prompt: str, genre: str) -> Image.Image:

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


def get_placeholder_image(size: tuple = (600, 600)) -> Image.Image:

    img = Image.new("RGB", size, color=(40, 40, 40))
    return img


def pil_to_tkinter(image: Image.Image, size: tuple = (300, 300)):
    from PIL import ImageTk
    image_resized = image.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(image_resized)