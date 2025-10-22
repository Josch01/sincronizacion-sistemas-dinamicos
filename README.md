# Simulador de Sincronización de Sistemas Dinámicos

Este proyecto es una aplicación de escritorio en Python (PyQt6) para el modelado, simulación y análisis de la sincronización en sistemas dinámicos acoplados.

Es una herramienta diseñada para estudiar cómo dos o más sistemas (ej. atractores caóticos como Lorenz o Rössler) pueden sincronizar su comportamiento bajo la influencia de un parámetro de acoplamiento `a`.

## Características Principales

* **Definición de Modelos:** Interfaz gráfica para definir múltiples sistemas de Ecuaciones Diferenciales Ordinarias (EDOs) de 3 variables (ej. `dx1/dt`, `dy1/dt`, ...).
* **Visualización 3D:** Renderización en tiempo real de las trayectorias del sistema (atractores) usando `pyqtgraph.opengl`.
* **Análisis de Sincronización:** Herramienta de "Análisis por Lotes" (`BatchThread`) que:
    1.  Itera sobre un parámetro de acoplamiento `a` en un rango definido.
    2.  Resuelve el sistema de EDOs acoplado (`scipy.integrate.solve_ivp`).
    3.  Calcula el error de sincronización (la diferencia absoluta entre variables, ej. `|x1 - x2|`) en estado estacionario.
    4.  Guarda los resultados (`a` vs. `error_max`) en un archivo `log.csv` para su posterior análisis.
* **Gestión de Proyectos:** Permite guardar y cargar configuraciones de modelos complejos en archivos `.json`.


## Tecnologías Utilizadas

* **Lenguaje:** Python 3
* **GUI:** PyQt6
* **Cómputo Científico:** SciPy (`solve_ivp`, `minimize_scalar`), NumPy
* **Visualización:** `pyqtgraph` (incluyendo `opengl`)
* **Manejo de Datos:** Pandas

## Estructura del Proyecto

El código está modularizado para una clara separación de responsabilidades:

* `main.py`: El punto de entrada que inicia la aplicación.
* `clases/`: Un paquete que contiene toda la lógica de la aplicación:
    * `modern_app.py`: La clase `MainWindow` principal.
    * `batch_thread.py`: El hilo `QThread` que maneja el cómputo pesado en segundo plano.
    * `resta_dialog.py`: El diálogo para configurar el análisis de sincronización.
    * `system_3d_view.py`: El widget de visualización 3D de OpenGL.
    * ...y otros componentes de la GUI (`equation_row.py`, `panel_graficas.py`, etc.).

## Cómo Usar

1.  Clonar el repositorio.
2.  (Recomendado) Crear un entorno virtual e instalar dependencias:
    ```bash
    pip install numpy pandas scipy pyqt6 pyqtgraph
    ```
3.  Ejecutar la aplicación:
    ```bash
    python main.py
    ```
4.  Definir las ecuaciones para el sistema 1 (x1, y1, z1) y el sistema 2 (x2, y2, z2). Asegúrate de incluir el parámetro de acoplamiento `a` donde corresponda.
5.  Usar el botón "Crear restas" para generar los archivos `info.txt` que definen el análisis.
6.  Ir al panel "Varias restas", cargar la carpeta creada y presionar "Iniciar".
7.  Los resultados se guardarán en los archivos `log.csv` dentro de cada subcarpeta de análisis.
