"""Application entry point — configures API keys and launches the GUI."""
import os


def configure_app() -> None:
    """Load API keys from config.py and/or environment variables."""
    from services import gemini_service, lastfm_service

    gemini_key = os.environ.get("GEMINI_API_KEY")
    try:
        import config

        gemini_key = gemini_key or getattr(config, "GEMINI_API_KEY", None)
    except ImportError:
        pass

    if not gemini_key:
        raise RuntimeError(
            "Gemini API key missing. Set GEMINI_API_KEY in the environment "
            "or add GEMINI_API_KEY to config.py (see config.example.py)."
        )

    gemini_service.configure_gemini(gemini_key)

    lastfm_key = os.environ.get("LASTFM_API_KEY")
    try:
        import config

        if not lastfm_key:
            lastfm_key = getattr(config, "LASTFM_API_KEY", None)
    except ImportError:
        pass

    if not lastfm_key:
        raise RuntimeError(
            "Last.fm API key missing. Set LASTFM_API_KEY in the environment "
            "or add LASTFM_API_KEY to config.py (see config.example.py)."
        )

    lastfm_service.configure_lastfm(lastfm_key)


def main() -> None:
    configure_app()
    from gui.app import App

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
