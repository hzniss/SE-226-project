import tkinter as tk

MAX_TRACKS = 14


class ResultPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#EEEFE0")

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
        tracks_frame.columnconfigure(0, weight=1)
        tracks_frame.columnconfigure(1, weight=1)

        self.track_labels: list[tk.Label] = []
        for i in range(1, MAX_TRACKS + 1):
            col = 0 if i <= 7 else 1
            row = (i - 1) % 7
            label = tk.Label(
                tracks_frame,
                text="",
                bg="#EEEFE0",
                fg="#819A91",
                font=("Arial", 11),
                anchor="w",
            )
            label.grid(row=row, column=col, sticky="w", pady=6, padx=(0, 12))
            self.track_labels.append(label)

        self._show_empty_tracklist()

    def _show_empty_tracklist(self):
        for i, label in enumerate(self.track_labels, start=1):
            label.configure(text=f"{i}. —", fg="#c0c8b8")

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
        for i, widget in enumerate(self.track_labels):
            if i < len(tracks):
                t = tracks[i]
                title = t.get("title", "Unknown")
                artist = t.get("artist", "Unknown")
                widget.configure(text=f"{i + 1}. {title} — {artist}", fg="#819A91")
            else:
                widget.configure(text="", fg="#819A91")

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
