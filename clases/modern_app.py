import sys
import json
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QMainWindow

from clases.collapsible_sidebar import CollapsibleSidebar
from clases.equation_row import EquationRow
from clases.initial_condition_row import InitialConditionRow
# from clases.system_3d_view import System3DView # Removed
from clases.resta_dialog import RestaDialog
from clases.varias_restas_panel import VariasRestasPanel
from clases.panel_graficas import PanelGraficas # Ensure this is present


class ModernApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulación Dinámica con Menú (Cargar/Guardar), ETA, y Lógica EXACTA")
        self.resize(1200, 800)
        self.setMouseTracking(True)

        # Crear menú "Inicio" con "Cargar" y "Guardar"
        menubar = self.menuBar()
        menuInicio = menubar.addMenu("Inicio")

        actionCargar = QtGui.QAction("Cargar", self)
        actionGuardar = QtGui.QAction("Guardar", self)
        menuInicio.addAction(actionCargar)
        menuInicio.addAction(actionGuardar)
        actionCargar.triggered.connect(self.onCargar)
        actionGuardar.triggered.connect(self.onGuardar)

        style = QtWidgets.QStyleFactory.create("Fusion")
        if style:
            self.setStyle(style)
        self.setStyleSheet("""
            QWidget {
                font-family: "Segoe UI";
                font-size: 10pt;
                background-color: #2b2b2b;
                color: #dcdcdc;
            }
            QGroupBox {
                border: 1px solid #444;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px;
            }
            QPushButton {
                background-color: #007ACC;
                border: none;
                padding: 6px;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005999;
            }
            QLineEdit, QPlainTextEdit, QComboBox, QSpinBox, QListWidget, QProgressBar {
                background-color: #3c3c3c;
                border: 1px solid #555;
                padding: 4px;
                color: #dcdcdc;
            }
        """)

        centralWidget = QtWidgets.QWidget()
        mainLayout = QtWidgets.QHBoxLayout(centralWidget)

        # Sidebar (navigation)
        self.sidebar = CollapsibleSidebar()
        mainLayout.addWidget(self.sidebar) # Add sidebar directly to mainLayout

        # Left Panel (input controls)
        leftPanel = QtWidgets.QWidget()
        leftLayout = QtWidgets.QVBoxLayout(leftPanel)

        # Ecuaciones
        eqGroup = QtWidgets.QGroupBox("Ecuaciones")
        eqLayout = QtWidgets.QVBoxLayout(eqGroup)
        self.eq_rows = []
        # Asumimos 2 eq_rows => x1,y1,z1 y x2,y2,z2
        for i in range(2):
            row = EquationRow(f"x{i+1}", f"y{i+1}", f"z{i+1}") # Assuming EquationRow takes var names
            self.eq_rows.append(row)
            eqLayout.addWidget(row)
            row.equationChanged.connect(self.onEquationChanged)
        eqGroup.setLayout(eqLayout)
        leftLayout.addWidget(eqGroup)

        # Condiciones Iniciales
        initGroup = QtWidgets.QGroupBox("Condiciones Iniciales")
        initLayout = QtWidgets.QVBoxLayout(initGroup)
        self.init_rows = []
        for i in range(2):
            row = InitialConditionRow(f"x{i+1}", f"y{i+1}", f"z{i+1}") # Assuming InitialConditionRow takes var names
            self.init_rows.append(row)
            initLayout.addWidget(row)
        initGroup.setLayout(initLayout)
        leftLayout.addWidget(initGroup)

        # Botón "Crear restas"
        self.crearRestasButton = QtWidgets.QPushButton("Crear restas (info.txt con ecuaciones e iniciales)")
        leftLayout.addWidget(self.crearRestasButton)

        # Panel "Varias restas"
        self.variasRestasPanel = VariasRestasPanel() # No longer takes a string title
        leftLayout.addWidget(self.variasRestasPanel)

        leftLayout.addStretch()
        mainLayout.addWidget(leftPanel, 2) # Add leftPanel directly to mainLayout

        # Panel derecho (Gráficas y Log)
        rightSplitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)

        # Gráficas (usando PanelGraficas)
        self.panel_graficas = PanelGraficas()
        rightSplitter.addWidget(self.panel_graficas)

        # Log
        logGroup = QtWidgets.QGroupBox("Log")
        logLayout = QtWidgets.QVBoxLayout(logGroup)
        self.logText = QtWidgets.QPlainTextEdit()
        self.logText.setReadOnly(True)
        logLayout.addWidget(self.logText)
        logGroup.setLayout(logLayout)
        rightSplitter.addWidget(logGroup)

        rightSplitter.setStretchFactor(0, 3)
        rightSplitter.setStretchFactor(1, 1)

        mainLayout.addWidget(rightSplitter, 3)
        self.setCentralWidget(centralWidget)

        self.crearRestasButton.clicked.connect(self.onCrearRestasClicked)
        self.variasRestasPanel.progress_message_signal.connect(self.log) # Assuming this signal exists
        self.variasRestasPanel.plot_batch_results.connect(self.panel_graficas.plot_simulation_batch) # New connection

    # ---------------------------------------------------------------------
    # Menú "Inicio" -> "Cargar" / "Guardar"
    # ---------------------------------------------------------------------
    def onCargar(self):
        """
        Cargar eq_rows e init_rows desde un .json
        """
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Cargar Ecuaciones/Iniciales", "", "JSON (*.json)"
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            eq_data = data.get("equations", [])
            init_data = data.get("initials", [])

            # eq_data es lista de [ [dx1, dy1, dz1], [dx2, dy2, dz2], ... ]
            # init_data es [ [x1_0,y1_0,z1_0], [x2_0,y2_0,z2_0], ... ]

            # Ajustamos eq_rows
            for i, row in enumerate(self.eq_rows):
                if i<len(eq_data):
                    dx, dy, dz = eq_data[i]
                    row.equation_input_x.setText(dx)
                    row.equation_input_y.setText(dy)
                    row.equation_input_z.setText(dz)

            # Ajustamos init_rows
            for i, row in enumerate(self.init_rows):
                if i<len(init_data):
                    x0, y0, z0 = init_data[i]
                    row.value_input_x.setText(str(x0))
                    row.value_input_y.setText(str(y0))
                    row.value_input_z.setText(str(z0))

            self.log(f"Cargado desde '{path}' correctamente.")
            self.updateSimulationAndPlot() # Call the new consolidated update method
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"No se pudo cargar: {e}")

    def onGuardar(self):
        """
        Guardar eq_rows e init_rows en un .json
        """
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Guardar Ecuaciones/Iniciales", "", "JSON (*.json)"
        )
        if not path:
            return

        # Recolectar ecuaciones
        eq_data = []
        for row in self.eq_rows:
            dx, dy, dz = row.getEquations()
            eq_data.append([dx, dy, dz])

        # Recolectar inits
        init_data = []
        for row in self.init_rows:
            x0, y0, z0 = row.getInitialValues()
            init_data.append([x0, y0, z0])

        data = {
            "equations": eq_data,
            "initials": init_data
        }

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            self.log(f"Guardado en '{path}' correctamente.")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"No se pudo guardar: {e}")

    # ---------------------------------------------------------------------
    # Lógica de la ventana principal
    # ---------------------------------------------------------------------
    def onCrearRestasClicked(self):
        var_list = self.buildVariableList()
        eq_code = self.buildSystemFunction()
        init_vals = []
        for row in self.init_rows:
            init_vals.extend(row.getInitialValues())

        dialog = RestaDialog(var_list, eq_code, init_vals, parent=self)
        res = dialog.exec()
        if res == QtWidgets.QDialog.DialogCode.Accepted:
            self.log("Se han creado restas (info.txt con ecuaciones e iniciales).")
        else:
            self.log("Operación de crear restas cancelada.")

    def buildVariableList(self):
        n = len(self.eq_rows)
        var_list = []
        for i in range(n):
            var_list.append(f"x{i+1}")
            var_list.append(f"y{i+1}")
            var_list.append(f"z{i+1}")
        return var_list

    def log(self, msg):
        self.logText.appendPlainText(msg)

    def onEquationChanged(self):
        self.log("Ecuaciones modificadas. Actualizando simulación y gráficas con a=0...")
        self.updateSimulationAndPlot()

    def updateSimulationAndPlot(self, a_param=0.0): # New consolidated method
        eq_code = self.buildSystemFunction()
        if not eq_code:
            return
        local_vars = {}
        try:
            exec(eq_code, {"np": np}, local_vars) # Pass np for eval
            sistema_dinamico = local_vars['sistema_dinamico']
        except Exception as e:
            self.log(f"Error generando ecuación: {e}")
            return

        init_values = []
        for row in self.init_rows:
            init_values.extend(row.getInitialValues())

        t_span = (0, 5) # These should ideally be configurable
        t_eval = np.linspace(0, 5, 200) # These should ideally be configurable
        try:
            sol = solve_ivp(sistema_dinamico, t_span, init_values, t_eval=t_eval, args=(a_param,))
        except Exception as e:
            self.log(f"Error solve_ivp: {e}")
            return

        if sol.success:
            self.panel_graficas.plot_simulation(sol)
        else:
            self.log("La simulación no fue exitosa.")


    def buildSystemFunction(self):
        """
        Genera eq_code con:
        def sistema_dinamico(t, variables, a):
            x1,y1,z1,x2,y2,z2 = variables
            ...
            return [...]
        """
        n = len(self.eq_rows)
        if n<1:
            return None

        var_names = []
        for i in range(n):
            var_names.append(f"x{i+1}")
            var_names.append(f"y{i+1}")
            var_names.append(f"z{i+1}")

        lines = []
        lines.append("def sistema_dinamico(t, variables, a):")
        lines.append("    " + ", ".join(var_names) + " = variables")

        eq_expressions = []
        for i,row in enumerate(self.eq_rows):
            dx,dy,dz = row.getEquations()
            dx = dx.strip() if dx.strip() else "0"
            dy = dy.strip() if dy.strip() else "0"
            dz = dz.strip() if dz.strip() else "0"
            eq_expressions.append(dx)
            eq_expressions.append(dy)
            eq_expressions.append(dz)

        ret_line = "    return [" + ", ".join(eq_expressions) + "]"
        lines.append(ret_line)

        return "\n".join(lines)

    def setTheme(self, theme: str) -> None:
        """Cambia el tema a 'Dark', 'Light' o 'Acrylic'."""
        if theme == "Dark":
            self.setPalette(self.makeDarkPalette())
            self.applyDarkStyles()
        elif theme == "Light":
            self.setPalette(self.makeLightPalette())
            self.applyLightStyles()
        elif theme == "Acrylic":
            self.applyAcrylicStyle()

    def applyDarkStyles(self):
        """Ejemplo: texto blanco y hover gris."""
        # self.sidebar.titleLabel.setStyleSheet("color: white;") # CollapsibleSidebar doesn't have titleLabel
        # self.sidebar.toggleButton.setStyleSheet("color: white;") # CollapsibleSidebar doesn't have toggleButton
        # for btn in self.sidebar.buttons: # CollapsibleSidebar doesn't have buttons directly
        #     btn.setStyleSheet("""
        #         QPushButton {
        #             color: white;
        #             border: none;
        #             border-radius: 4px;
        #             padding: 8px;
        #         }
        #         QPushButton:hover {
        #             background-color: rgba(100, 100, 100, 80);
        #         }
        #     """)
        pass # Styles will be applied via global stylesheet or individual widgets

    def applyLightStyles(self):
        """Ejemplo: texto negro y hover azul."""
        # self.sidebar.titleLabel.setStyleSheet("color: black;")
        # self.sidebar.toggleButton.setStyleSheet("color: black;")
        # for btn in self.sidebar.buttons:
        #     btn.setStyleSheet("""
        #         QPushButton {
        #             color: black;
        #             border: none;
        #             border-radius: 4px;
        #             padding: 8px;
        #         }
        #         QPushButton:hover {
        #             background-color: rgba(0, 120, 215, 80);
        #         }
        #     """)
        pass # Styles will be applied via global stylesheet or individual widgets

    def makeDarkPalette(self) -> QtGui.QPalette:
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(45, 45, 45))
        palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtCore.Qt.GlobalColor.white)
        palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(35, 35, 35))
        palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(45, 45, 45))
        palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtCore.Qt.GlobalColor.white)
        palette.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtCore.Qt.GlobalColor.white)
        palette.setColor(QtGui.QPalette.ColorRole.Text, QtCore.Qt.GlobalColor.white)
        palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(70, 70, 70))
        palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtCore.Qt.GlobalColor.white)
        palette.setColor(QtGui.QPalette.ColorRole.BrightText, QtCore.Qt.GlobalColor.red)
        palette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(100, 100, 255))
        palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtCore.Qt.GlobalColor.black)
        return palette

    def makeLightPalette(self) -> QtGui.QPalette:
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.ColorRole.Window, QtCore.Qt.GlobalColor.white)
        palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtCore.Qt.GlobalColor.black)
        palette.setColor(QtGui.QPalette.ColorRole.Base, QtCore.Qt.GlobalColor.white)
        palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(220, 220, 220))
        palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtCore.Qt.GlobalColor.white)
        palette.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtCore.Qt.GlobalColor.black)
        palette.setColor(QtGui.QPalette.ColorRole.Text, QtCore.Qt.GlobalColor.black)
        palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(200, 200, 200))
        palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtCore.Qt.GlobalColor.black)
        palette.setColor(QtGui.QPalette.ColorRole.BrightText, QtCore.Qt.GlobalColor.red)
        palette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(0, 120, 215))
        palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtCore.Qt.GlobalColor.white)
        return palette

    def applyAcrylicStyle(self) -> None:
        """
        Estilo acrílico simulado mediante transparencia.
        Para un acrílico real, se requiere integración con APIs de Windows 10/11.
        """
        self.setWindowOpacity(0.92)
        self.setPalette(self.makeDarkPalette())  # Usamos base oscura + algo de transparencia

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        """
        Si el sidebar está expandido, verificamos si el mouse salió del área
        + margen para colapsarlo.
        """
        # if self.sidebar.is_expanded: # CollapsibleSidebar doesn't have is_expanded
        #     pos = self.sidebar.mapFromGlobal(event.globalPosition().toPoint())
        #     # Ajustamos el rect con un margen
        #     rect_con_margen = self.sidebar.rect().adjusted(-self.sidebar.margin,
        #                                                    -self.sidebar.margin,
        #                                                     self.sidebar.margin,
        #                                                     self.sidebar.margin)
        #     if not rect_con_margen.contains(pos):
        #         self.sidebar.collapse()
        super().mouseMoveEvent(event)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """Confirmar al cerrar la aplicación."""
        reply = QtWidgets.QMessageBox.question(
            self, "Salir", "¿Seguro que deseas salir?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

