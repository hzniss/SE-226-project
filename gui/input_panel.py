import tkinter as tk
from tkinter import ttk

MIN_TRACKS = 6
MAX_TRACKS = 14
PROJECT_GENRES = [
    "Pop", "Rock", "Hip-Hop / Rap", "Electronic", "Indie",
    "R&B / Soul", "Jazz", "Metal", "Türk Pop", "Klasik",
]


class InputPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#D1D8BE", height=180, padx=20, pady=20)
        self.pack_propagate(False)

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)
        self.rowconfigure(0, weight=1)

        settings_frame = tk.Frame(self, bg="#D1D8BE")
        settings_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        lbl_style = {"bg": "#D1D8BE", "fg": "#819A91", "font": ("Arial", 9, "bold")}

        tk.Label(settings_frame, text="Genre", **lbl_style).grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )
        self.genre_combo = ttk.Combobox(
            settings_frame, values=PROJECT_GENRES, state="readonly", width=14
        )
        self.genre_combo.set("Indie")
        self.genre_combo.grid(row=0, column=1, sticky="w", pady=(0, 5), padx=(5, 0))

        tk.Label(settings_frame, text="Era", **lbl_style).grid(
            row=1, column=0, sticky="w", pady=(0, 5)
        )
        self.era_combo = ttk.Combobox(
            settings_frame,
            values=["1970s", "1980s", "1990s", "2000s", "2010s", "2020s"],
            state="readonly",
            width=14,
        )
        self.era_combo.set("2000s")
        self.era_combo.grid(row=1, column=1, sticky="w", pady=(0, 5), padx=(5, 0))

        tk.Label(settings_frame, text="Tracks", **lbl_style).grid(row=2, column=0, sticky="w")
        self.track_spinbox = ttk.Spinbox(
            settings_frame, from_=MIN_TRACKS, to=MAX_TRACKS, width=12
        )
        self.track_spinbox.set(str(MIN_TRACKS))
        self.track_spinbox.grid(row=2, column=1, sticky="w", padx=(5, 0))

        mood_frame = tk.Frame(self, bg="#D1D8BE")
        mood_frame.grid(row=0, column=1, sticky="nsew", padx=20)

        tk.Label(
            mood_frame,
            text="YOUR MOOD",
            bg="#D1D8BE",
            fg="#819A91",
            font=("Arial", 10, "bold"),
        ).pack(anchor="w", pady=(0, 5))

        self.mood_text = tk.Text(
            mood_frame,
            height=4,
            bg="#EEEFE0",
            fg="#444444",
            insertbackground="#819A91",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#A7C1A8",
            font=("Arial", 11),
            padx=10,
            pady=10,
        )
        self.mood_text.pack(fill="both", expand=True)

        btn_frame = tk.Frame(self, bg="#D1D8BE", width=150)
        btn_frame.grid(row=0, column=2, sticky="nsew", padx=(20, 0))
        btn_frame.pack_propagate(False)

        style = ttk.Style()
        style.configure(
            "Generate.TButton",
            background="#A7C1A8",
            foreground="#ffffff",
            font=("Arial", 11, "bold"),
        )
        style.map("Generate.TButton", background=[("active", "#819A91")])
        style.configure(
            "Export.TButton",
            background="#819A91",
            foreground="#ffffff",
            font=("Arial", 10, "bold"),
        )
        style.map("Export.TButton", background=[("active", "#6a7a6a")])

        self.generate_btn = ttk.Button(
            btn_frame, text="GENERATE\nALBUM", style="Generate.TButton"
        )
        self.generate_btn.pack(fill="both", expand=True, pady=(0, 6))

        self.export_btn = ttk.Button(
            btn_frame, text="EXPORT", style="Export.TButton", state="disabled"
        )
        self.export_btn.pack(fill="x")

    def get_generation_inputs(self) -> dict:
        return {
            "journal_text": self.mood_text.get("1.0", "end").strip(),
            "genre": self.genre_combo.get(),
            "era": self.era_combo.get(),
            "track_count": int(self.track_spinbox.get()),
        }

    def validate_inputs(self) -> tuple[bool, str]:
        inputs = self.get_generation_inputs()
        if not inputs["journal_text"]:
            return False, "Please write something about your mood before generating."
        try:
            count = inputs["track_count"]
        except ValueError:
            return False, "Track count must be a number."
        if count < MIN_TRACKS or count > MAX_TRACKS:
            return False, f"Track count must be between {MIN_TRACKS} and {MAX_TRACKS}."
        if not inputs["genre"]:
            return False, "Please select a genre."
        return True, ""

    def set_busy(self, busy: bool):
        state = "disabled" if busy else "normal"
        self.generate_btn.configure(state=state)
        if busy:
            self.generate_btn.configure(text="GENERATING…")
        else:
            self.generate_btn.configure(text="GENERATE\nALBUM")

    def set_export_enabled(self, enabled: bool):
        self.export_btn.configure(state="normal" if enabled else "disabled")
