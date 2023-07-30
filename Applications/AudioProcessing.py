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

separator = Separator('spleeter:2stems', multiprocess=False)  
   
class AudioProcessing():
    def __init__(self, app_window):
        self.ruta_audio_procesar = None
        self.tecnicas_procesamiento = None
        self.duracion_segundos = None
        self.audios_seleccionados = None
        self.etiqueta_duracion_entrada_audios = None
        self.app_window = app_window
        
    def calcular_duracion_total(self, ruta_carpeta, lbl_duracion):
        global duracion_segundos, audios_seleccionados
        audios_seleccionados = None
        archivos = os.listdir(ruta_carpeta)
        archivos_audio = [archivo for archivo in archivos if archivo.lower().endswith((".mp3", ".wav", ".wma"))]
        duracion_total_ms = 0
        for archivo in archivos_audio:
            ruta_audio = os.path.join(ruta_carpeta, archivo)
            audio = AudioSegment.from_file(ruta_audio)
            if lbl_duracion == self.app_window.etiqueta_duracion_entrada_audios:
                if audios_seleccionados is None:
                    audios_seleccionados = audio
                else:
                    audios_seleccionados += audio
            duracion_total_ms += len(audio)

        # Convertir la duración total a formato horas:minutos:segundos
        segundos_totales = duracion_total_ms / 1000
        duracion_segundos = float(round(segundos_totales))
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
        global ruta_audio_procesar, tecnicas_procesamiento, audios_seleccionados
        self.app_window.etiqueta_progreso.setText("Combinando audios...")
        ruta_carpeta = self.app_window.txt_ruta_carpeta.text()
        ruta_outputs = os.path.join(ruta_carpeta, "outputs")
        if not os.path.exists(ruta_outputs):
            os.makedirs(ruta_outputs)

        ruta_audio_procesar = os.path.join(ruta_outputs, "audio_combinado.wav")
        audios_seleccionados.export(ruta_audio_procesar, format="wav")
            
        self.app_window.update_progress_signal.emit(int(self.app_window.barra_de_progreso.maximum() / tecnicas_procesamiento))
 
    def extraer_voz(self):
        global ruta_audio_procesar, duracion_segundos, separator
        self.app_window.etiqueta_progreso.setText("Extrayendo voz...")
        ruta_carpeta = self.app_window.txt_ruta_carpeta.text()
        ruta_outputs = os.path.join(ruta_carpeta, "outputs")
        separator.separate_to_file(ruta_audio_procesar, ruta_outputs, duration=duracion_segundos, filename_format='{instrument}.wav')
        os.remove(ruta_audio_procesar)
        os.remove(f"{ruta_outputs}/accompaniment.wav")
        ruta_audio_procesar = f"{ruta_outputs}/vocals.wav"
        
        self.app_window.update_progress_signal.emit(self.app_window.barra_de_progreso.value() + self.app_window.barra_de_progreso.value())
            
    def eliminar_ruido(self):
        global ruta_audio_procesar
        self.app_window.etiqueta_progreso.setText("Suprimiendo ruido...")
        ruta_carpeta = self.app_window.txt_ruta_carpeta.text()
        ruta_outputs = os.path.join(ruta_carpeta, "outputs")
        rate, data = wavfile.read(ruta_audio_procesar)
        orig_shape = data.shape
        data = np.reshape(data, (2, -1))
        ruido_reducido = nr.reduce_noise(y=data, sr=rate, stationary=True)
        ruta_audio_sin_ruido = os.path.join(ruta_outputs, "audio_combinado_sin_ruido.wav")
        wavfile.write(ruta_audio_sin_ruido, rate, ruido_reducido.reshape(orig_shape))
        os.remove(ruta_audio_procesar)
        ruta_audio_procesar = ruta_audio_sin_ruido
        
        self.app_window.update_progress_signal.emit(self.app_window.barra_de_progreso.value() + self.app_window.barra_de_progreso.value())
    
    def eliminar_silencios_suave(self):
        global ruta_audio_procesar, tecnicas_procesamiento
        self.app_window.etiqueta_progreso.setText("Removiendo silencios...")
        ruta_carpeta = self.txt_ruta_carpeta.text()
        ruta_outputs = os.path.join(ruta_carpeta, "outputs")

        fs, audio = aIO.read_audio_file(ruta_audio_procesar)
        segments = aS.silence_removal(audio, fs, 0.020, 0.020, smooth_window=0.5, weight=0.6, plot=False)

        # Crear un nuevo audio combinando los segmentos sin silencios
        audio_combinado = AudioSegment.empty()

        for segment in segments:
            start, end = segment
            audio_segment = audio[int(start * fs):int(end * fs)]

            # Convertir el arreglo NumPy a bytes usando io.BytesIO y scipy.wavfile.write
            bytes_io = io.BytesIO()
            wavfile.write(bytes_io, fs, audio_segment)

            bytes_io.seek(0)

            # Crear el AudioSegment a partir de los bytes
            audio_segment = AudioSegment.from_file(bytes_io, format="wav")

            audio_combinado += audio_segment

        # Guardar el nuevo audio sin silencios
        ruta_audio_sin_silencios = os.path.join(ruta_outputs, "audio_combinado_sin_silencios.wav")
        audio_combinado.export(ruta_audio_sin_silencios, format="wav")

        # Eliminar el archivo de audio original
        os.remove(ruta_audio_procesar)
        ruta_audio_procesar = ruta_audio_sin_silencios

        # Actualizar la barra de progreso
        self.app_window.update_progress_signal.emit(self.app_window.barra_de_progreso.value() + self.app_window.barra_de_progreso.value())
        
    def eliminar_silencios_intenso(self):
        global ruta_audio_procesar, tecnicas_procesamiento
        self.app_window.etiqueta_progreso.setText("Removiendo silencios...")
        ruta_carpeta = self.app_window.txt_ruta_carpeta.text()
        ruta_outputs = os.path.join(ruta_carpeta, "outputs")
        sound = AudioSegment.from_file(ruta_audio_procesar, format = "wav")
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
        os.remove(ruta_audio_procesar)
        ruta_audio_procesar = ruta_audio_sin_silencios
        
        self.app_window.update_progress_signal.emit(self.app_window.barra_de_progreso.value() + self.app_window.barra_de_progreso.value())
        
    def dividir_archivo_wav(self):
        global ruta_audio_procesar
        self.app_window.etiqueta_progreso.setText("Generando dataset...")
        duracion_maxima=15000
        ruta_carpeta = self.app_window.txt_ruta_carpeta.text()
        ruta_outputs = os.path.join(ruta_carpeta, "outputs")
        ruta_dataset = os.path.join(ruta_outputs, "dataset")
        if not os.path.exists(ruta_dataset):    
            os.makedirs(ruta_dataset)   
        
        # Cargar el archivo WAV
        audio = AudioSegment.from_wav(ruta_audio_procesar)
        
        # Duración máxima en milisegundos (15 segundos por defecto)
        duracion_maxima_ms = duracion_maxima
        
        # Obtener la duración total del audio
        duracion_total_ms = len(audio)
        
        # Número total de segmentos
        num_segmentos = (duracion_total_ms + duracion_maxima_ms - 1) // duracion_maxima_ms
        
        for i in range(num_segmentos):
            inicio_ms = i * duracion_maxima_ms
            fin_ms = min((i + 1) * duracion_maxima_ms, duracion_total_ms)
            
            # Extraer el segmento
            segmento = audio[inicio_ms:fin_ms]
            
            nombre_segmento = f"audio_{i+1}.wav"
            segmento.export(f"{ruta_dataset}/{nombre_segmento}", format="wav")
            
        self.calcular_duracion_total(ruta_dataset, self.app_window.etiqueta_duracion_salida_audios)
           
        self.app_window.update_progress_signal.emit(100)
            
    def generar_dataset(self):
        global tecnicas_procesamiento
        tecnicas_procesamiento = 5
        extraer_voz = self.app_window.opcion_seleccionada_voz.currentText()
        suprimir_ruido = self.app_window.opcion_seleccionada_ruido.currentText()
        eliminar_silencio = self.app_window.opcion_seleccionada_silencio.currentText()
        if extraer_voz == "No":
            tecnicas_procesamiento -= 1
        if suprimir_ruido == "No":
            tecnicas_procesamiento -= 1
            
        self.combinar_audios()
        if extraer_voz == "Si": 
            self.extraer_voz()
        if suprimir_ruido == "Si": 
            self.eliminar_ruido()
        if eliminar_silencio == "Alta tolerancia":
            self.eliminar_silencios_suave()
        else:
            self.eliminar_silencios_intenso()
        self.dividir_archivo_wav()
        
        self.app_window.etiqueta_progreso.setText("Completado")
        
    def procesar_audios(self):
        hilo_procesamiento = Thread(target=self.generar_dataset)
        hilo_procesamiento.start()
        self.app_window.btnProcesar.setEnabled(False)
