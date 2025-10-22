from PyQt6 import QtWidgets, QtCore, QtGui

class CollapsibleSidebar(QtWidgets.QFrame):
    """
    Panel lateral colapsable con animación.
      - Ancho expandido: 200 px
      - Ancho colapsado: 50 px (ajustable)
      - Usa QPropertyAnimation para transiciones suaves
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.expanded_width = 200
        self.collapsed_width = 50  # Visible para el botón de toggle
        self.is_expanded = True
        self.margin = 50

        # Configurar el ancho inicial
        self.setFixedWidth(self.expanded_width)

        # Configurar la animación del ancho
        self.animation = QtCore.QPropertyAnimation(self, b"minimumWidth", self)
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QtCore.QEasingCurve.Type.InOutCubic)

        # Layout vertical con márgenes y espaciado
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(10)

        # Botón de toggle (icono de hamburguesa)
        self.toggleButton = QtWidgets.QPushButton("☰")
        self.toggleButton.setFixedSize(30, 30)
        self.toggleButton.clicked.connect(self.toggle)
        self.layout.addWidget(self.toggleButton, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        # Título del menú
        self.titleLabel = QtWidgets.QLabel("Menú")
        font = self.titleLabel.font()
        font.setBold(True)
        self.titleLabel.setFont(font)
        self.layout.addWidget(self.titleLabel, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)

        # Botones de navegación (solo dos: "Cálculos" y "Gráficas")
        self.buttons = []

        btn_calculos = QtWidgets.QPushButton("Cálculos")
        btn_calculos.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn_calculos.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: rgba(100, 100, 100, 80);
            }
        """)
        self.layout.addWidget(btn_calculos)
        self.buttons.append(btn_calculos)

        btn_graficas = QtWidgets.QPushButton("Gráficas")
        btn_graficas.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn_graficas.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: rgba(100, 100, 100, 80);
            }
        """)
        self.layout.addWidget(btn_graficas)
        self.buttons.append(btn_graficas)

        # Combobox para seleccionar el tema
        self.themeCombo = QtWidgets.QComboBox()
        self.themeCombo.addItems(["Dark", "Light", "Acrylic"])
        self.layout.addWidget(self.themeCombo)

        self.layout.addStretch()

    def toggle(self) -> None:
        """Al pulsar el botón hamburguesa, expandimos o colapsamos."""
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self) -> None:
        if not self.is_expanded:
            self.is_expanded = True
            self.titleLabel.setVisible(True)
            for btn in self.buttons:
                btn.setVisible(True)
            self.themeCombo.setVisible(True)

            self.animation.stop()
            self.animation.setStartValue(self.width())
            self.animation.setEndValue(self.expanded_width)
            self.animation.start()

    def collapse(self) -> None:
        if self.is_expanded:
            self.is_expanded = False
            self.animation.stop()
            self.animation.setStartValue(self.width())
            self.animation.setEndValue(self.collapsed_width)
            self.animation.start()
            self.animation.finished.connect(self._hideElements)

    def _hideElements(self) -> None:
        """Ocultamos textos y botones tras la animación de colapso."""
        if not self.is_expanded:
            self.titleLabel.setVisible(False)
            for btn in self.buttons:
                btn.setVisible(False)
            self.themeCombo.setVisible(False)
        # Evitar conectar duplicado
        try:
            self.animation.finished.disconnect(self._hideElements)
        except TypeError:
            pass
