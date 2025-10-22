from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton

class InitialConditionRow(QWidget):
    def __init__(self, var_x_name, var_y_name, var_z_name, on_remove=None):
        super().__init__()
        self.var_x_name = var_x_name
        self.var_y_name = var_y_name
        self.var_z_name = var_z_name
        self.on_remove = on_remove

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.label_x = QLabel(f"{self.var_x_name}(0) =")
        self.value_input_x = QLineEdit()

        self.label_y = QLabel(f"{self.var_y_name}(0) =")
        self.value_input_y = QLineEdit()

        self.label_z = QLabel(f"{self.var_z_name}(0) =")
        self.value_input_z = QLineEdit()

        self.remove_button = QPushButton("X")
        self.remove_button.setFixedSize(25, 25)
        self.remove_button.clicked.connect(self.remove_row)

        self.layout.addWidget(self.label_x)
        self.layout.addWidget(self.value_input_x)
        self.layout.addWidget(self.label_y)
        self.layout.addWidget(self.value_input_y)
        self.layout.addWidget(self.label_z)
        self.layout.addWidget(self.value_input_z)
        self.layout.addWidget(self.remove_button)

    def getInitialValues(self):
        try:
            val_x = float(self.value_input_x.text())
        except ValueError:
            val_x = 0.0
        try:
            val_y = float(self.value_input_y.text())
        except ValueError:
            val_y = 0.0
        try:
            val_z = float(self.value_input_z.text())
        except ValueError:
            val_z = 0.0
        return (val_x, val_y, val_z)

    def remove_row(self):
        if self.on_remove:
            self.on_remove(self)