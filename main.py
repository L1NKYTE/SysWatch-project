# main.py — Punto de entrada de SysWatch
import tkinter as tk
from ui import Monitor

if __name__ == "__main__":
    root = tk.Tk()
    app  = Monitor(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
