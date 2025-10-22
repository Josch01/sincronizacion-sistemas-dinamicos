from PyQt6 import QtWidgets
import pyqtgraph.opengl as gl
import numpy as np

class System3DView(QtWidgets.QGroupBox):
    def __init__(self, title="Gráfica 3D", parent=None):
        super().__init__(title, parent)
        layout = QtWidgets.QVBoxLayout(self)

        self.glView = gl.GLViewWidget()
        layout.addWidget(self.glView)

        axis = gl.GLAxisItem()
        axis.setSize(10, 10, 10)
        self.glView.addItem(axis)

        grid = gl.GLGridItem()
        grid.setSize(20, 20)
        grid.setSpacing(1, 1)
        self.glView.addItem(grid)

        self.items3D = []

    def clearData(self):
        for item in self.items3D:
            self.glView.removeItem(item)
        self.items3D.clear()

    def addTrajectory(self, x, y, z, color=(1,1,1,1)):
        pos = np.column_stack((x, y, z))
        plt = gl.GLLinePlotItem(pos=pos, color=color, width=1.0, antialias=True)
        self.glView.addItem(plt)
        self.items3D.append(plt)
