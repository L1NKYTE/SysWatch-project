# backend.py — Lógica de sistema: procesos, métricas, filtros y ordenamiento
import psutil, time, datetime, collections

from config import MAX_HIST, ram_history


def obtener_procesos(filtro="", col_orden=None, orden_asc=True):
    """Lee todos los procesos del sistema y devuelve la lista filtrada y ordenada"""
    datos = []

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
                           uptime(i['create_time']),
                           i['status'] or "?",
                           i['create_time']))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if col_orden:
        idx = {"PID": 0, "Proceso": 1, "RAM (MB)": 2,
               "CPU %": 3, "Tiempo Activo": 6, "Estado": 5}[col_orden]
        datos.sort(key=lambda x: x[idx], reverse=not orden_asc)

    return datos


def filtrar_datos(datos, filtro):
    """Filtra una lista de procesos ya cargada por nombre o PID."""
    f = filtro.lower()
    return [d for d in datos if f in d[1].lower() or f in str(d[0])]


def obtener_metricas():
    """Devuelve CPU % y snapshot de memoria virtual."""
    mem = psutil.virtual_memory()
    cpu = psutil.cpu_percent()
    return cpu, mem


def actualizar_historial(mem, cpu_hist):
    """Agrega los valores actuales a los historiales RAM y CPU."""
    ram_history.append(mem.percent)
    cpu_hist.append(psutil.cpu_percent())


def terminar_proceso(pid):
    """
    Intenta terminar el proceso con el PID dado.
    Devuelve (True, None) si OK, o (False, 'razon') si falla.
    """
    try:
        psutil.Process(pid).terminate()
        return True, None
    except psutil.AccessDenied:
        return False, "acceso_denegado"
    except psutil.NoSuchProcess:
        return False, "no_existe"


def uptime(create_time):
    """Convierte un timestamp de creación en texto legible de tiempo activo."""
    try:
        d, r = divmod(int(time.time() - create_time), 86400)
        h, r = divmod(r, 3600)
        m, s = divmod(r, 60)
        if d: return f"{d}d {h:02d}h {m:02d}m"
        if h: return f"{h}h {m:02d}m {s:02d}s"
        return f"{m}m {s:02d}s"
    except Exception:
        return "—"


def timestamp_ahora():
    """Devuelve la hora actual formateada para la barra de estado."""
    return datetime.datetime.now().strftime("%H:%M:%S")


def datetime_completo():
    """Devuelve fecha y hora completa para el reloj."""
    return datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
