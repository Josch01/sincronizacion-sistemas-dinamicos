from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal

class EquationRow(QWidget):
    equationChanged = pyqtSignal() # Signal to notify when an equation changes

    def __init__(self, var_x_name, var_y_name, var_z_name, on_remove=None):
        super().__init__()
        self.var_x_name = var_x_name
        self.var_y_name = var_y_name
        self.var_z_name = var_z_name
        self.on_remove = on_remove

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.label_x = QLabel(f"d{self.var_x_name}/dt =")
        self.equation_input_x = QLineEdit()
        self.equation_input_x.textChanged.connect(self.equationChanged.emit)

        self.label_y = QLabel(f"d{self.var_y_name}/dt =")
        self.equation_input_y = QLineEdit()
        self.equation_input_y.textChanged.connect(self.equationChanged.emit)

        self.label_z = QLabel(f"d{self.var_z_name}/dt =")
        self.equation_input_z = QLineEdit()
        self.equation_input_z.textChanged.connect(self.equationChanged.emit)

        self.remove_button = QPushButton("X")
        self.remove_button.setFixedSize(25, 25)
        self.remove_button.clicked.connect(self.remove_row)

        self.layout.addWidget(self.label_x)
        self.layout.addWidget(self.equation_input_x)
        self.layout.addWidget(self.label_y)
        self.layout.addWidget(self.equation_input_y)
        self.layout.addWidget(self.label_z)
        self.layout.addWidget(self.equation_input_z)
        self.layout.addWidget(self.remove_button)

    def getEquations(self):
        return (self.equation_input_x.text(),
                self.equation_input_y.text(),
                self.equation_input_z.text())

    def remove_row(self):
        if self.on_remove:
            self.on_remove(self)