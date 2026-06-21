# 🖥️ SysWatch --- Monitor de Sistema

## Descripción

SysWatch es una aplicación de escritorio desarrollada en Python que
permite monitorear el estado de un sistema operativo en tiempo real.

La aplicación muestra información sobre procesos activos, consumo de
CPU, memoria RAM y permite administrar procesos desde una interfaz
gráfica creada con Tkinter.

## Características

-   Monitoreo en tiempo real de CPU y RAM
-   Lista de procesos activos
-   Información de:
    -   PID
    -   Nombre del proceso
    -   Uso de memoria RAM
    -   Porcentaje de CPU
    -   Tiempo activo
    -   Estado del proceso
-   Búsqueda y filtrado de procesos
-   Ordenamiento de información por columnas
-   Finalización de procesos seleccionados
-   Gráficas dinámicas de rendimiento
-   Interfaz moderna estilo blanco/rojo

## Tecnologías utilizadas

-   Python 3
-   Tkinter
-   psutil
-   datetime
-   collections
-   time

## Instalación

Clona el repositorio:

``` bash
git clone https://github.com/TU-USUARIO/SysWatch.git
```

Entra a la carpeta:

``` bash
cd SysWatch
```

Instala las dependencias:

``` bash
pip install -r requirements.txt
```

## Ejecución

Ejecuta el programa:

``` bash
python monitorfinal.py
```

## Dependencias

Archivo `requirements.txt`:

``` txt
psutil
```

## Estructura del proyecto

    SysWatch/
    │
    ├── monitorfinal.py
    ├── requirements.txt
    └── README.md

## Objetivo

Proyecto desarrollado para aplicar conceptos de Sistemas Operativos,
monitoreo de recursos, administración de procesos e interfaces gráficas.

## Autor

Angel Alonso Romo Núñez

## Licencia

MIT License
