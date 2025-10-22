import os
from PyQt6 import QtWidgets, QtCore, QtGui

class RestaDialog(QtWidgets.QDialog):
    def __init__(self, var_list, eq_code, init_values, parent=None):
        """
        var_list: ["x1","y1","z1","x2","y2","z2"] (o más)
        eq_code: string con la def sistema_dinamico(t, variables, a): ...
        init_values: [x1_0, y1_0, z1_0, x2_0, y2_0, z2_0]
        """
        super().__init__(parent)
        self.setWindowTitle("Crear Restas y Parámetros de 'a'")
        self.resize(600, 600)

        self.var_list = var_list
        self.eq_code = eq_code
        self.init_values = init_values

        layout = QtWidgets.QVBoxLayout(self)

        self.allCombinationsCheck = QtWidgets.QCheckBox("Todas las combinaciones posibles")
        layout.addWidget(self.allCombinationsCheck)

        self.restaListWidget = QtWidgets.QListWidget()
        self.restaListWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        layout.addWidget(self.restaListWidget)

        for i in range(len(var_list)):
            for j in range(i+1, len(var_list)):
                item_text = f"{var_list[i]} - {var_list[j]}"
                item = QtWidgets.QListWidgetItem(item_text)
                self.restaListWidget.addItem(item)

        paramGroup = QtWidgets.QGroupBox("Parámetros de 'a'")
        paramLayout = QtWidgets.QFormLayout(paramGroup)
        self.aStartEdit = QtWidgets.QLineEdit("0.0")
        self.aStopEdit = QtWidgets.QLineEdit("5.0")
        self.aStepEdit = QtWidgets.QLineEdit("0.01")
        paramLayout.addRow("a inicial:", self.aStartEdit)
        paramLayout.addRow("a final:", self.aStopEdit)
        paramLayout.addRow("Paso de a:", self.aStepEdit)
        layout.addWidget(paramGroup)

        folderLayout = QtWidgets.QHBoxLayout()
        self.folderLabel = QtWidgets.QLabel("Carpeta destino: (no seleccionado)")
        self.folderButton = QtWidgets.QPushButton("Seleccionar carpeta")
        folderLayout.addWidget(self.folderLabel)
        folderLayout.addWidget(self.folderButton)
        layout.addLayout(folderLayout)

        btnLayout = QtWidgets.QHBoxLayout()
        self.createButton = QtWidgets.QPushButton("Crear")
        self.cancelButton = QtWidgets.QPushButton("Cancelar")
        btnLayout.addWidget(self.createButton)
        btnLayout.addWidget(self.cancelButton)
        layout.addLayout(btnLayout)

        self.selectedFolder = None

        self.folderButton.clicked.connect(self.selectFolder)
        self.createButton.clicked.connect(self.onCreate)
        self.cancelButton.clicked.connect(self.reject)
        self.allCombinationsCheck.stateChanged.connect(self.onAllCombinationsToggled)

        self.setLayout(layout)

    def selectFolder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta", "")
        if folder:
            self.selectedFolder = folder
            self.folderLabel.setText(f"Carpeta destino: {folder}")

    def onAllCombinationsToggled(self, state):
        if self.allCombinationsCheck.isChecked():
            for i in range(self.restaListWidget.count()):
                item = self.restaListWidget.item(i)
                item.setSelected(True)
            self.restaListWidget.setEnabled(False)
        else:
            self.restaListWidget.clearSelection()
            self.restaListWidget.setEnabled(True)

    def onCreate(self):
        if not self.selectedFolder:
            QtWidgets.QMessageBox.warning(self, "Falta carpeta", "Selecciona la carpeta destino.")
            return

        try:
            a_start = float(self.aStartEdit.text())
            a_stop = float(self.aStopEdit.text())
            a_step = float(self.aStepEdit.text())
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Error", "Los parámetros de 'a' deben ser numéricos.")
            return

        selected_restas = []
        if self.allCombinationsCheck.isChecked():
            for i in range(self.restaListWidget.count()):
                item = self.restaListWidget.item(i)
                selected_restas.append(item.text())
        else:
            for item in self.restaListWidget.selectedItems():
                selected_restas.append(item.text())

        if not selected_restas:
            QtWidgets.QMessageBox.warning(self, "Sin restas", "No has seleccionado ninguna resta.")
            return

        # eq_code => def sistema_dinamico(t, variables, a): ...
        # init_values => [x1_0, y1_0, z1_0, x2_0, y2_0, z2_0]

        for resta in selected_restas:
            subdir_name = resta.replace(" ", "")
            subdir = os.path.join(self.selectedFolder, subdir_name)
            if not os.path.exists(subdir):
                os.makedirs(subdir, exist_ok=True)
            info_path = os.path.join(subdir, "info.txt")

            with open(info_path, "w", encoding="utf-8") as f:
                # 1) Resta y 'a'
                f.write(f"Resta: {resta}\n")
                f.write(f"a_start = {a_start}\n")
                f.write(f"a_stop = {a_stop}\n")
                f.write(f"a_step = {a_step}\n\n")

                # 2) Ecuaciones
                f.write("Ecuaciones:\n")
                f.write(self.eq_code + "\n\n")

                # 3) CondicionesIniciales
                if len(self.init_values)>=6:
                    f.write("CondicionesIniciales:\n")
                    f.write(f"x1 = {self.init_values[0]}\n")
                    f.write(f"y1 = {self.init_values[1]}\n")
                    f.write(f"z1 = {self.init_values[2]}\n")
                    f.write(f"x2 = {self.init_values[3]}\n")
                    f.write(f"y2 = {self.init_values[4]}\n")
                    f.write(f"z2 = {self.init_values[5]}\n")

        QtWidgets.QMessageBox.information(
            self,
            "Listo",
            f"Se han creado {len(selected_restas)} restas (info.txt con ecuaciones e iniciales) en:\n{self.selectedFolder}"
        )
        self.accept()

# -------------------------------------------------------------------------
# parse_info_file
# -------------------------------------------------------------------------
def parse_info_file(info_path):
    with open(info_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    lines = [ln.strip("\n\r") for ln in lines]

    resta_name = None
    a_start = None
    a_stop = None
    a_step = None
    eq_code_lines = []
    init_dict = {}

    in_equations = False
    in_init = False

    for line in lines:
        if line.startswith("Resta:"):
            resta_name = line.split(":",1)[-1].strip()
        elif line.startswith("a_start ="):
            a_start = float(line.split("=")[-1])
        elif line.startswith("a_stop ="):
            a_stop = float(line.split("=")[-1])
        elif line.startswith("a_step ="):
            a_step = float(line.split("=")[-1])

        elif line.lower().startswith("ecuaciones:"):
            in_equations = True
            in_init = False
            continue
        elif line.lower().startswith("condicionesiniciales:"):
            in_equations = False
            in_init = True
            continue
        else:
            if in_equations:
                eq_code_lines.append(line)
            elif in_init:
                parts = line.split("=")
                if len(parts)==2:
                    var_name = parts[0].strip()
                    val = float(parts[1])
                    init_dict[var_name] = val

    eq_code = "\n".join(eq_code_lines)
    init_values = [
        init_dict.get("x1",0.0),
        init_dict.get("y1",0.0),
        init_dict.get("z1",0.0),
        init_dict.get("x2",0.0),
        init_dict.get("y2",0.0),
        init_dict.get("z2",0.0)
    ]

    return resta_name, a_start, a_stop, a_step, eq_code, init_values

def parse_resta_name(resta_name):
    mapping = {"x1":0,"y1":1,"z1":2,"x2":3,"y2":4,"z2":5}
    r = resta_name.replace(" ","")
    if "-" not in r:
        return (0,3)
    varA, varB = r.split("-",1)
    idxA = mapping.get(varA, 0)
    idxB = mapping.get(varB, 3)
    return (idxA, idxB)