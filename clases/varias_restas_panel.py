import os
from PyQt6 import QtWidgets, QtCore
from clases.batch_thread import BatchThread

class VariasRestasPanel(QtWidgets.QGroupBox):
    progress_message_signal = QtCore.pyqtSignal(str)
    plot_batch_results = QtCore.pyqtSignal(object) # New signal

    def __init__(self, title="Varias restas", parent=None):
        super().__init__(title, parent)
        layout = QtWidgets.QVBoxLayout(self)

        self.loadButton = QtWidgets.QPushButton("Cargar carpeta con restas")
        layout.addWidget(self.loadButton)

        self.restaList = QtWidgets.QListWidget()
        layout.addWidget(self.restaList)

        btnLayout = QtWidgets.QHBoxLayout()
        self.startButton = QtWidgets.QPushButton("Iniciar")
        self.stopButton = QtWidgets.QPushButton("Detener")
        btnLayout.addWidget(self.startButton)
        btnLayout.addWidget(self.stopButton)
        layout.addLayout(btnLayout)

        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setValue(0)
        layout.addWidget(self.progressBar)

        self.loadButton.clicked.connect(self.onLoad)
        self.startButton.clicked.connect(self.onStart)
        self.stopButton.clicked.connect(self.onStop)

        self.batchThread = None
        self.base_folder = None

        # eq_code e init_values no se usan para el batch, pero se mantienen
        # para compatibilidad con la interfaz
        self.eq_code = None
        self.init_values = None

        self.setLayout(layout)

    def onLoad(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Restas", "")
        if folder:
            self.base_folder = folder
            self.restaList.clear()
            for name in os.listdir(folder):
                subdir = os.path.join(folder, name)
                if os.path.isdir(subdir):
                    self.restaList.addItem(name)

    def onStart(self):
        count = self.restaList.count()
        if count == 0:
            QtWidgets.QMessageBox.information(self, "Nada", "No hay subcarpetas para procesar.")
            return
        if not self.base_folder:
            QtWidgets.QMessageBox.information(self, "Falta carpeta", "No has cargado ninguna carpeta base.")
            return

        subfolders = [self.restaList.item(i).text() for i in range(count)]
        self.batchThread = BatchThread(self.base_folder, subfolders)
        self.batchThread.progress_signal.connect(self.onThreadProgress)
        self.batchThread.folder_done_signal.connect(self.onFolderDone)
        self.batchThread.all_done_signal.connect(self.onAllDone)
        self.batchThread.simulation_result_signal.connect(self.onSimulationResult) # New connection

        self.batchThread.start()
        self.progressBar.setValue(0)

    def onStop(self):
        if self.batchThread:
            self.batchThread.request_stop()
            self.progress_message_signal.emit("Solicitud de detención enviada.")

    def onThreadProgress(self, msg):
        self.progress_message_signal.emit(msg)

    def onFolderDone(self, idx):
        total = self.restaList.count()
        progress = int(((idx+1)/total)*100)
        self.progressBar.setValue(progress)

    def onAllDone(self):
        self.progress_message_signal.emit("Proceso batch finalizado.")
        QtWidgets.QMessageBox.information(self, "Fin", "Procesamiento finalizado.")
        self.batchThread = None

    def onSimulationResult(self, sol): # New slot
        self.plot_batch_results.emit(sol)
