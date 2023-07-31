from PyQt5.QtWidgets import QDesktopWidget, QSlider, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QComboBox, QMessageBox, QWidget, QProgressBar
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

import os
class AppWindow(QMainWindow):
    update_progress_signal = pyqtSignal(int) # Definir una señal para actualizar la barra de progreso   
    
    def __init__(self, app, audio_processing_instance):
        super().__init__()
        self.audio_processing = audio_processing_instance
        self.setWindowTitle("Kreaset (by Omarleel)")
        icono = QIcon('../icono.ico')
        app.setWindowIcon(icono)
        self.setGeometry(0, 0, 580, 460)
        self.center_window()
        self.file_path = None
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.label1 = QLabel("<b>Directorio del dataset:</b>")
        layout.addWidget(self.label1)

        self.txt_ruta_carpeta = QLineEdit()
        self.txt_ruta_carpeta.setDisabled(True)
        layout.addWidget(self.txt_ruta_carpeta)

        self.btnSeleccionarRuta = QPushButton("Seleccionar", self)
        self.btnSeleccionarRuta.clicked.connect(self.seleccionar_carpeta)
        layout.addWidget(self.btnSeleccionarRuta)

        self.label2 = QLabel("<b>Archivos de audio:</b>")
        layout.addWidget(self.label2)
        
        self.etiqueta_cantidad_audios = QLabel("-")
        layout.addWidget(self.etiqueta_cantidad_audios)

        self.label3 = QLabel("<b>Duración entrada:</b>")
        layout.addWidget(self.label3)
        
        self.etiqueta_duracion_entrada_audios = QLabel("-")
        layout.addWidget(self.etiqueta_duracion_entrada_audios)
        
        self.label4 = QLabel("<b>Suprimir ruido</b>")
        layout.addWidget(self.label4)
        
        # Crear el slider horizontal
        self.slider_suprimir_ruido = QSlider(Qt.Horizontal)
        self.slider_suprimir_ruido.setMinimum(0)
        self.slider_suprimir_ruido.setMaximum(100)
        self.slider_suprimir_ruido.setValue(0)  # Valor inicial al 0%
        
        # Etiqueta para mostrar el valor actual del slider en porcentaje
        self.label = QLabel('0%')

        # Conectar el cambio del slider con la función de actualización de la etiqueta
        self.slider_suprimir_ruido.valueChanged.connect(self.update_label)

        # Crear el layout vertical y agregar el slider y la etiqueta a él
        layout.addWidget(self.slider_suprimir_ruido)
        layout.addWidget(self.label)
        
        self.label5 = QLabel("<b>Extraer voz</b>")
        layout.addWidget(self.label5)
        
        self.opcion_seleccionada_voz = QComboBox()
        self.opcion_seleccionada_voz.addItems(["Si", "No"])
        self.opcion_seleccionada_voz.setCurrentText("Si")
        layout.addWidget(self.opcion_seleccionada_voz)
        
        self.label6 = QLabel("<b>Remover silencio</b>")
        layout.addWidget(self.label6)
        
        self.opcion_seleccionada_silencio = QComboBox()
        self.opcion_seleccionada_silencio.addItems(["Alta tolerancia", "Baja tolerancia"])
        self.opcion_seleccionada_silencio.setCurrentText("Alta tolerancia")
        layout.addWidget(self.opcion_seleccionada_silencio)
        
        self.label7 = QLabel("<b>Dividir audio</b>")
        layout.addWidget(self.label7)
        
        self.opcion_seleccionada_dividir = QComboBox()
        self.opcion_seleccionada_dividir.addItems(["5 segundos", "10 segundos", "15 segundos", "20 segundos"])
        self.opcion_seleccionada_dividir.setCurrentText("15 segundos")
        layout.addWidget(self.opcion_seleccionada_dividir)
        
        self.btnProcesar = QPushButton("Generar dataset", self)
        layout.addWidget(self.btnProcesar)
        self.btnProcesar.setEnabled(False)
        
        self.etiqueta_progreso = QLabel("Sin procesar")
        layout.addWidget(self.etiqueta_progreso)

        self.barra_de_progreso = QProgressBar(self)
        self.barra_de_progreso.setOrientation(Qt.Horizontal)
        self.barra_de_progreso.setValue(0)
        layout.addWidget(self.barra_de_progreso)
        self.update_progress_signal.connect(self.actualizar_progreso)
        
        self.label7 = QLabel("<b>Duración salida:</b>")
        layout.addWidget(self.label7)
        
        self.etiqueta_duracion_salida_audios = QLabel("-")
        layout.addWidget(self.etiqueta_duracion_salida_audios)
    
    def update_label(self, value):
        # Actualizar el texto de la etiqueta con el valor del slider en porcentaje
        self.label.setText(f'{value}%')
            
    def actualizar_progreso(self, value):
        self.barra_de_progreso.setValue(value)
                
    def center_window(self):
        # Obtiene la geometría de la pantalla disponible y el centro de la misma
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        # Mueve la ventana al centro de la pantalla
        qr.moveCenter(cp)
        self.move(qr.topLeft())
            
    def seleccionar_carpeta(self):
        ruta_carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")

        if ruta_carpeta and os.path.exists(ruta_carpeta):
            self.etiqueta_progreso.setText("Sin procesar")
            self.barra_de_progreso.setValue(0)
            self.etiqueta_duracion_salida_audios.setText("-")
            
            self.btnProcesar.setEnabled(True)
            self.txt_ruta_carpeta.setEnabled(True)
            self.txt_ruta_carpeta.clear()
            self.txt_ruta_carpeta.insert(ruta_carpeta)
            self.txt_ruta_carpeta.setDisabled(True)

            archivos = os.listdir(ruta_carpeta)
            archivos_audio = [archivo for archivo in archivos if archivo.lower().endswith((".mp3", ".wav", ".wma"))]
            cantidad_audios = len(archivos_audio)
            self.etiqueta_cantidad_audios.setText(f"{cantidad_audios}")

            self.audio_processing.audios_seleccionados = None
            self.audio_processing.calcular_duracion_total(ruta_carpeta, self.etiqueta_duracion_entrada_audios)
