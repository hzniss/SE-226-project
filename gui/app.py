import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from core.album_generator import generate_full_album
from core.exporter import save_album
try:
    from gui.input_panel import InputPanel
    from gui.result_panel import ResultPanel
except ImportError:
    from input_panel import InputPanel
    from result_panel import ResultPanel


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Album Cover Studio")
        self.geometry("1050x700")
        self.configure(bg="#EEEFE0")

        self._last_album_data = None
        self._last_cover = None
        self._generation_running = False

        style = ttk.Style(self)
        style.theme_use("clam")

        self.result_panel = ResultPanel(self)
        self.result_panel.pack(side="top", fill="both", expand=True)

        self.input_panel = InputPanel(self)
        self.input_panel.pack(side="bottom", fill="x")

        self.input_panel.generate_btn.configure(command=self._on_generate)
        self.input_panel.export_btn.configure(command=self._on_export)

    def _on_generate(self):
        if self._generation_running:
            return

        ok, message = self.input_panel.validate_inputs()
        if not ok:
            messagebox.showwarning("Input required", message)
            return

        inputs = self.input_panel.get_generation_inputs()
        self._generation_running = True
        self.input_panel.set_busy(True)
        self.input_panel.set_export_enabled(False)
        self.result_panel.set_loading(True)

        def worker():
            try:
                album_data, cover = generate_full_album(
                    journal_text=inputs["journal_text"],
                    genre=inputs["genre"],
                    era=inputs["era"],
                    track_count=inputs["track_count"],
                )
                self.after(0, lambda: self._on_generate_success(album_data, cover))
            except Exception as e:
                self.after(0, lambda: self._on_generate_error(str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _on_generate_success(self, album_data: dict, cover):
        self._last_album_data = album_data
        self._last_cover = cover

        self.result_panel.set_loading(False)
        self.result_panel.set_album_metadata(album_data)
        self.result_panel.set_tracklist(album_data.get("tracks") or [])
        self.result_panel.set_cover_image(cover)

        self.input_panel.set_export_enabled(True)
        self._finish_generation()

        tracks = album_data.get("tracks") or []
        if not tracks:
            messagebox.showwarning(
                "No tracks found",
                "Album metadata was created but Last.fm returned no tracks. "
                "Check your Last.fm API key in config.py.",
            )

    def _on_generate_error(self, error_message: str):
        self.result_panel.set_loading(False)
        self._finish_generation()
        messagebox.showerror(
            "Generation failed",
            f"Could not generate the album.\n\n{error_message}",
        )

    def _finish_generation(self):
        self._generation_running = False
        self.input_panel.set_busy(False)

    def _on_export(self):
        if not self._last_album_data or not self._last_cover:
            messagebox.showinfo("Nothing to export", "Generate an album first.")
            return

        folder = filedialog.askdirectory(title="Choose folder to save album")
        if not folder:
            return

        result = save_album(self._last_album_data, self._last_cover, folder)
        if result["success"]:
            messagebox.showinfo(
                "Export complete",
                f"Saved:\n{result['json_path']}\n{result['png_path']}",
            )
        else:
            messagebox.showerror("Export failed", result.get("error") or "Unknown error")


if __name__ == "__main__":
    from main import configure_app

    configure_app()
    app = App()
    app.mainloop()
