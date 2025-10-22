from PyQt6 import QtWidgets, QtCore
from panel_calculo import EquationRow # Placeholder, will be updated

class MainArea(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stack = QtWidgets.QStackedLayout(self)
        self.screens = {}

        # Pantalla "calculos"
        calc_frame = QtWidgets.QFrame()
        calc_layout = QtWidgets.QVBoxLayout(calc_frame)

        self.panelCalculo = EquationRow(1)  # <--- tu widget con ecuaciones, etc.
        calc_layout.addWidget(self.panelCalculo)

        self.screens["calculos"] = calc_frame
        self.stack.addWidget(calc_frame)

        # Pantalla "graficas"
        graf_frame = QtWidgets.QFrame()
        graf_layout = QtWidgets.QVBoxLayout(graf_frame)
        graf_label = QtWidgets.QLabel("Contenido de Gráficas")
        graf_label.setStyleSheet("font-size: 24px;")
        graf_layout.addWidget(graf_label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.screens["graficas"] = graf_frame
        self.stack.addWidget(graf_frame)

        # Muestra “calculos” por defecto
        self.showScreen("calculos")

    def showScreen(self, name: str):
        for i, (k, w) in enumerate(self.screens.items()):
            if k == name:
                self.stack.setCurrentIndex(i)
                break
