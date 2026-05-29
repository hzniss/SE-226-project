import tkinter as tk
import webbrowser
from tkinter import ttk

MAX_TRACKS = 14


class ResultPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#EEEFE0")

        style = ttk.Style(self)
        style.configure(
            "Listen.TButton",
            background="#A7C1A8",
            foreground="#ffffff",
            font=("Arial", 9, "bold"),
            padding=(10, 3),
        )
        style.map(
            "Listen.TButton",
            background=[("active", "#819A91"), ("pressed", "#819A91")],
            foreground=[("active", "#ffffff"), ("pressed", "#ffffff")],
        )

        tk.Label(
            self,
            text="Album Cover Studio",
            bg="#EEEFE0",
            fg="#819A91",
            font=("Arial", 22, "bold"),
        ).pack(pady=(30, 5))

        self.album_info_label = tk.Label(
            self,
            text="Generate an album to see results",
            bg="#EEEFE0",
            fg="#819A91",
            font=("Arial", 11),
            wraplength=900,
            justify="center",
        )
        self.album_info_label.pack(pady=(0, 10))

        self.status_label = tk.Label(
            self,
            text="",
            bg="#EEEFE0",
            fg="#5a6a5a",
            font=("Arial", 10, "italic"),
        )
        self.status_label.pack(pady=(0, 5))

        stage = tk.Frame(self, bg="#EEEFE0")
        stage.pack(expand=True, fill="both", padx=60, pady=20)

        cover_placeholder = tk.Frame(stage, bg="#D1D8BE", width=300, height=300)
        cover_placeholder.pack(side="left", padx=(0, 50))
        cover_placeholder.pack_propagate(False)
        self.cover_label = tk.Label(
            cover_placeholder,
            text="[ COVER IMAGE ]",
            bg="#D1D8BE",
            fg="#819A91",
            font=("Arial", 12, "bold"),
        )
        self.cover_label.pack(expand=True)
        self._cover_photo = None

        tracklist_container = tk.Frame(stage, bg="#EEEFE0")
        tracklist_container.pack(side="left", fill="both", expand=True)

        tk.Label(
            tracklist_container,
            text="Tracklist",
            bg="#EEEFE0",
            fg="#819A91",
            font=("Arial", 12, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        tracks_frame = tk.Frame(tracklist_container, bg="#EEEFE0")
        tracks_frame.pack(fill="both", expand=True)
        tracks_frame.columnconfigure(0, weight=1)  # title/artist
        tracks_frame.columnconfigure(1, weight=0)  # Listen button

        self.track_labels: list[tk.Label] = []
        self.track_buttons: list[ttk.Button] = []
        for i in range(1, MAX_TRACKS + 1):
            row = i - 1
            label = tk.Label(
                tracks_frame,
                text="",
                bg="#EEEFE0",
                fg="#819A91",
                font=("Arial", 11),
                anchor="w",
            )
            label.grid(row=row, column=0, sticky="w", pady=4, padx=(0, 8))
            self.track_labels.append(label)

            btn = ttk.Button(
                tracks_frame,
                text="Listen",
                style="Listen.TButton",
                command=lambda url=None: self._open_track_url(url),
            )
            btn.grid(row=row, column=1, sticky="e", pady=4, padx=(0, 0))
            btn.configure(state="disabled")
            btn.grid_remove()
            self.track_buttons.append(btn)

        self._show_empty_tracklist()

    def _show_empty_tracklist(self):
        for i, label in enumerate(self.track_labels, start=1):
            label.configure(text=f"{i}. —", fg="#c0c8b8")
        for btn in self.track_buttons:
            btn.configure(state="disabled", command=lambda url=None: self._open_track_url(url))
            btn.grid_remove()

    def set_album_metadata(self, album_data: dict):
        name = album_data.get("album_name") or "Unknown Album"
        artist = album_data.get("artist_name") or "Unknown Artist"
        year = album_data.get("year", "")
        label = album_data.get("label", "")
        mood = album_data.get("mood_description") or album_data.get("mood") or ""

        header = f"{name}  ·  {artist}  ·  {year}"
        if label:
            header += f"  ·  {label}"
        self.album_info_label.configure(text=header, fg="#4a5a4a", font=("Arial", 12, "bold"))

        if mood:
            self.status_label.configure(text=mood[:200] + ("…" if len(mood) > 200 else ""))
        else:
            self.status_label.configure(text="")

    def set_tracklist(self, tracks: list[dict]):
        for i, (label, btn) in enumerate(zip(self.track_labels, self.track_buttons)):
            if i < len(tracks):
                t = tracks[i]
                title = t.get("title", "Unknown")
                artist = t.get("artist", "Unknown")
                url = t.get("url") or ""
                label.configure(text=f"{i + 1}. {title} — {artist}", fg="#819A91")
                if url:
                    btn.grid()
                    btn.configure(
                        state="normal",
                        command=lambda u=url: self._open_track_url(u),
                    )
                else:
                    btn.configure(state="disabled", command=lambda url=None: self._open_track_url(url))
                    btn.grid_remove()
            else:
                label.configure(text="", fg="#819A91")
                btn.configure(state="disabled", command=lambda url=None: self._open_track_url(url))
                btn.grid_remove()

    def set_cover_image(self, pil_image):
        from services.image_service import pil_to_tkinter

        self._cover_photo = pil_to_tkinter(pil_image, size=(300, 300))
        self.cover_label.configure(image=self._cover_photo, text="")

    def clear_cover_image(self):
        self._cover_photo = None
        self.cover_label.configure(image="", text="[ COVER IMAGE ]")

    def set_loading(self, loading: bool):
        if loading:
            self.status_label.configure(text="Generating album… this may take a minute.")
            self.cover_label.configure(image="", text="Loading…")
            self._cover_photo = None
            for i, widget in enumerate(self.track_labels, start=1):
                widget.configure(text=f"{i}. …", fg="#a0a8a0")
            for btn in self.track_buttons:
                btn.configure(state="disabled", command=lambda url=None: self._open_track_url(url))
                btn.grid_remove()
        else:
            if self.status_label.cget("text") == "Generating album… this may take a minute.":
                self.status_label.configure(text="")

    def reset(self):
        self.album_info_label.configure(
            text="Generate an album to see results",
            fg="#819A91",
            font=("Arial", 11),
        )
        self.status_label.configure(text="")
        self.clear_cover_image()
        self._show_empty_tracklist()

    def _open_track_url(self, url: str | None):
        if not url:
            return
        try:
            webbrowser.open(url)
        except Exception:
            pass
