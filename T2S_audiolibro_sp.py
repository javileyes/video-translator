import subprocess

try:
    # Intenta importar el paquete
    import fairseq
    print('fairseq ya está instalado.')
except ImportError:
    # Si el paquete no está instalado, instálalo
    print('Instalando paquetes...')
    paquetes = ["pydub", "num2words", "fairseq", "sentencepiece", "huggingface_hub", "pdfplumber", "git+https://github.com/openai/whisper.git", "Levenshtein" ]

    # !pip install pydub
    # !pip install num2words
    # !pip install fairseq sentencepiece
    # !pip install huggingface_hub
    # !pip install pdfplumber
    # !pip install git+https://github.com/openai/whisper.git
    # !pip install Levenshtein
    for paquete in paquetes:
      try:
          subprocess.run(["pip", "install", paquete], check=True)
          print(f"Paquete '{paquete}' instalado exitosamente.")
      except subprocess.CalledProcessError as e:
          print(f"Error al instalar el paquete '{paquete}': {e}")


from pydub import AudioSegment, silence

def quitar_silencios(input_filepath, output_filepath, min_silence_len=1500, new_silence_len=750, silence_thresh=-60):
    """
    Elimina silencios largos de un archivo de audio.

    Parámetros:
    - input_filepath: ruta al archivo de audio de entrada (MP3).
    - output_filepath: ruta al archivo de audio de salida (MP3).
    - min_silence_len: duración mínima del silencio a eliminar (en milisegundos).
    - new_silence_len: duración de los nuevos segmentos de silencio (en milisegundos).
    - silence_thresh: umbral de silencio (en dB).
    """

    # Cargar el archivo de audio
    audio_segment = AudioSegment.from_mp3(input_filepath)

    # Encuentra los segmentos de audio separados por silencios
    segments = silence.split_on_silence(audio_segment, min_silence_len=min_silence_len, silence_thresh=silence_thresh)

    # Crear un nuevo segmento de audio con silencios ajustados
    new_audio_segment = AudioSegment.empty()
    silence_chunk = AudioSegment.silent(duration=new_silence_len)  # Chunk de silencio de la nueva duración

    # Añade cada segmento de audio al nuevo audio, intercalando con los nuevos segmentos de silencio
    for segment in segments:
        new_audio_segment += segment + silence_chunk

    # Removemos el último chunk de silencio añadido
    new_audio_segment = new_audio_segment[:-new_silence_len]

    # Guarda el nuevo archivo de audio
    new_audio_segment.export(output_filepath, format="mp3")

  
# Diccionario con las traducciones
translations = {
    'Dr': 'Doctor',
    'Sr': 'Señor',
    'Sra': 'Señora',
    # Añade más traducciones aquí
}

def process_abrev(line):
    for abbr, full in translations.items():
        line = line.replace(f'{abbr}.', full)
        line = line.replace(f'{abbr} ', f'{full} ')
    return line

# Ejemplo de uso
# line1 = 'El Dr está hablando con el Sr. Pérez y la Sra. Gómez.'
# line2 = 'Buenos días Sr. Gómez.'

# new_line1 = process_abrev(line1)
# new_line2 = process_abrev(line2)

# print(new_line1)  # Debería imprimir: 'El Doctor está hablando con el Señor Pérez y la Señora Gómez.'
# print(new_line2)  # Debería imprimir: 'Buenos días Señor Gómez.'

import re
from num2words import num2words

def number_to_words(num_str):
    try:
        num = int(num_str)
        return num2words(num, lang='es')
    except ValueError:
        return "Por favor, introduzca un número válido."

def process_numbers_in_line(line):
    def replace_with_words(match):
        return number_to_words(match.group())

    return re.sub(r'\b\d+\b', replace_with_words, line)

# Ejemplo de uso
# line = "Tengo 3 manzanas y 15 naranjas, sumando un total de 18 frutas."
# new_line = process_numbers_in_line(line)
# print(new_line)
# Salida: "Tengo tres manzanas y quince naranjas, sumando un total de dieciocho frutas."

# Diccionario con las traducciones
translations = {
    '-': ',',
    '—': ','
    # Añade más traducciones aquí
}

def otras_traducciones(line):
    for old, new in translations.items():
        line = line.replace(old, new)
    return line

# Ejemplo de uso
# line1 = 'Hola —cómo estás—?'
# line2 = "El relato tuvo su origen en los primeros capítulos del Libro Rojo, compuesto por Bilbo Bolsón —el primer hobbit que fue famoso en el mundo entero— y que él tituló Historia de una ida y de una vuelta,"

# new_line1 = otras_traducciones(line1)
# new_line2 = otras_traducciones(line2)

# print(new_line1)  # Debería imprimir: 'Hola, cómo estás?'
# print(new_line2)  # Debería imprimir: 'Bien, gracias.'

def preprocesado_al_modelo(line):
    line_with_numbers = process_numbers_in_line(line)
    # print("numbers:", line_with_numbers)
    line_with_both = process_abrev(line_with_numbers)
    # print("abrev:", line_with_both)
    line_with_all = otras_traducciones(line_with_both)
    return line_with_all

# text = "Hola, esta es -una prueba-. ¿Está de acuerdo Sr. López? Voy a comprobar, Dr Alonso cuántas frases puede decir de 25 palabras de golpe."

# preprocesado_al_modelo(text)

#######################################################3
##PARA CARGAR MODELO FAIRSEQ###############
########################################33

from fairseq.checkpoint_utils import load_model_ensemble_and_task_from_hf_hub
from fairseq.models.text_to_speech.hub_interface import TTSHubInterface
import IPython.display as ipd
import torch  # Importamos PyTorch para poder usar la función `to()`

# Función para mover recursivamente todos los tensores en una estructura anidada a un dispositivo
def move_to_device(obj, device):
    if isinstance(obj, torch.Tensor):
        return obj.to(device)
    elif isinstance(obj, dict):
        return {key: move_to_device(value, device) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [move_to_device(item, device) for item in obj]
    else:
        return obj





def spanish_t2s(text):
    text = preprocesado_al_modelo(text)
    # Preparamos los datos de entrada para el modelo
    sample = TTSHubInterface.get_model_input(task, text)

    # Movemos los datos al dispositivo GPU
    sample = move_to_device(sample, 'cuda:0')

    # Realizamos la predicción
    wav, rate = TTSHubInterface.get_prediction(task, model, generator, sample)

    return wav, rate



import re
import pdfplumber

def leer_pdf(ruta_pdf, pagina_inicio=1):
    with pdfplumber.open(ruta_pdf) as archivo_pdf:
        for pagina in archivo_pdf.pages[pagina_inicio:]:
            yield pagina.extract_text()

def procesar_texto(ruta_pdf):
    word_count = 0
    current_paragraph = []

    parrafos = []
    texto_procesado = None
    for texto in leer_pdf(ruta_pdf):
        if not texto:  # Si el texto es None o está vacío, continúa con la siguiente iteración
            continue

        # del texto_procesado
        # Eliminar saltos de línea que no sean líneas en blanco que separen párrafos. También eliminar los retornos de carro.
        texto_procesado = re.sub(r'(?<!\n)\n(?!\n)', ' ', texto).replace('\r', '')

        # Iterar sobre cada carácter del texto
        for char in texto_procesado:
            if char == ' ':  # Contar las palabras
                word_count += 1

            current_paragraph.append(char)  # Añadir el carácter al párrafo actual

            # Dividir el párrafo si se encuentra con un signo de puntuación y hay más de 12 palabras
            if char in ['.', ',', ':', ';', '?', '!', '-', '—'] and word_count >= 13:
                parrafos.append(''.join(current_paragraph).strip())
                # del current_paragraph  # Ejemplo
                current_paragraph = []
                word_count = 0

        # Añadir el último párrafo si contiene texto
        if current_paragraph:
            parrafos.append(''.join(current_paragraph).strip())
            

    return parrafos


def quitar_puntuacion(texto):
    texto = texto.replace('.', '')
    texto = texto.replace(',', '')
    texto = texto.replace('?', '')
    texto = texto.replace('!', '')
    texto = texto.replace('¿', '')
    texto = texto.replace('¡', '')
    texto = texto.replace(';', '')
    texto = texto.replace(':', '')
    texto = texto.replace('(', '')
    texto = texto.replace(')', '')
    texto = texto.replace('[', '')
    texto = texto.replace(']', '')
    texto = texto.replace('{', '')
    texto = texto.replace('}', '')
    texto = texto.replace('"', '')
    texto = texto.replace("'", '')
    texto = texto.replace('`', '')
    texto = texto.replace('´', '')
    texto = texto.replace('’', '')
    texto = texto.replace('‘', '')
    texto = texto.replace('“', '')
    texto = texto.replace('”', '')
    texto = texto.replace('…', '')
    texto = texto.replace('«', '')
    texto = texto.replace('»', '')
    texto = texto.replace('–', '')
    texto = texto.replace('—', '')
    texto = texto.replace('−', '')
    texto = texto.replace('‐', '')
    texto = texto.replace('⁃', '')
    texto = texto.replace('‒', '')
    texto = texto.replace('―', '')
    texto = texto.replace('‹', '')
    texto = texto.replace('›', '')
    texto = texto.replace('•', '')
    texto = texto.replace('·', '')
    texto = texto.replace('‣', '')
    texto = texto.replace('⁌', '')
    texto = texto
    return texto



##############################################
#################  MAIN  #####################

print("recordatorio de uso del script: python T2S_audiolibro_sp.py <nombre_del_libro> <párrafo_inicial> <párrafo_final>\n si no se pasan parámetros, se usan los valores por defecto: libro.pdf, 0, -1")
PARRAFO_INICIAL = 0
PARRAFO_FINAL = -1
DESTINATION = "libro.pdf"
import sys
# si el comando se ejecuta con parámetro (texto entre comillas) entonces se usa ese texto como system_prompt
if len(sys.argv) > 1:
    DESTINATION = sys.argv[1]
    print("Libro: ", DESTINATION)

if len(sys.argv) > 2:
    PARRAFO_INICIAL = int(sys.argv[2])
    print("Párrafo inicial: ", PARRAFO_INICIAL)

if len(sys.argv) > 3:
    PARRAFO_FINAL = int(sys.argv[3])
    print("Párrafo final: ", PARRAFO_FINAL)

if len(sys.argv) == 1:
    print("No se han pasado parámetros. Se usará el valor por defecto: ", DESTINATION)

pdf_path = F'./{DESTINATION}'
print("Procesando todos los párrafos del libro... (puede tardar varios minutos)")
parrafos = procesar_texto(pdf_path)
parrafos = parrafos[PARRAFO_INICIAL:PARRAFO_FINAL]


# para librar memoria
import gc
gc.collect()


# VALIDAMOS AUDIO CON WHISPER
import whisper
modelWhisper = whisper.load_model('small')

import Levenshtein

texto1= "hola como estas"
texto2= "hola, como estas?"
# funcion que quita simbolos de puntuacion



import os
import torchaudio
import Levenshtein
import shutil
import subprocess

# Cargamos el modelo y la configuración desde el modelo preentrenado de Hugging Face
models, cfg, task = load_model_ensemble_and_task_from_hf_hub(
    "facebook/tts_transformer-es-css10",
    arg_overrides={"vocoder": "hifigan", "fp16": False}
)
model = models[0]

# Movemos el modelo al dispositivo GPU
model = model.to('cuda:0')

# Actualizamos la configuración con los datos del task
TTSHubInterface.update_cfg_with_data_cfg(cfg, task.data_cfg)

# Creamos el generador
generator = task.build_generator([model], cfg)




small_temp_files = []


print(f"Creando audio... cada párrafo desde {PARRAFO_INICIAL} hasta {PARRAFO_FINAL} se irá guardando en un archivo temporal y luego todos ellos se ensamblarán")

# crear carpeta temporal si no existe
carpetaTemporal = "./audioLibro_sp"
if not os.path.exists(carpetaTemporal):
    os.makedirs(carpetaTemporal)

# Itera sobre cada párrafo
for i, text in enumerate(parrafos):
    # print(f"Paragraph {i + 1}:\n{text}\n")
    print("creando audio de párrafo: ", i + PARRAFO_INICIAL)

    text = parrafos[i]
    text = preprocesado_al_modelo(text)

    # text = "pues, contaba el viaje de Bilbo hacia el este y la vuelta,"
    # print(f"Paragraph {i + 1}:\n{text}\n")
    # Genera el audio

    wav, rate = spanish_t2s(text)

    if len(wav.shape) == 1:
        wav = wav.unsqueeze(0)

    temp_file_name = f"{carpetaTemporal}/temp_{str(i).zfill(5)}.wav"
    torchaudio.save(temp_file_name, wav.to('cpu'), rate)

    similitud = 0
    contador = 0
    line = text
    longitud_texto = len(text.split())
    while True:

        prediction = modelWhisper.transcribe(temp_file_name, language="Spanish", temperature=0, beam_size=1)["text"]
        similitud = Levenshtein.ratio(quitar_puntuacion(line), quitar_puntuacion(prediction))
        # print("Linea: ", line)
        # print("Perdiction: ", prediction)
        # print("Similitud: ", similitud)
        # print("Contador: ", contador)


        # print("Provisional transcripted_sentence:", prediction)
        if (similitud > 0.96) or (similitud > 0.93 and longitud_texto < 24) or (similitud > 0.90 and contador > 8) or (similitud > 0.88 and contador > 11) or (similitud > 0.85 and contador > 15) or contador > 17:
            break
        else:
            contador += 1
            if contador > 2 and longitud_texto < 24 or contador > 4:
                line = " ".join(text.split()[:contador]) + "," + " ".join(text.split()[contador:])
            wav, rate = spanish_t2s(line)
            if len(wav.shape) == 1:
                wav = wav.unsqueeze(0)
            torchaudio.save(temp_file_name, wav.to('cpu'), rate)

    temp_file_name_definitivo = f"{carpetaTemporal}/temp_{str(i).zfill(5)}.mp3"
    # convertir .wav en .mp3
    # !ffmpeg -y -i "{temp_file_name}" "{temp_file_name_definitivo}"
    comando_ffmpeg = [
        "ffmpeg", "-loglevel", "panic", "-y", "-i", temp_file_name, temp_file_name_definitivo
    ]

    # Ejecutar el comando
    try:
        subprocess.run(comando_ffmpeg, check=True)
        # print("ffmpeg ejecutado exitosamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar ffmpeg: {e}")

    # eliminar .wav
    # !rm "{temp_file_name}"
    try:
        os.remove(temp_file_name)
        # print(f"Archivo '{temp_file_name}' eliminado exitosamente.")
    except OSError as e:
        print(f"Error al eliminar archivo: {e}") 

    # añadir fichero a la lista de ficheros temporales
    small_temp_files.append(temp_file_name_definitivo)


# Concatena todos los archivos mp3 grandes en uno final
# !ffmpeg -y -f concat -safe 0 -i <(for f in {' '.join(small_temp_files)}; do echo file ${"PWD"}/${"f"}; done) -c copy "{carpetaTemporal}/audioLibro_output.mp3"
archivo_salida = f"{carpetaTemporal}/audioLibro_output.mp3"

# Crear un archivo de lista de reproducción (playlist)
playlist_file = "playlist.txt"
with open(playlist_file, "w") as file:
    for f in small_temp_files:
        file.write(f"file '{os.path.join(os.getcwd(), f)}'\n")

# Construir el comando ffmpeg
comando_ffmpeg = [
    "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", playlist_file, "-c", "copy", archivo_salida
]

# Ejecutar el comando
try:
    subprocess.run(comando_ffmpeg, check=True)
    print("ffmpeg ejecutado exitosamente.")
except subprocess.CalledProcessError as e:
    print(f"Error al ejecutar ffmpeg: {e}")

# Eliminar el archivo de la lista de reproducción después del uso
os.remove(playlist_file)


quitar_silencios(f"{carpetaTemporal}/audioLibro_output.mp3", f"{carpetaTemporal}/audioLibro_output_sin_silencios.mp3")

# !cp "{carpetaTemporal}/audioLibro_output_sin_silencios.mp3" "./audioLibro_sp_output_sin_silencios.mp3"
archivo_origen = f"{carpetaTemporal}/audioLibro_output_sin_silencios.mp3"
archivo_destino = f"./{DESTINATION}.mp3"

# Copiar el archivo
try:
    shutil.copy(archivo_origen, archivo_destino)
    print("Archivo copiado exitosamente.")
except IOError as e:
    print(f"Error al copiar archivo: {e}")


shutil.rmtree(carpetaTemporal)


