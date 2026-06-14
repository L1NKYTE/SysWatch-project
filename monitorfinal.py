import tkinter as tk
from tkinter import ttk, messagebox
import psutil, time, datetime, collections

# ── Paleta blanco / rojo ──────────────────────────────────────────────────────
BG    = "#ffffff"
BG2   = "#f7f7f7"
ROJO  = "#d32f2f"
ROJO2 = "#ffebee"
TEXTO = "#1a1a1a"
GRIS  = "#9e9e9e"
BORDE = "#e0e0e0"
VERDE = "#2e7d32"

MAX_HIST    = 60
ram_history = collections.deque([0] * MAX_HIST, maxlen=MAX_HIST)

# ── Botón con hover ───────────────────────────────────────────────────────────
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

# ── Tarjeta de métrica ────────────────────────────────────────────────────────
def tarjeta(parent, titulo, color):
    f = tk.Frame(parent, bg="white", highlightthickness=1,
                 highlightbackground=BORDE)
    tk.Label(f, text=titulo, bg="white", fg=GRIS,
             font=("Segoe UI", 8)).pack(pady=(10, 2))
    val = tk.Label(f, text="0%", bg="white", fg=color,
                   font=("Segoe UI", 22, "bold"))
    val.pack(pady=(0, 10))
    return f, val


class Monitor:
    def __init__(self, root):
        self.root   = root
        self.root.title("SysWatch — Monitor de Sistema")
        self.root.geometry("940x620")
        self.root.configure(bg=BG)
        self.root.minsize(780, 520)

        self.running   = True
        self.datos     = []
        self.col_orden = None
        self.orden_asc = True
        self.cpu_hist  = collections.deque([0] * MAX_HIST, maxlen=MAX_HIST)

        self._estilos()
        self._cabecera()
        self._pestanas()
        self._barra_estado()

        self.actualizar_procesos()
        self.actualizar_grafica()

    # ── Estilos ───────────────────────────────────────────────────────────────
    def _estilos(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("TNotebook", background=BG, borderwidth=0)
        s.configure("TNotebook.Tab", background=BG2, foreground=GRIS,
                    padding=[18, 8], font=("Segoe UI", 10), borderwidth=0)
        s.map("TNotebook.Tab",
              background=[("selected", BG)],
              foreground=[("selected", ROJO)])
        s.configure("Treeview", background=BG, foreground=TEXTO,
                    fieldbackground=BG, rowheight=28, font=("Segoe UI", 9))
        s.configure("Treeview.Heading", background=BG2, foreground=ROJO,
                    relief="flat", font=("Segoe UI", 9, "bold"))
        s.map("Treeview", background=[("selected", ROJO)],
              foreground=[("selected", "white")])
        s.configure("Vertical.TScrollbar", background=BG2, troughcolor=BG,
                    borderwidth=0)

    # ── Cabecera ──────────────────────────────────────────────────────────────
    def _cabecera(self):
        # Franja roja principal
        cab = tk.Frame(self.root, bg=ROJO, height=60)
        cab.pack(fill="x")
        cab.pack_propagate(False)

        # Logo + título
        logo = tk.Frame(cab, bg=ROJO)
        logo.pack(side="left", padx=18, pady=8)
        tk.Label(logo, text="◈", bg=ROJO, fg="white",
                 font=("Segoe UI", 20)).pack(side="left")
        tk.Label(logo, text=" SysWatch", bg=ROJO, fg="white",
                 font=("Segoe UI", 16, "bold")).pack(side="left")
        tk.Label(logo, text="  Monitor de Sistema", bg=ROJO, fg="#ffcdd2",
                 font=("Segoe UI", 9)).pack(side="left", pady=(8, 0))

        # Tarjetas métricas en la cabecera
        metricas = tk.Frame(cab, bg=ROJO)
        metricas.pack(side="right", padx=18)

        self._ram_badge = self._badge(metricas, "RAM", "0%")
        self._ram_badge.pack(side="right", padx=6)
        self._cpu_badge = self._badge(metricas, "CPU", "0%")
        self._cpu_badge.pack(side="right", padx=6)

        # Línea de acento debajo de la cabecera
        tk.Frame(self.root, bg="#b71c1c", height=3).pack(fill="x")

    def _badge(self, parent, etiqueta, valor):
        """Pequeña pastilla blanca con etiqueta y valor."""
        f = tk.Frame(parent, bg="white", padx=10, pady=4)
        tk.Label(f, text=etiqueta, bg="white", fg=ROJO,
                 font=("Segoe UI", 7, "bold")).pack()
        lbl = tk.Label(f, text=valor, bg="white", fg=TEXTO,
                       font=("Segoe UI", 13, "bold"))
        lbl.pack()
        # guardamos referencia al label de valor
        f._val = lbl
        return f

    # ── Pestañas ──────────────────────────────────────────────────────────────
    def _pestanas(self):
        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=0, pady=0)

        t1 = tk.Frame(nb, bg=BG)
        nb.add(t1, text="   Procesos   ")
        self._tab_procesos(t1)

        t2 = tk.Frame(nb, bg=BG)
        nb.add(t2, text="   Rendimiento   ")
        self._tab_rendimiento(t2)

    # ── Tab Procesos ──────────────────────────────────────────────────────────
    def _tab_procesos(self, p):
        # — Toolbar —
        bar = tk.Frame(p, bg=BG, pady=10)
        bar.pack(fill="x", padx=16)

        # Cuadro de búsqueda con borde redondeado simulado
        busq = tk.Frame(bar, bg=BG2, highlightthickness=1,
                        highlightbackground=BORDE)
        tk.Label(busq, text="🔍", bg=BG2, fg=GRIS,
                 font=("Segoe UI", 10)).pack(side="left", padx=(8, 2))
        self.filtro = tk.Entry(busq, bg=BG2, fg=TEXTO, relief="flat",
                               font=("Segoe UI", 10), width=22,
                               insertbackground=ROJO)
        self.filtro.pack(side="left", ipady=5, padx=(0, 8))
        self.filtro.bind("<KeyRelease>", lambda e: self._filtrar())
        busq.pack(side="left")

        boton(bar, "↺  Refrescar", self.actualizar_procesos).pack(
            side="left", padx=10)

        boton(bar, "✕  Finalizar Proceso", self.finalizar_proceso,
              rojo=True).pack(side="right")

        self.lbl_count = tk.Label(bar, text="", bg=BG, fg=GRIS,
                                   font=("Segoe UI", 9))
        self.lbl_count.pack(side="right", padx=12)

        # Separador
        tk.Frame(p, bg=BORDE, height=1).pack(fill="x", padx=16)

        # — Tabla —
        frame = tk.Frame(p, bg=BG)
        frame.pack(fill="both", expand=True, padx=16, pady=10)

        cols = ("PID", "Proceso", "RAM (MB)", "CPU %", "Tiempo Activo", "Estado")
        self.tabla = ttk.Treeview(frame, columns=cols, show="headings")
        anchos = {"PID": 65, "Proceso": 240, "RAM (MB)": 95,
                  "CPU %": 72, "Tiempo Activo": 150, "Estado": 90}
        for c in cols:
            self.tabla.heading(c, text=c,
                               command=lambda col=c: self._ordenar(col))
            self.tabla.column(c, width=anchos[c],
                              anchor="w" if c == "Proceso" else "center")

        self.tabla.tag_configure("par",      background=BG)
        self.tabla.tag_configure("impar",    background=BG2)
        self.tabla.tag_configure("alto_ram", foreground="#e65100")
        self.tabla.tag_configure("alto_cpu", foreground=ROJO)

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tabla.pack(fill="both", expand=True)

    # ── Tab Rendimiento ───────────────────────────────────────────────────────
    def _tab_rendimiento(self, p):
        p.columnconfigure(0, weight=1)
        p.columnconfigure(1, weight=1)
        p.rowconfigure(1, weight=1)

        # — Panel RAM —
        panel_ram = tk.Frame(p, bg=BG)
        panel_ram.grid(row=0, column=0, sticky="w", padx=20, pady=(16, 6))

        tk.Label(panel_ram, text="Memoria RAM", bg=BG, fg=ROJO,
                 font=("Segoe UI", 12, "bold")).pack(side="left")

        # Info en línea
        info_ram = tk.Frame(p, bg=BG)
        info_ram.grid(row=0, column=0, sticky="e", padx=20, pady=(16, 6))
        self.lbl_total = tk.Label(info_ram, text="Total —", bg=BG, fg=GRIS,
                                   font=("Segoe UI", 8))
        self.lbl_total.pack(side="left", padx=4)
        self.lbl_usada = tk.Label(info_ram, text="Usada —", bg=BG, fg=TEXTO,
                                   font=("Segoe UI", 8, "bold"))
        self.lbl_usada.pack(side="left", padx=4)
        self.lbl_libre = tk.Label(info_ram, text="Libre —", bg=BG, fg=VERDE,
                                   font=("Segoe UI", 8))
        self.lbl_libre.pack(side="left", padx=4)

        self.canvas_ram = tk.Canvas(p, bg=BG, highlightthickness=1,
                                    highlightbackground=BORDE)
        self.canvas_ram.grid(row=1, column=0, sticky="nsew",
                             padx=(20, 8), pady=(0, 16))

        # — Panel CPU —
        tk.Label(p, text="CPU", bg=BG, fg=VERDE,
                 font=("Segoe UI", 12, "bold")).grid(
            row=0, column=1, sticky="w", padx=8, pady=(16, 6))

        self.canvas_cpu = tk.Canvas(p, bg=BG, highlightthickness=1,
                                    highlightbackground=BORDE)
        self.canvas_cpu.grid(row=1, column=1, sticky="nsew",
                             padx=(8, 20), pady=(0, 16))

    # ── Barra de estado ───────────────────────────────────────────────────────
    def _barra_estado(self):
        bar = tk.Frame(self.root, bg=BG2, height=26)
        bar.pack(fill="x", side="bottom")
        tk.Frame(bar, bg=BORDE, height=1).pack(fill="x")
        self.lbl_status = tk.Label(bar, text="Iniciando…", bg=BG2, fg=GRIS,
                                   font=("Segoe UI", 8), anchor="w")
        self.lbl_status.pack(side="left", padx=14)
        self.lbl_hora = tk.Label(bar, text="", bg=BG2, fg=GRIS,
                                  font=("Segoe UI", 8))
        self.lbl_hora.pack(side="right", padx=14)
        self._tick()

    def _tick(self):
        self.lbl_hora.configure(
            text=datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
        self.root.after(1000, self._tick)

    # ── Lógica de procesos ────────────────────────────────────────────────────
    def actualizar_procesos(self):
        if not self.running:
            return
        filtro = self.filtro.get().lower()
        datos  = []

        for proc in psutil.process_iter(
                ['pid', 'name', 'memory_info', 'cpu_percent',
                 'create_time', 'status']):
            try:
                i = proc.info
                pid, nombre = i['pid'], i['name'] or "—"
                ram = i['memory_info'].rss / 1_048_576
                cpu = i['cpu_percent'] or 0.0
                if filtro and filtro not in nombre.lower() \
                           and filtro not in str(pid):
                    continue
                datos.append((pid, nombre, ram, cpu,
                               self._uptime(i['create_time']),
                               i['status'] or "?",
                               i['create_time']))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        if self.col_orden:
            idx = {"PID":0,"Proceso":1,"RAM (MB)":2,
                   "CPU %":3,"Tiempo Activo":6,"Estado":5}[self.col_orden]
            datos.sort(key=lambda x: x[idx], reverse=not self.orden_asc)

        self.datos = datos
        self._renderizar(datos)

        cpu_t = psutil.cpu_percent()
        ram_i = psutil.virtual_memory()
        self._cpu_badge._val.configure(text=f"{cpu_t:.0f}%")
        self._ram_badge._val.configure(text=f"{ram_i.percent:.0f}%")

        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.lbl_status.configure(
            text=f"Actualizado: {ts}  ·  {len(datos)} procesos visibles")
        self.lbl_count.configure(text=f"{len(datos)} procesos")
        self.root.after(2000, self.actualizar_procesos)

    def _renderizar(self, datos):
        sel_pid = None
        sel = self.tabla.selection()
        if sel:
            try:
                sel_pid = int(self.tabla.item(sel[0])["values"][0])
            except Exception:
                pass

        self.tabla.delete(*self.tabla.get_children())
        new_sel = None

        for i, (pid, nombre, ram, cpu, uptime, estado, _) in enumerate(datos):
            tags = ["par" if i % 2 == 0 else "impar"]
            if ram > 500: tags.append("alto_ram")
            if cpu > 50:  tags.append("alto_cpu")
            iid = self.tabla.insert("", "end",
                                    values=(pid, nombre, f"{ram:.1f}",
                                            f"{cpu:.1f}", uptime, estado),
                                    tags=tuple(tags))
            if pid == sel_pid:
                new_sel = iid

        if new_sel:
            self.tabla.selection_set(new_sel)
            self.tabla.see(new_sel)

    def _filtrar(self):
        f = self.filtro.get().lower()
        r = [d for d in self.datos if f in d[1].lower() or f in str(d[0])]
        self._renderizar(r)
        self.lbl_count.configure(text=f"{len(r)} procesos")

    def _ordenar(self, col):
        self.orden_asc = not self.orden_asc if self.col_orden == col else True
        self.col_orden = col
        self._filtrar()

    def finalizar_proceso(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Sin selección",
                                   "Selecciona un proceso primero.")
            return
        v      = self.tabla.item(sel[0])["values"]
        pid    = int(v[0])
        nombre = v[1]
        if not messagebox.askyesno("Confirmar",
                                    f"¿Finalizar '{nombre}'  (PID {pid})?"):
            return
        try:
            psutil.Process(pid).terminate()
            messagebox.showinfo("Listo", f"'{nombre}' finalizado.")
            self.actualizar_procesos()
        except psutil.AccessDenied:
            messagebox.showerror("Sin permisos",
                                  "Ejecuta el programa como administrador.")
        except psutil.NoSuchProcess:
            messagebox.showinfo("Info", "El proceso ya no existe.")
            self.actualizar_procesos()

    # ── Gráficas ──────────────────────────────────────────────────────────────
    def actualizar_grafica(self):
        if not self.running:
            return
        mem = psutil.virtual_memory()
        ram_history.append(mem.percent)
        self.cpu_hist.append(psutil.cpu_percent())

        self.lbl_total.configure(text=f"Total {mem.total/1073741824:.1f} GB")
        self.lbl_usada.configure(
            text=f"Usada {mem.used/1073741824:.1f} GB ({mem.percent:.0f}%)")
        self.lbl_libre.configure(
            text=f"Libre {mem.available/1073741824:.1f} GB")

        self._grafica(self.canvas_ram, ram_history, ROJO,  "#ffcdd2", "RAM %")
        self._grafica(self.canvas_cpu, self.cpu_hist, VERDE, "#c8e6c9", "CPU %")
        self.root.after(1000, self.actualizar_grafica)

    def _grafica(self, cv, hist, color, relleno, label):
        cv.delete("all")
        w, h = cv.winfo_width(), cv.winfo_height()
        if w < 10 or h < 10:
            return

        pl, pr, pt, pb = 40, 12, 14, 26
        gw, gh = w-pl-pr, h-pt-pb

        # Fondo con sombra ligera
        cv.create_rectangle(pl, pt, pl+gw, pt+gh,
                            fill="white", outline=BORDE, width=1)

        # Cuadrícula y etiquetas
        for pct in (25, 50, 75, 100):
            y = pt + gh - int(gh * pct / 100)
            cv.create_line(pl, y, pl+gw, y, fill=BORDE, dash=(4, 6))
            cv.create_text(pl-4, y, text=str(pct), fill=GRIS,
                           font=("Segoe UI", 7), anchor="e")

        cv.create_text(10, pt+gh//2, text=label, fill=color,
                       font=("Segoe UI", 8, "bold"), angle=90)

        if len(hist) < 2:
            return

        step = gw / (MAX_HIST - 1)
        pts  = [(pl + i*step, pt + gh - (v/100)*gh)
                for i, v in enumerate(hist)]

        # Área rellena
        poly = [pl, pt+gh] + [c for pt2 in pts for c in pt2] \
               + [pts[-1][0], pt+gh]
        cv.create_polygon(poly, fill=relleno, outline="")

        # Línea principal
        for i in range(len(pts)-1):
            cv.create_line(*pts[i], *pts[i+1],
                           fill=color, width=2, smooth=True)

        # Punto actual al final de la línea
        lx, ly = pts[-1]
        cv.create_oval(lx-4, ly-4, lx+4, ly+4, fill=color, outline="white",
                       width=2)

        # Valor actual en esquina
        cur = list(hist)[-1]
        cv.create_text(pl+gw-6, pt+8, text=f"{cur:.0f}%",
                       fill=color, font=("Segoe UI", 12, "bold"), anchor="e")

        # Eje X
        for i in range(0, MAX_HIST, 15):
            cv.create_text(pl + i*step, pt+gh+12,
                           text=f"-{MAX_HIST-i}s", fill=GRIS,
                           font=("Segoe UI", 7))

    # ── Utilidades ────────────────────────────────────────────────────────────
    @staticmethod
    def _uptime(ct):
        try:
            d, r = divmod(int(time.time()-ct), 86400)
            h, r = divmod(r, 3600)
            m, s = divmod(r, 60)
            if d: return f"{d}d {h:02d}h {m:02d}m"
            if h: return f"{h}h {m:02d}m {s:02d}s"
            return f"{m}m {s:02d}s"
        except Exception:
            return "—"

    def on_close(self):
        self.running = False
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app  = Monitor(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
