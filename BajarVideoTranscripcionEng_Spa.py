import os
import shutil

# Establecer las variables de entorno
os.environ['CUDA_HOME'] = '/usr/local/cuda-12.3'
os.environ['LD_LIBRARY_PATH'] = os.path.join(os.environ['CUDA_HOME'], 'targets/x86_64-linux/lib/stubs') + ':' + os.environ.get('LD_LIBRARY_PATH', '')
os.environ['LD_LIBRARY_PATH'] = os.path.join(os.environ['CUDA_HOME'], 'lib64') + ':' + os.environ.get('LD_LIBRARY_PATH', '')
os.environ['PATH'] = os.path.join(os.environ['CUDA_HOME'], 'bin') + ':' + os.environ.get('PATH', '')

os.environ['CUDNN_HOME'] = '/home/javier/cosas/cudnn-linux-x86_64-8.8.1.3_cuda11-archive'
os.environ['LD_LIBRARY_PATH'] = os.path.join(os.environ['CUDNN_HOME'], 'lib64') + ':' + os.environ.get('LD_LIBRARY_PATH', '')
os.environ['CPATH'] = os.path.join(os.environ['CUDNN_HOME'], 'include') + ':' + os.environ.get('CPATH', '')
os.environ['LIBRARY_PATH'] = os.path.join(os.environ['CUDNN_HOME'], 'lib64') + ':' + os.environ.get('LIBRARY_PATH', '')

# Verificar las variables de entorno
# for var in ['CUDA_HOME', 'LD_LIBRARY_PATH', 'PATH', 'CUDNN_HOME', 'CPATH', 'LIBRARY_PATH']:
#     print(f'{var}: {os.environ.get(var)}')


base_media_path = os.path.join(os.getcwd(), 'media_temporal')
# si no existe la carpeta media, la creamos
if not os.path.exists(base_media_path):
    os.makedirs(base_media_path)

# nombre del video a crear dentro de la carpeta media
# path_video = os.path.join(media_path, 'trainingFinetuning.mp4')

base_output_path = os.path.join(os.getcwd(), 'output')
# si no existe la carpeta media, la creamos
if not os.path.exists(base_output_path):
    os.makedirs(base_output_path)


media_path = ""
output_path = ""



# export TF_ENABLE_ONEDNN_OPTS=0 #para desactivar el optimizador que puede dar problemas de accuracy
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'


import subprocess
import pkg_resources

try:
    # Intenta importar el paquete
    pkg_resources.get_distribution('pytube')
    print('pytube ya está instalado.')
except pkg_resources.DistributionNotFound:
    # Si el paquete no está instalado, instálalo
    print('Instalando pytube...')
    subprocess.run(['pip', 'install', 'pytube'])
    print('pytube instalado exitosamente.')


from pytube import YouTube


def Download(path, link):
    youtubeObject = YouTube(link)
    youtubeObject = youtubeObject.streams.get_highest_resolution()
    print("Downloading...")
    try:
        youtubeObject.download(filename=path)
    except:
        print("An error has occurred")
    print("Download is completed successfully")
    

# link = input("Enter the YouTube video URL: ")
# Download(link)

import subprocess

def convertir_video_a_audio(path_video, output_audio):
    comando = [
        "ffmpeg", "-y", "-i", path_video, 
        "-c:a", "libmp3lame", "-qscale:a", "1", output_audio
    ]
    subprocess.run(comando)


def transcribir_video_eng_spa(path_video, output_audio, nombre_transcripcion, nombre_transcripcion_es, video_transcrito_path):
    comando = [
        "ffmpeg", "-y", "-i", path_video, 
        "-i", output_audio, 
        "-i", nombre_transcripcion, 
        "-i", nombre_transcripcion_es, 
        "-map", "0:v", "-map", "1:a", "-map", "2", "-map", "3",
        "-metadata:s:s:0", "language=eng", 
        "-metadata:s:s:1", "language=spa", 
        "-c:v", "copy", "-c:a", "aac", "-c:s", "mov_text", 
        video_transcrito_path
    ]
    subprocess.run(comando)



def transcribir_audio_con_whisper(output_audio, carpeta_transcripcion):
    comando = [
        "whisper", output_audio, "--task", "transcribe", 
        "--model", "large-v3", "--verbose", "False", 
        "--output_dir", carpeta_transcripcion
    ]
    subprocess.run(comando)


def transcribir_audio_con_whisper_spa(output_audio, carpeta_transcripcion_es):
    comando = [
        "whisper", output_audio, "--task", "transcribe", 
        "--model", "large-v3", "--language", "Spanish", 
        "--verbose", "False", "--output_dir", carpeta_transcripcion_es
    ]
    subprocess.run(comando)


from pytube import YouTube, Playlist

def identificar_y_obtener_urls_nombres(url):
    global media_path
    global output_path

    resultados = []
    if "playlist?list=" in url:
        # Es una playlist
        playlist = Playlist(url)
        nombre_carpeta = playlist.title

        for video_url in playlist.video_urls:
            video = YouTube(video_url)
            resultados.append((video.title, video_url))
    else:
        # Es un video individual
        video = YouTube(url)
        nombre_carpeta = video.title
        resultados.append((video.title, url))

    media_path = os.path.join(base_media_path, nombre_carpeta)
    if not os.path.exists(media_path):
        os.makedirs(media_path)
    output_path = os.path.join(base_output_path, nombre_carpeta)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    return resultados

if __name__ == "__main__":
    url = input("Ingresa la URL de YouTube: ")
    videos = identificar_y_obtener_urls_nombres(url)
    for nombre, video_url in videos:
        print("Preparando: ", f"{nombre}: {video_url}")
        path_video = os.path.join(media_path, f"{nombre}.mp4")
        Download(path_video, video_url)
        output_audio = path_video.replace(".mp4", ".mp3")
        carpeta_transcripcion = os.path.join(output_path, "audio_transcription")
        carpeta_transcripcion_es = os.path.join(output_path, "audio_transcription_es")
        #coger solo nombre del video sin path
        nombre_video = os.path.basename(path_video)
        fichero_transcripcion = nombre_video.replace(".mp4", ".vtt")
        nombre_transcripcion = os.path.join(carpeta_transcripcion, fichero_transcripcion)
        nombre_transcripcion_es = os.path.join(carpeta_transcripcion_es, fichero_transcripcion)
        video_transcrito_path = os.path.join(output_path, nombre_video.replace(".mp4", "_transcribed.mp4"))


        #SEPARAMOS EL AUDIO EN OTRO FICHERO (LUEGO LO JUNTAREMOS OTRA VEZ)
        # !ffmpeg -y -i {path_video} -c:a libmp3lame -qscale:a 1 {output_audio}
        convertir_video_a_audio(path_video, output_audio)

        #generamos la transcripción con whisper
        # !whisper  {output_audio} --task transcribe --model large --verbose False --output_dir {carpeta_transcripcion}
        transcribir_audio_con_whisper(output_audio, carpeta_transcripcion)

        #generamos la transcripción (con traducción inversa de inglés a español) con whisper
        # !whisper  {output_audio} --task transcribe --model large-v2 --language="Spanish" --verbose False --output_dir {carpeta_transcripcion_es}        
        transcribir_audio_con_whisper_spa(output_audio, carpeta_transcripcion_es)

        # !ffmpeg -y -i {path_video} -i {output_audio} -i {nombre_transcripcion} -i {nombre_transcripcion_es} -map 0:v -map 1:a -map 2 -map 3 -metadata:s:s:0 language=eng -metadata:s:s:1 language=spa -c:v copy -c:a aac -c:s mov_text {video_transcrito_path}
        transcribir_video_eng_spa(path_video, output_audio, nombre_transcripcion, nombre_transcripcion_es, video_transcrito_path)

    # borramos la carpeta temporal
    shutil.rmtree(base_media_path)