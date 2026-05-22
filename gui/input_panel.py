import tkinter as tk
from tkinter import ttk

class InputPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#D1D8BE", height=180, padx=20, pady=20)
        self.pack_propagate(False)

        self.columnconfigure(1, weight=1)

        settings_frame = tk.Frame(self, bg="#D1D8BE")
        settings_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        #label styling
        lbl_style = {"bg": "#D1D8BE", "fg": "#819A91", "font": ("Arial", 9, "bold")}
        
        tk.Label(settings_frame, text="Genre", **lbl_style).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.genre_combo = ttk.Combobox(settings_frame, values=["Classical", "Rock", "Pop", "Jazz"], state="readonly", width=12)
        self.genre_combo.set("Classical")
        self.genre_combo.grid(row=0, column=1, sticky="w", pady=(0, 5), padx=(5, 0))

        tk.Label(settings_frame, text="Era", **lbl_style).grid(row=1, column=0, sticky="w", pady=(0, 5))
        self.era_combo = ttk.Combobox(settings_frame, values=["1980s", "1990s", "2000s"], state="readonly", width=12)
        self.era_combo.set("2000s")
        self.era_combo.grid(row=1, column=1, sticky="w", pady=(0, 5), padx=(5, 0))

        tk.Label(settings_frame, text="Tracks", **lbl_style).grid(row=2, column=0, sticky="w")
        self.track_spinbox = ttk.Spinbox(settings_frame, from_=1, to=20, width=10)
        self.track_spinbox.set(10)
        self.track_spinbox.grid(row=2, column=1, sticky="w", padx=(5, 0))

        #moodframe
        mood_frame = tk.Frame(self, bg="#D1D8BE")
        mood_frame.grid(row=0, column=1, sticky="nsew", padx=20)

        tk.Label(mood_frame, text="YOUR MOOD", bg="#D1D8BE", fg="#819A91", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        self.mood_text = tk.Text(mood_frame, height=4, bg="#EEEFE0", fg="#444444", insertbackground="#819A91", relief="flat", highlightthickness=1, highlightbackground="#A7C1A8", font=("Arial", 11), padx=10, pady=10)
        self.mood_text.pack(fill="both", expand=True)

        btn_frame = tk.Frame(self, bg="#D1D8BE", width=150)
        btn_frame.grid(row=0, column=2, sticky="nsew", padx=(20, 0))
        btn_frame.pack_propagate(False)

        style = ttk.Style()
        style.configure("Generate.TButton", background="#A7C1A8", foreground="#ffffff", font=("Arial", 12, "bold"))
        style.map("Generate.TButton", background=[("active", "#819A91")])

        self.generate_btn = ttk.Button(btn_frame, text="GENERATE\nALBUM", style="Generate.TButton")
        self.generate_btn.pack(fill="both", expand=True)