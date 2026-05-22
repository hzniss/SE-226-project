import tkinter as tk

class ResultPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#EEEFE0")
        
        #header
        tk.Label(self, text="Mood Song Creator", bg="#EEEFE0", fg="#819A91", font=("Arial", 22, "bold")).pack(pady=(30, 10))
        
        stage = tk.Frame(self, bg="#EEEFE0")
        stage.pack(expand=True, fill="both", padx=60, pady=40)
        
        #placeholder for album cover
        cover_placeholder = tk.Frame(stage, bg="#D1D8BE", width=300, height=300)
        cover_placeholder.pack(side="left", padx=(0, 50))
        cover_placeholder.pack_propagate(False)
        tk.Label(cover_placeholder, text="[ COVER IMAGE ]", bg="#D1D8BE", fg="#819A91", font=("Arial", 12, "bold")).pack(expand=True)
        
        #placeholder for tracks
        tracklist_container = tk.Frame(stage, bg="#EEEFE0")
        tracklist_container.pack(side="left", fill="both", expand=True)
        
        tk.Label(tracklist_container, text="Tracklist", bg="#EEEFE0", fg="#819A91", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 20))
        
        tracks_frame = tk.Frame(tracklist_container, bg="#EEEFE0")
        tracks_frame.pack(fill="both", expand=True)
        tracks_frame.columnconfigure(0, weight=1)
        tracks_frame.columnconfigure(1, weight=1)
        
        #track color setter
        for i in range(1, 11):
            col = 0 if i <= 5 else 1
            row = (i - 1) % 5
            tk.Label(tracks_frame, text=f"{i}. Song Title Placeholder", bg="#EEEFE0", fg="#819A91", font=("Arial", 11)).grid(row=row, column=col, sticky="w", pady=8)