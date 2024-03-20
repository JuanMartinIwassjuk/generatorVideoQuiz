import json
import requests
import audio
import time
import functions_videos
import os
from pathlib import Path
import generatorQuiz
from creatomate import Animation, Image, Element, Composition, Source, Video, Audio
from config import NUMBER_OF_QUESTIONS,NUMBER_OF_OPTIONS, LEVEL_OF_DIFFICULTY, TOPIC,BACKGROUND_IMG,AUTORIZACION


#data = '{ "questions": [ { "question": "Who is known as The King in the NBA?", "options": [ "LeBron James", "Kobe Bryant", "Stephen Curry" ], "correct_answer": "LeBron James" }, { "question": "Which team has won the most NBA championships?", "options": [ "Boston Celtics", "Los Angeles Lakers", "Chicago Bulls" ], "correct_answer": "Boston Celtics" }, { "question": "Which player holds the record for the most points scored in a single NBA game?", "options": [ "Wilt Chamberlain", "Michael Jordan", "Kobe Bryant" ], "correct_answer": "Wilt Chamberlain" }, { "question": "Who is the NBAs all-time leader in assists?", "options": [ "John Stockton", "Magic Johnson", "Steve Nash" ], "correct_answer": "John Stockton" } ] }'

background_list_dict = json.loads(BACKGROUND_IMG)

data = generatorQuiz.get_openai_response_in_json_format(NUMBER_OF_QUESTIONS,NUMBER_OF_OPTIONS, LEVEL_OF_DIFFICULTY, TOPIC)

quiz_data_dict=json.loads(data)

generatorQuiz.download_questions_audios_local(quiz_data_dict["questions"])

ruta_audios = Path(os.getcwd()+'/audio')

audioDrive=[]

while True:  #Espera a que se suban todos los archivos de forma local
    if len(list(ruta_audios.glob("*"))) >= NUMBER_OF_QUESTIONS:
        break
    time.sleep(1)

for index_pregunta, question in enumerate(quiz_data_dict["questions"]):#Esto sube los audios desde local a drive
    urlDrive = audio.upload_file_to_google_drive(os.getcwd()+'/audio'+'/'+str(index_pregunta)+'.mp3', '/audio'+'/'+str(index_pregunta)+'.mp3')
    audioDrive.append(urlDrive)



while True:  #Espera a que se suban todos los archivos al Drive
    if audio.obtener_cantidad_archivos_en_carpeta(urlDrive) >= NUMBER_OF_QUESTIONS:
        time.sleep(10)
        break
    time.sleep(1)    


text_start_anim = Animation(
    time="start s",
    duration="1.5 s",
    easing="quadratic-out",
    type="text-slide",
    scope="split-clip",
    split="line",
    distance="100%",
    direction="right",
    background_effect="disabled"
)

text_end_anim = Animation(
    time="end",
    duration="1 s",
    easing="quadratic-out",
    type="text-slide",
    direction="left",
    split="line",
    scope="element",
    distance="200%",
    reversed=True
)

comp_start_anim = Animation(
    time="start",
    duration="1 s",
    transition=True,
    type="wipe",
    fade=False,
    x_anchor="0%",
    end_angle="270°",
    start_angle="270°"
)

stroke_color = [{ "time": "0 s", "value": "#000000" }, { "time": "7.2 s", "value": "#000000" }, { "time": "7.5 s", "value": "#00ff00" }]

source = Source('mp4', 1080, 1920, functions_videos.generar_tiempo_video(NUMBER_OF_QUESTIONS))
background_music = Audio("Music", 18, "0 s", None, True, "b5dc815e-dcc9-4c62-9405-f94913936bf5", "5%", "2 s")
source.elements.append(background_music)
video = Video(source)


for index_pregunta, question in enumerate(quiz_data_dict["questions"]):
    composition = Composition("Question" + str(index_pregunta), 1, "10 s")

    question_text = Element("text", track=2, text=question["question"], y="21.80%", fill_color="#000000", background_color="#ffffff")
    question_text.animations.append(text_start_anim)
    question_text.animations.append(text_end_anim)
    composition.elements.append(question_text)
    question_to_speech = Audio("Audio" + str(index_pregunta), 10, "0 s", "5 s", True, audioDrive[index_pregunta], "100%", "0 s")
    composition.elements.append(question_to_speech)

    animation = Animation(easing='linear', type='scale', scope='element', start_scale='120%', fade=False)
    background_video = Image(type="video", source="05940918-3ab9-444e-b32f-1e39141f7282", track=1, time=0, duration=10, clip=True)
    background_video.animations.append(animation)
    image = Image(background_list_dict[index_pregunta], 1, 10, True, [])
    image.animations.append(animation)
    composition.elements.append(image)
    composition.elements.append(background_video)

    counter = Image("06311a89-c770-48e1-8a33-b5c1c417c787", 9, 5, True, [], y="7%", width="20%", height="12%", time=1.2)
    composition.elements.append(counter)

    countdown = Audio("countdown", 10, "1.2 s", "4.8 s", True, "3b591fe7-e995-4e18-9353-f38c122cc3fb", "5%", "0 s")
    composition.elements.append(countdown)
    correct = Audio("correct", 10, "7.2 s", "1.85 s", True, "530d3905-bd5b-4534-9532-f6657ed03296", "50%", "0 s")
    composition.elements.append(countdown)
    composition.elements.append(correct)

    if index_pregunta > 0:
        composition.animations.append(comp_start_anim)

    for index_opcion, option in enumerate(question["options"]):
        position_y = 52 + (10 * index_opcion)
        option_text = Element("text", track=index_opcion + 3, text=option, y=str(position_y) + "%", fill_color="#ffffff")
        option_text.animations.append(text_start_anim)
        option_text.animations.append(text_end_anim)

        if index_opcion == functions_videos.encontrar_indice(quiz_data_dict["questions"][index_pregunta]["options"],quiz_data_dict["questions"][index_pregunta]["correct_answer"]):
            option_text.stroke_color = stroke_color
        else:
            option_text.stroke_color = "#000000"
        
        composition.elements.append(option_text)

    for i in range(5):
        countdown_text_number = Element("text", track=12, text=str(5 - i), x="54.90%", y="9.5%", z_index=1, time=i + 1.2, duration="1 s", fill_color="#111111", font_size="12 vmin", font_weight="400")
        composition.elements.append(countdown_text_number)

    source.elements.append(composition)

output = json.loads(video.toJSON())
print(output)
response = requests.post(
 'https://api.creatomate.com/v1/renders',
 headers={
  'Authorization': 'Bearer '+str(AUTORIZACION),
  'Content-Type': 'application/json',
 },
 json=output
)

if response.status_code >= 200 & response.status_code<300:  # Código 200 indica éxito
    print("La solicitud fue exitosa.")
    print("Respuesta:", response.json())  # Imprimir la respuesta JSON
else:
    print("La solicitud falló con el código de estado:", response.status_code)
    print("Mensaje de error:", response.text)  # Imprimir el mensaje de error si hay uno

audio.eliminar_archivos_en_ruta(os.getcwd()+'/audio')

#for index_pregunta, question in enumerate(quiz_data_dict["questions"]):
#    audio.eliminar_archivo_de_drive(audioDrive[index_pregunta])


print("todo ok")
