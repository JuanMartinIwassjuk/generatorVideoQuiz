import openai
from openai import OpenAI
import json
import os
from config import API_KEY, MODEL_NAME
from pathlib import Path
client = OpenAI(api_key=API_KEY)
def get_openai_response_in_json_format(number_of_questions, number_of_options, difficulty_level, topic):
    if ((comparar_parametros_con_json(number_of_questions, number_of_options, difficulty_level, topic)==False)): # Si Son iguales los parámetros actuales con la consulta anterior
        openai.api_key = API_KEY
        model = MODEL_NAME
        prompt = f"generate {number_of_questions} specific questions with a difficulty level of {difficulty_level} about the topic {topic}"
        messages = [
            {'role': 'system', 'content': f'have {number_of_options} options for each question, including the correct answer,dont use single quote, and your response in JSON format like this:openkey "questions": [ openkey "question": "Sample question?", "options": ["Option A", "Option B", "Option C"], "correct_answer": "Option A" closedkey ] closedkey'},
            {'role': 'user', 'content': prompt}
        ]
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0.3 # Nivel de creatividad, el más alto es 1 que podría llegar a ser menos preciso
        )
        json_response = response["choices"][0]["message"]["content"]
        print(json_response)
        guardar_datos_en_json(number_of_questions, number_of_options, difficulty_level, topic)
        with open(os.getcwd()+'/response'+'/'+"data.txt", "w") as file:
            file.write(json_response)
        return json_response
    else: return obtener_contenido_txt()
def guardar_datos_en_json(number_of_questions, number_of_options, difficulty_level, topic):
    # Crear un diccionario con los datos
    data = {
        "number_of_questions": number_of_questions,
        "number_of_options": number_of_options,
        "difficulty_level": difficulty_level,
        "topic": topic
    }
    with open(os.getcwd()+'/response'+'/'+"lastParameters.txt", "w") as file:
        # Escribir los datos en formato JSON
        json.dump(data,file)
def comparar_parametros_con_json(number_of_questions, number_of_options, difficulty_level, topic):
    if (os.path.getsize(os.getcwd()+'/response'+'/'+"lastParameters.txt") != 0):#No Esta vacio
        # Cargar los datos del archivo JSON
        with open(os.getcwd()+'/response'+'/'+"lastParameters.txt", "r") as file:
            data = json.load(file)
        # Comparar los valores con los parámetros
        if (data["number_of_questions"] == number_of_questions and
            data["number_of_options"] == number_of_options and
            data["difficulty_level"] == difficulty_level and
            data["topic"] == topic):
            return True
        else:
            return False
    else: return False
def obtener_contenido_txt():
    ruta_archivo = os.path.join(os.getcwd(), 'response', 'data.txt')
    with open(ruta_archivo, 'r') as archivo:
        contenido = archivo.read()
    return contenido
def download_questions_audios_local(questions):
    for index_pregunta, question in enumerate(questions):
        speech_file_path = Path(__file__).parent / "audio" / (str(index_pregunta) + ".mp3")
        response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=question["question"]
        )
        response.stream_to_file(speech_file_path)