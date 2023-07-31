import os
import io
import numpy as np
from threading import Thread
from pydub import AudioSegment
import io
from scipy.io import wavfile
import noisereduce as nr
from pydub.silence import split_on_silence
from pyAudioAnalysis import audioBasicIO as aIO
from pyAudioAnalysis import audioSegmentation as aS
from spleeter.separator import Separator
   
class AudioProcessing():
    def __init__(self, app_window):
        self.separator = Separator('spleeter:2stems', multiprocess=False)
        self.ruta_audio_procesar = None
        self.tecnicas_procesamiento = None
        self.duracion_segundos = None
        self.audios_seleccionados = None
        self.etiqueta_duracion_entrada_audios = None
        self.app_window = app_window
        
    def calcular_duracion_total(self, ruta_carpeta, lbl_duracion):
        archivos = os.listdir(ruta_carpeta)
        archivos_audio = [archivo for archivo in archivos if archivo.lower().endswith((".mp3", ".wav", ".wma"))]
        duracion_total_ms = 0
        for archivo in archivos_audio:
            ruta_audio = os.path.join(ruta_carpeta, archivo)
            audio = AudioSegment.from_file(ruta_audio)
            if lbl_duracion == self.app_window.etiqueta_duracion_entrada_audios:
                if self.audios_seleccionados is None:
                    self.audios_seleccionados = audio
                else:
                    self.audios_seleccionados += audio
                
            duracion_total_ms += len(audio)

        # Convertir la duración total a formato horas, minutos y segundos
        segundos_totales = duracion_total_ms / 1000
        self.duracion_segundos = float(round(segundos_totales))
        horas = int(segundos_totales // 3600)
        segundos_totales %= 3600
        minutos = int(segundos_totales // 60)
        segundos = int(segundos_totales % 60)
        # Actualizar la etiqueta con la duración total de los audios
        if horas > 0:
            lbl_duracion.setText(f"{horas} horas, {minutos} minutos y {segundos} segundos")
        else:
            lbl_duracion.setText(f"{minutos} minutos y {segundos} segundos")

    def combinar_audios(self):
        self.app_window.etiqueta_progreso.setText("Combinando audios...")
        ruta_carpeta = self.app_window.txt_ruta_carpeta.text()
        ruta_outputs = os.path.join(ruta_carpeta, "outputs")
        if not os.path.exists(ruta_outputs):
            os.makedirs(ruta_outputs)

        self.ruta_audio_procesar = os.path.join(ruta_outputs, "audio_combinado.wav")
        self.audios_seleccionados.export(self.ruta_audio_procesar, format="wav")
            
        self.app_window.update_progress_signal.emit(int(self.app_window.barra_de_progreso.maximum() / self.tecnicas_procesamiento))
 
    def extraer_voz(self):
        self.app_window.etiqueta_progreso.setText("Extrayendo voz...")
        ruta_carpeta = self.app_window.txt_ruta_carpeta.text()
        ruta_outputs = os.path.join(ruta_carpeta, "outputs")
        self.separator.separate_to_file(self.ruta_audio_procesar, ruta_outputs, duration=self.duracion_segundos, filename_format='{instrument}.wav')
        os.remove(self.ruta_audio_procesar)
        os.remove(f"{ruta_outputs}/accompaniment.wav")
        self.ruta_audio_procesar = f"{ruta_outputs}/vocals.wav"

        self.app_window.update_progress_signal.emit(self.app_window.barra_de_progreso.value() + self.app_window.barra_de_progreso.value())

    def eliminar_ruido(self, suprimir_ruido):
        self.app_window.etiqueta_progreso.setText("Suprimiendo ruido...")
        ruta_carpeta = self.app_window.txt_ruta_carpeta.text()
        ruta_outputs = os.path.join(ruta_carpeta, "outputs")
        ruta_audio_sin_ruido = os.path.join(ruta_outputs, "audio_combinado_sin_ruido.wav")
        sr = 44100
        porcentaje_reduccion = float(suprimir_ruido/100)
        rate, data = wavfile.read(self.ruta_audio_procesar)
        orig_shape = data.shape
        data = np.reshape(data, (2, -1))
        
        ruido_reducido = nr.reduce_noise(y=data, sr=sr, stationary=True, prop_decrease=porcentaje_reduccion)  
        
        wavfile.write(ruta_audio_sin_ruido, sr, ruido_reducido.reshape(orig_shape))
        os.remove(self.ruta_audio_procesar)
        self.ruta_audio_procesar = ruta_audio_sin_ruido
        
        self.app_window.update_progress_signal.emit(self.app_window.barra_de_progreso.value() + self.app_window.barra_de_progreso.value())
    
    def eliminar_silencios_suave(self):
        self.app_window.etiqueta_progreso.setText("Removiendo silencios...")
        ruta_carpeta = self.app_window.txt_ruta_carpeta.text()
        ruta_outputs = os.path.join(ruta_carpeta, "outputs")

        fs, audio = aIO.read_audio_file(self.ruta_audio_procesar)
        segments = aS.silence_removal(audio, fs, 0.020, 0.020, smooth_window=0.5, weight=0.6, plot=False)

        audio_combinado = AudioSegment.empty()

        for segment in segments:
            start, end = segment
            audio_segment = audio[int(start * fs):int(end * fs)]

            bytes_io = io.BytesIO()
            wavfile.write(bytes_io, fs, audio_segment)
            bytes_io.seek(0)
            audio_segment = AudioSegment.from_file(bytes_io, format="wav")
            audio_combinado += audio_segment

        ruta_audio_sin_silencios = os.path.join(ruta_outputs, "audio_combinado_sin_silencios.wav")
        audio_combinado.export(ruta_audio_sin_silencios, format="wav")

        os.remove(self.ruta_audio_procesar)
        self.ruta_audio_procesar = ruta_audio_sin_silencios

        self.app_window.update_progress_signal.emit(self.app_window.barra_de_progreso.value() + self.app_window.barra_de_progreso.value())
        
    def eliminar_silencios_intenso(self):
        self.app_window.etiqueta_progreso.setText("Removiendo silencios...")
        ruta_carpeta = self.app_window.txt_ruta_carpeta.text()
        ruta_outputs = os.path.join(ruta_carpeta, "outputs")
        sound = AudioSegment.from_file(self.ruta_audio_procesar, format = "wav")
        audio_chunks = split_on_silence(sound
                            ,min_silence_len = 100
                            ,silence_thresh = -45
                            ,keep_silence = 30
        )
        audio_combinado = AudioSegment.empty()
        for chunk in audio_chunks:
            audio_combinado += chunk
            
        ruta_audio_sin_silencios = os.path.join(ruta_outputs, "audio_combinado_sin_silencios.wav")
        audio_combinado.export(ruta_audio_sin_silencios, format = "wav")
        os.remove(self.ruta_audio_procesar)
        self.ruta_audio_procesar = ruta_audio_sin_silencios
        
        self.app_window.update_progress_signal.emit(self.app_window.barra_de_progreso.value() + self.app_window.barra_de_progreso.value())
        
    def dividir_archivo_wav(self):
        self.app_window.etiqueta_progreso.setText("Generando dataset...")
        duracion_division_seleccionada = self.app_window.opcion_seleccionada_dividir.currentText()
        if duracion_division_seleccionada == "5 segundos": 
            duracion_maxima=5000
        elif duracion_division_seleccionada == "10 segundos": 
            duracion_maxima=10000
        elif duracion_division_seleccionada == "15 segundos": 
            duracion_maxima=15000
        else:
            duracion_maxima=20000  
        ruta_carpeta = self.app_window.txt_ruta_carpeta.text()
        ruta_outputs = os.path.join(ruta_carpeta, "outputs")
        ruta_dataset = os.path.join(ruta_outputs, "dataset")
        if not os.path.exists(ruta_dataset):    
            os.makedirs(ruta_dataset)   
        
        audio = AudioSegment.from_wav(self.ruta_audio_procesar)
        duracion_maxima_ms = duracion_maxima      
        duracion_total_ms = len(audio)   
        num_segmentos = (duracion_total_ms + duracion_maxima_ms - 1) // duracion_maxima_ms
        
        for i in range(num_segmentos):
            inicio_ms = i * duracion_maxima_ms
            fin_ms = min((i + 1) * duracion_maxima_ms, duracion_total_ms)
            segmento = audio[inicio_ms:fin_ms]            
            nombre_segmento = f"audio_{i+1}.wav"
            segmento.export(f"{ruta_dataset}/{nombre_segmento}", format="wav")
            
        self.calcular_duracion_total(ruta_dataset, self.app_window.etiqueta_duracion_salida_audios)
           
        self.app_window.update_progress_signal.emit(100)
            
    def generar_dataset(self):
        self.tecnicas_procesamiento = 5
        extraer_voz = self.app_window.opcion_seleccionada_voz.currentText()
        suprimir_ruido = self.app_window.slider_suprimir_ruido.value()
        eliminar_silencio = self.app_window.opcion_seleccionada_silencio.currentText()
        if extraer_voz == "No":
            self.tecnicas_procesamiento -= 1
        if suprimir_ruido == 0:
            self.tecnicas_procesamiento -= 1
            
        self.combinar_audios()
        if extraer_voz == "Si": 
            self.extraer_voz()
        if suprimir_ruido > 0: 
            self.eliminar_ruido(suprimir_ruido)
        if eliminar_silencio == "Alta tolerancia":
            self.eliminar_silencios_suave()
        else:
            self.eliminar_silencios_intenso()
        self.dividir_archivo_wav()
        
        self.app_window.etiqueta_progreso.setText("Completado")
        self.app_window.btnProcesar.setEnabled(True)
        self.app_window.btnSeleccionarRuta.setEnabled(True)
        
    def procesar_audios(self):
        self.app_window.btnProcesar.setEnabled(False)
        self.app_window.btnSeleccionarRuta.setEnabled(False)
        hilo_procesamiento = Thread(target=self.generar_dataset)
        hilo_procesamiento.start()
        
