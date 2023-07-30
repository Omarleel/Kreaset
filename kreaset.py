
import sys
from PyQt5.QtWidgets import QApplication
from Applications.AudioProcessing import AudioProcessing
from Widgets.AppWindow import AppWindow    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    audio_processing = AudioProcessing(None)  # Pasa 'None' como placeholder, se asignará la instancia de 'AppWindow' después
    window = AppWindow(app, audio_processing)
    window.btnProcesar.clicked.connect(audio_processing.procesar_audios)
    audio_processing.app_window = window 
    window.show()
    sys.exit(app.exec_())