import tkinter as tk

class ResultPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#EEEFE0")
        
        #header
        tk.Label(self, text="Mood Song Creator", bg="#EEEFE0", fg="#819A91", font=("Arial", 22, "bold")).pack(pady=(30, 10))
        
        stage = tk.Frame(self, bg="#EEEFE0")
        stage.pack(expand=True, fill="both", padx=60, pady=40)
        
        # album cover (Can layout + Irmak set_cover_image)
        cover_placeholder = tk.Frame(stage, bg="#D1D8BE", width=300, height=300)
        cover_placeholder.pack(side="left", padx=(0, 50))
        cover_placeholder.pack_propagate(False)
        self.cover_label = tk.Label(
            cover_placeholder, text="[ COVER IMAGE ]", bg="#D1D8BE", fg="#819A91",
            font=("Arial", 12, "bold"),
        )
        self.cover_label.pack(expand=True)
        self._cover_photo = None
        
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

    # Call from main thread after cover generation (e.g. root.after from workflow).
    def set_cover_image(self, pil_image):
        from services.image_service import pil_to_tkinter
        self._cover_photo = pil_to_tkinter(pil_image, size=(300, 300))
        self.cover_label.configure(image=self._cover_photo, text="")

    def clear_cover_image(self):
        self._cover_photo = None
        self.cover_label.configure(image="", text="[ COVER IMAGE ]")