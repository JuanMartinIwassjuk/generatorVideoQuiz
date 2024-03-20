import os
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from urllib.parse import urlparse, parse_qs
from urllib.parse import urlparse
from mutagen.mp3 import MP3

def authenticate():
    creds = None
    # Comprueba si ya hay credenciales almacenadas
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    # Si no hay credenciales válidas, solicita la autorización del usuario
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', ['https://www.googleapis.com/auth/drive']
            )
            creds = flow.run_local_server(port=0)
        # Guarda las credenciales para usarlas la próxima vez
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds
def upload_file_to_google_drive(file_path, file_name):
    creds = authenticate()
    drive_service = build('drive', 'v3', credentials=creds)
    
    # Crea el archivo en Google Drive
    file_metadata = {
        'name': file_name,
        'viewersCanCopyContent': True  # Esto es necesario para archivos que no son de Google Docs
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='webViewLink, id'
    ).execute()

    file_id = file.get('id')
    
    # Actualiza los permisos del archivo para hacerlo público
    drive_service.permissions().create(
        fileId=file_id,
        body={'role': 'reader', 'type': 'anyone'}
    ).execute()
    
    # Obtiene la URL pública del archivo
    file_url = file.get('webViewLink')

    return file_url



def obtener_Url_Del_Archivo_De_Drive(Num_audio):
    file_path = os.getcwd()+'/audio'+str(Num_audio)+'.mp3'
    file_name = '/audio'+str(Num_audio)+'.mp3'
    file_url = upload_file_to_google_drive(file_path, file_name)
    if file_url:
        print("URL del archivo:", file_url)
        return file_url
    else:
        print("Error al subir archivo a Google Drive.")
def eliminar_archivos_en_ruta(ruta):
    """
    Elimina todos los archivos en la ruta especificada.
    :param ruta: La ruta donde se encuentran los archivos a eliminar.
    """
    try:
        # Verificar si la ruta existe y es un directorio
        if os.path.isdir(ruta):
            # Iterar sobre los archivos en la ruta y eliminarlos
            for archivo in os.listdir(ruta):
                ruta_archivo = os.path.join(ruta, archivo)
                if os.path.isfile(ruta_archivo):
                    os.remove(ruta_archivo)
                    print(f"Archivo eliminado: {ruta_archivo}")
            print("Todos los archivos han sido eliminados.")
        else:
            print(f"La ruta especificada '{ruta}' no es un directorio válido.")
    except Exception as e:
        print(f"Error al intentar eliminar archivos en la ruta '{ruta}': {e}")
def eliminar_archivo_de_drive(file_url):
    try:
        # Extraer el ID del archivo de la URL
        file_id = file_url.split("/")[5]
        # Autenticar
        creds = authenticate()
        drive_service = build('drive', 'v3', credentials=creds)
        # Eliminar el archivo
        drive_service.files().delete(fileId=file_id).execute()
        print("Archivo eliminado de Google Drive.")
    except Exception as e:
        print(f"Error al intentar eliminar el archivo de Google Drive: {e}")
def obtener_cantidad_archivos_en_carpeta(url_archivo):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    # Parsear la URL del archivo para obtener su ID
    id_archivo = obtener_id_desde_url(url_archivo)
    print(f"el id de archivo es {id_archivo}")
    # Obtener información del archivo
    archivo = service.files().get(fileId=id_archivo, fields='parents').execute()
    id_carpeta = archivo.get('parents')[0]
    # Obtener la lista de archivos en la carpeta
    resultados = service.files().list(q="'{}' in parents and trashed=false".format(id_carpeta),
                                       fields='nextPageToken, files(id)').execute()
    cantidad_archivos = len(resultados.get('files', []))
    return cantidad_archivos
def obtener_id_desde_url(url_archivo):
    # Parsear la URL para obtener el ID del archivo
    parsed_url = urlparse(url_archivo)
    file_id = None
    # Buscar el índice del segmento que contiene '/file/d/'
    index = parsed_url.path.find('/file/d/')
    if index != -1:
        # Avanzar el índice al inicio del ID del archivo
        index += len('/file/d/')
        # Buscar el índice del siguiente '/' después del ID del archivo
        end_index = parsed_url.path.find('/', index)
        if end_index != -1:
            # Extraer el ID del archivo
            file_id = parsed_url.path[index:end_index]
    return file_id

def obtener_duracion_mp3_en_segundos(archivo_mp3): # os.path.abspath(os.path.join(os.getcwd(), 'audio', f"{1}.mp3"))
    try:
        # Obtener la duración del archivo MP3
        audio = MP3(archivo_mp3)
        duracion_segundos = audio.info.length
        return (str(duracion_segundos)+' s')
    except Exception as e:
        print("Error al obtener la duración del archivo MP3:", e)
        return None
