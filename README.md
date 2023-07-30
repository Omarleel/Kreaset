# Kreaset - Documentación del programa

## Introducción
Kreaset es una aplicación de procesamiento de audio desarrollada por Cliver Omar Flores Pacheco. Su objetivo es facilitar la generación de datasets de audio para tareas de procesamiento y análisis de señales de sonido.

## Requisitos
- FFmpeg
- Python 3.6 o superior
- PyQt5
- pydub
- scipy
- noisereduce
- pyAudioAnalysis
- [Spleeter](https://github.com/deezer/spleeter)

## Descripción general del programa
Kreaset proporciona una interfaz gráfica de usuario (GUI) para facilitar el procesamiento y análisis de archivos de audio en formato MP3, WAV o WMA. El programa cuenta con diversas técnicas de procesamiento de audio, como la extracción de voz, la supresión de ruido y la eliminación de silencios, que pueden aplicarse a los archivos de audio seleccionados. Además, Kreaset tiene la capacidad de combinar varios archivos de audio en uno solo y dividir un archivo de audio grande en segmentos más pequeños para la creación de un dataset.

## Interfaz de usuario
La interfaz de usuario de Kreaset se compone de los siguientes elementos:

1. Etiqueta de "Directorio del dataset": Muestra un mensaje indicando que se debe seleccionar un directorio que contenga los archivos de audio para procesar.

2. Cuadro de texto "Ruta de la carpeta": Muestra la ruta del directorio seleccionado que contiene los archivos de audio.

3. Botón "Seleccionar": Permite seleccionar el directorio que contiene los archivos de audio a procesar.

4. Etiqueta de "Archivos de audio": Muestra la cantidad total de archivos de audio encontrados en el directorio seleccionado.

5. Etiqueta de "Duración entrada": Muestra la duración total de los archivos de audio seleccionados en formato horas, minutos y segundos.

6. Etiqueta de "Suprimir ruido": Permite seleccionar si se desea aplicar la técnica de supresión de ruido a los archivos de audio.

7. Cuadro desplegable "Si/No": Permite seleccionar "Si" o "No" para activar o desactivar la técnica de supresión de ruido, respectivamente.

8. Etiqueta de "Extraer voz": Permite seleccionar si se desea aplicar la técnica de extracción de voz a los archivos de audio.

9. Cuadro desplegable "Si/No": Permite seleccionar "Si" o "No" para activar o desactivar la técnica de extracción de voz, respectivamente.

10. Etiqueta de "Remover silencio": Permite seleccionar el nivel de tolerancia para eliminar silencios en los archivos de audio.

11. Cuadro desplegable "Alta tolerancia/Baja tolerancia": Permite seleccionar el nivel de tolerancia para eliminar silencios, ya sea alta o baja.

12. Botón "Generar dataset": Inicia el procesamiento de los archivos de audio seleccionados con las técnicas elegidas.

13. Etiqueta de progreso: Muestra el estado actual del procesamiento, como "Sin procesar" o "Completado".

14. Barra de progreso: Representa visualmente el progreso del procesamiento de los archivos de audio.

15. Etiqueta de "Duración salida": Muestra la duración total de los archivos de audio procesados (después de aplicar las técnicas) en formato horas, minutos y segundos.

## Procesamiento de audio
Kreaset permite realizar las siguientes técnicas de procesamiento de audio:

### Combinar audios
- Descripción: Combina varios archivos de audio seleccionados en uno solo.
- Funcionalidad: Los archivos de audio seleccionados se concatenan para crear un único archivo WAV llamado "audio_combinado.wav" en una carpeta llamada "outputs" dentro del directorio seleccionado.

### Extracción de voz
- Descripción: Utiliza el modelo de separación de fuentes de Spleeter para extraer la pista vocal de los archivos de audio seleccionados.
- Funcionalidad: Los archivos de audio se procesan utilizando el modelo preentrenado "spleeter:2stems" de Spleeter. La pista vocal extraída se guarda en un archivo WAV llamado "vocals.wav" en la carpeta "outputs".

### Supresión de ruido
- Descripción: Aplica la técnica de reducción de ruido de noisereduce a los archivos de audio seleccionados.
- Funcionalidad: Se calcula la señal de ruido en los archivos de audio y se reduce el ruido en la señal original. El archivo de audio resultante se guarda en la carpeta "outputs" con el nombre "audio_combinado_sin_ruido.wav".

### Eliminación de silencios
- Descripción: Elimina los segmentos de silencio de los archivos de audio seleccionados.
- Funcionalidad: Los archivos de audio se procesan para eliminar los intervalos de silencio. Se proporciona una opción para seleccionar "Alta tolerancia" o "Baja tolerancia", que afecta la sensibilidad de detección de silencios. El archivo de audio resultante se guarda en la carpeta "outputs" con el nombre "audio_combinado_sin_silencios.wav".

### Dividir archivo WAV
- Descripción: Divide un archivo de audio grande en segmentos más pequeños para la creación de un dataset.
- Funcionalidad: El archivo de audio seleccionado se divide en segmentos de duración máxima (por defecto, 15 segundos) y se guardan en la carpeta "dataset" dentro de la carpeta "outputs". Los segmentos se nombran como "audio_1.wav", "audio_2.wav", etc.

## Progreso y finalización
El proceso de procesamiento de audio se realiza en segundo plano utilizando hilos, lo que permite que la interfaz de usuario siga siendo interactiva y responda durante el procesamiento. La barra de progreso se actualiza para indicar el progreso del procesamiento. Una vez completado el procesamiento, se muestra la etiqueta "Completado" en la interfaz de usuario.

## Uso del programa
1. Ejecute el programa usando Python y se abrirá la ventana principal de Kreaset.
2. Haga clic en el botón "Seleccionar" y seleccione el directorio que contiene los archivos de audio que desea procesar.
3. Se mostrará la cantidad total de archivos de audio encontrados en el directorio seleccionado y la duración total de los archivos de audio.
4. Seleccione las técnicas de procesamiento de audio que desee aplicar utilizando los cuadros desplegables.
5. Haga clic en el botón "Generar dataset" para iniciar el procesamiento de los archivos de audio con las técnicas seleccionadas.
6. El progreso del procesamiento se muestra en la etiqueta y la barra de progreso.
7. Una vez completado el procesamiento, se mostrará la etiqueta "Completado" y la duración total de los archivos de audio procesados en la etiqueta "Duración salida".

![Interfaz gráfica del programa](https://raw.githubusercontent.com/Omarleel/Kreaset/main/Assets/interfaz_grafica.jpg)

## Conclusión
Kreaset es una herramienta útil para el procesamiento y análisis de archivos de audio, especialmente cuando se trabaja con datasets grandes o se requiere la aplicación de técnicas específicas para la preparación de los datos. La interfaz de usuario facilita el uso del programa y permite a los usuarios procesar archivos de audio de manera eficiente y efectiva.

## Pruebas
Para correr el programa, puedes ejecutar el siguiente conjunto de comandos:
```bash
# Clonar el repositorio y acceder a la carpeta del programa
git clone https://github.com/Omarleel/Kreaset
cd Kreaset
# Ejecutar el script
py kreaset.py

