# config.py — Paleta de colores, constantes y widgets reutilizables
import tkinter as tk
import collections

# ── Paleta blanco / rojo
BG    = "#ffffff"
BG2   = "#f7f7f7"
ROJO  = "#d32f2f"
ROJO2 = "#ffebee"
TEXTO = "#1a1a1a"
GRIS  = "#9e9e9e"
BORDE = "#e0e0e0"
VERDE = "#2e7d32"

# ── Historial de métricas 
MAX_HIST    = 60
ram_history = collections.deque([0] * MAX_HIST, maxlen=MAX_HIST)


# ── Botón con hover
def boton(parent, texto, cmd, rojo=False):
    bg_n = ROJO  if rojo else BG2
    fg_n = "white" if rojo else ROJO
    bg_h = "#b71c1c" if rojo else ROJO2
    b = tk.Button(parent, text=texto, command=cmd, relief="flat",
                  bg=bg_n, fg=fg_n, font=("Segoe UI", 9, "bold"),
                  cursor="hand2", padx=12, pady=5, bd=0)
    b.bind("<Enter>", lambda e: b.config(bg=bg_h))
    b.bind("<Leave>", lambda e: b.config(bg=bg_n))
    return b


# ── Tarjeta de métrica
def tarjeta(parent, titulo, color):
    f = tk.Frame(parent, bg="white", highlightthickness=1,
                 highlightbackground=BORDE)
    tk.Label(f, text=titulo, bg="white", fg=GRIS,
             font=("Segoe UI", 8)).pack(pady=(10, 2))
    val = tk.Label(f, text="0%", bg="white", fg=color,
                   font=("Segoe UI", 22, "bold"))
    val.pack(pady=(0, 10))
    return f, val
