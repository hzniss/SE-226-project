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
from utils.threading_helper import WorkerThread


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Album Cover Studio")
        self.geometry("1050x760")
        self.minsize(900, 680)
        self.configure(bg="#EEEFE0")

        self._last_album_data = None
        self._last_cover = None
        self._generation_running = False

        style = ttk.Style(self)
        style.theme_use("clam")

        self.input_panel = InputPanel(self)
        self.result_panel = ResultPanel(self)

        # Pack bottom bar first so it always keeps ~180px; result area uses the rest.
        self.input_panel.pack(side="bottom", fill="x")
        self.result_panel.pack(side="top", fill="both", expand=True)

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

        # Uzun süren albüm üretimini arka plan thread'inde çalıştır (REQ 9).
        # WorkerThread; success/error/status callback'lerini root.after() ile
        # ana thread'e taşır, böylece GUI donmaz ve thread-safe kalır.
        WorkerThread(
            root=self,
            target=generate_full_album,
            kwargs={
                "journal_text": inputs["journal_text"],
                "genre": inputs["genre"],
                "era": inputs["era"],
                "track_count": inputs["track_count"],
            },
            on_success=lambda result: self._on_generate_success(*result),
            on_error=lambda e: self._on_generate_error(str(e)),
            on_status=self._on_status_update,
        ).start()

    def _on_generate_success(self, album_data: dict, cover):
        try:
            self._last_album_data = album_data
            self._last_cover = cover

            self.result_panel.set_loading(False)
            self.result_panel.set_album_metadata(album_data)
            self.result_panel.set_tracklist(album_data.get("tracks") or [])
            self.result_panel.set_cover_image(cover)

            self.input_panel.set_export_enabled(True)

            tracks = album_data.get("tracks") or []
            if not tracks:
                messagebox.showwarning(
                    "No tracks found",
                    "Album metadata was created but Last.fm returned no tracks. "
                    "Check your Last.fm API key in config.py.",
                )
        finally:
            self._finish_generation()

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

    def _on_status_update(self, message: str):
        """
        WorkerThread tarafından (root.after üzerinden) ana thread'de çağrılır.
        Mevcut adımı status label'da gösterir: "Gemini is thinking...",
        "Fetching tracks...", "Generating cover..." (REQ 9).
        """
        self.result_panel.status_label.configure(text=message)

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
