from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class PanelGraficas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        self.canvas_2d = FigureCanvas(Figure(figsize=(5, 4)))
        self.ax_2d = self.canvas_2d.figure.subplots()
        self.ax_2d.set_xlabel("Tiempo")
        self.ax_2d.set_ylabel("Valor")
        self.ax_2d.set_title("Evolución de las Variables")
        self.ax_2d.grid(True)
        
        self.canvas_3d = FigureCanvas(Figure(figsize=(5, 4)))
        self.ax_3d = self.canvas_3d.figure.add_subplot(111, projection='3d')
        self.ax_3d.set_xlabel("X")
        self.ax_3d.set_ylabel("Y")
        self.ax_3d.set_zlabel("Z")
        self.ax_3d.set_title("Espacio de Fases 3D")

        self.layout.addWidget(self.canvas_2d)
        self.layout.addWidget(self.canvas_3d)

    def plot_simulation_batch(self, results):
        self.ax_2d.clear()
        self.ax_3d.clear()

        # results can be a single sol object or a list of sol objects
        if not isinstance(results, list):
            results = [results]

        for sol in results:
            if sol and sol.success:
                t = sol.t
                y = sol.y
                
                # Gráfica 2D
                for i in range(y.shape[0]):
                    self.ax_2d.plot(t, y[i], label=f'y_{i+1}(t)')

                # Gráfica 3D
                if y.shape[0] >= 3:
                    self.ax_3d.plot(y[0], y[1], y[2])

        self.ax_2d.legend()
        self.ax_2d.grid(True)
        self.canvas_2d.draw()

        self.ax_3d.set_xlabel("X")
        self.ax_3d.set_ylabel("Y")
        self.ax_3d.set_zlabel("Z")
        self.ax_3d.set_title("Espacio de Fases 3D")
        self.canvas_3d.draw()

    def plot_simulation(self, sol):
        if sol and sol.success:
            self.ax_2d.clear()
            self.ax_3d.clear()
            
            t = sol.t
            y = sol.y

            # Gráfica 2D
            for i in range(y.shape[0]):
                self.ax_2d.plot(t, y[i], label=f'y_{i+1}(t)')
            self.ax_2d.legend()
            self.ax_2d.grid(True)
            self.canvas_2d.draw()

            # Gráfica 3D
            if y.shape[0] >= 3:
                self.ax_3d.plot(y[0], y[1], y[2])
                self.ax_3d.set_xlabel("X")
                self.ax_3d.set_ylabel("Y")
                self.ax_3d.set_zlabel("Z")
                self.ax_3d.set_title("Espacio de Fases 3D")
                self.canvas_3d.draw()