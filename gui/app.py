import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tkinter as tk
from tkinter import ttk
from input_panel import InputPanel
from result_panel import ResultPanel
#Creating the main window
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Album Cover Studio")
        self.geometry("1050x700")
        self.configure(bg="#EEEFE0") 
        
        style = ttk.Style(self)
        style.theme_use('clam')
        
        #result panel 
        self.result_panel = ResultPanel(self)
        self.result_panel.pack(side="top", fill="both", expand=True)

        #userinputpanel
        self.input_panel = InputPanel(self)
        self.input_panel.pack(side="bottom", fill="x")

if __name__ == "__main__":
    app = App()
    app.mainloop()