import sys
from PyQt6 import QtWidgets
from clases.modern_app import ModernApp

def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    # Estilo Fusion
    QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create("Fusion"))

    window = ModernApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()