import os
import openai
from google_images_search import GoogleImagesSearch
import subprocess
import json
import datetime
from dotenv import load_dotenv
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip
from moviepy.video.VideoClip import ColorClip
from moviepy.video.tools.segmenting import findObjects
from PIL import Image, ImageOps
import numpy as np

load_dotenv()

VAR = 'pens'

GCP_API_KEY = os.getenv('GCP_API_KEY')
GCP_CX_KEY = os.getenv('GCP_CX_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

gis = GoogleImagesSearch(GCP_API_KEY, GCP_CX_KEY)

openai.api_key = OPENAI_API_KEY


def get_first_image_from_folder(folder_name):
    for file in sorted(os.listdir(folder_name)):
        if file.endswith(".jpg"):
            return os.path.join(folder_name, file)
    return None


def resize_and_center(image_path, width, height):
    img = Image.open(image_path)
    img_w, img_h = img.size

    # Вычислите новые размеры изображения, сохраняя пропорции
    scale_factor = width / img_w
    new_img_w = int(img_w * scale_factor)
    new_img_h = int(img_h * scale_factor)

    # Измените размер изображения
    img = img.resize((new_img_w, new_img_h), Image.Resampling.LANCZOS)

    # Центрируйте изображение на фоне
    bg = Image.new('RGB', (width, height), (0, 0, 0))  # Задаем черный цвет фона
    offset = ((width - new_img_w) // 2, (height - new_img_h) // 2)
    bg.paste(img, offset)

    return bg

# def run_js_script(script_path, argument1, argument2):
#     try:
#         output = subprocess.check_output(["node", script_path, argument1, argument2], stderr=subprocess.STDOUT)
#         print(f"Output from JS script: {output.decode('utf-8')}")
#     except subprocess.CalledProcessError as e:
#         print(f"Error occurred: {e.output.decode('utf-8')}")
#
#
# def clean_name(name):
#     invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
#     for char in invalid_chars:
#         name = name.replace(char, '')
#     return name
#
#
# def search(query):
#     _search_params = {
#         'q': query,
#         'num': 3,
#         'fileType': 'jpg|png',
#         'imgSize': 'imgSizeUndefined',
#     }
#
#     if not os.path.exists('downloads'):
#         os.makedirs('downloads')
#
#     current_datetime = datetime.datetime.now()
#     formatted_datetime = current_datetime.strftime('%Y-%m-%d_%H-%M-%S')
#
#     directory_name = os.path.join('downloads', f"{VAR}_{formatted_datetime}")
#     if not os.path.exists(directory_name):
#         os.makedirs(directory_name)
#
#     gis.search(search_params=_search_params)
#     for image in gis.results():
#         image.download(directory_name)
#
#
# def make_request():
#     response = openai.ChatCompletion.create(
#         model="gpt-4",
#         messages=[
#             {"role": "system", "content": "You are ChatGPT, a large language model."},
#             {"role": "user", "content": f""" Write the 5 most expensive {VAR} in the world as json where the key is the
#             name and the value is the price and sign of currency and sort from the cheapest in the list to the most expensive
#             For example: {{
#                 "La Modernista Diamonds by Caran d’Ache": "$265,000",
#                 "Mystery Masterpiece by Mont Blanc and Van Cleef & Arpels": "$730,000",
#                 "Heaven Gold Pen by Anita Tan": "$995,000",
#                 "Boheme Royal by Mont Blanc": "$1,500,000",
#                 "Fulgor Nocturnus by Tibaldi": "$8,000,000"
#             }}
#             """},
#         ]
#     )
#     return response
#
#
# output = None
# for i in range(3):
#     try:
#         response = make_request()
#         output = json.loads(response['choices'][0]['message']['content'])
#         print(output)
#         break
#     except json.JSONDecodeError:
#         print("JSON Decode Error, retrying...")
# else:
#     print("Failed to get a valid response after 3 attempts.")
#
# list_items = output
#
# # list_items = {
# #     "La Modernista Diamonds by Caran d’Ache": "$265,000",
# #     "Mystery Masterpiece by Mont Blanc and Van Cleef & Arpels": "$730,000",
# #     "Heaven Gold Pen by Anita Tan": "$995,000",
# #     "Boheme Royal by Mont Blanc": "$1,500,000",
# #     "Fulgor Nocturnus by Tibaldi": "$8,000,000"
# # }
#
# mj_query = f'Create a beautiful background for a video titled: Write the 5 most expensive {VAR} in the world'
# run_js_script("mj.js", mj_query, VAR)
#
# for name, price in list_items.items():
#     search(name)


import os

background_folder = "background"
downloads_folder = "downloads"

# Фильтруйте изображения в папке background по ключевому слову
background_folders = [folder for folder in os.listdir(background_folder) if folder.startswith(VAR)]

# Если найдена хотя бы одна папка, используйте первое изображение в ней
if background_folders:
    images = os.listdir(os.path.join(background_folder, background_folders[0]))
    if images:
        background_image_path = os.path.join(background_folder, background_folders[0], images[0])
        print("Фоновое изображение:", background_image_path)
    else:
        print(f"В папке {background_folders[0]} нет изображений.")
else:
    print(f"Не найдено папок с ключевым словом '{VAR}' в папке background.")

# Получите список всех папок в папке downloads
folders = [folder for folder in os.listdir(downloads_folder) if folder.startswith(VAR)]

# Выберите первое изображение из каждой папки с ключом "pens"
image_paths = []
for folder in folders:
    images = os.listdir(os.path.join(downloads_folder, folder))
    if images:
        image_path = os.path.join(downloads_folder, folder, images[0])
        image_paths.append(image_path)

print("Пути к первым изображениям в каждой папке:", image_paths[0])


resolution = (1080, 1920)

# Вступление
intro_text1 = TextClip("Топ 5", fontsize=60, color='black').set_duration(3).fadein(1).fadeout(1)
intro_text2 = TextClip("самых дорогих ручек в мире", fontsize=60, color='black').set_duration(3).fadein(1).fadeout(1)

intro_text_size1 = intro_text1.size
intro_text_size2 = intro_text2.size

intro_text_bg = ColorClip(size=(resolution[0], intro_text_size1[1] + intro_text_size2[1] + 50), color=[255, 255, 255]).set_opacity(0.8).set_position(('center', 'center')).set_duration(3)
intro_image = ImageClip(np.array(resize_and_center(background_image_path, *resolution)), ismask=False).set_duration(3)

intro = CompositeVideoClip([intro_image, intro_text_bg, intro_text1.set_position(('center', (resolution[1] - intro_text_size1[1] - intro_text_size2[1]) // 2)), intro_text2.set_position(('center', (resolution[1] + intro_text_size1[1] - intro_text_size2[1]) // 2))])

# Загрузите изображения и установите продолжительность
clips = [ImageClip(np.array(resize_and_center(image_path, *resolution)), ismask=False).set_duration(3).fadein(1).fadeout(1) for image_path in image_paths]

# Создайте текстовые надписи и цены
texts = [TextClip(f"{5 - i} место: Ручка {5 - i}\n\n${1000 * (5 - i)}", fontsize=50, color='black').set_pos('center').set_duration(3) for i in range(5)]
text_bgs = [ColorClip(size=(resolution[0], 200), color=[255, 255, 255]).set_opacity(0.8).set_position(('center', 'center')).set_duration(3) for i in range(5)]

# Объедините изображения и текст
videos = [CompositeVideoClip([clips[i], text_bgs[i], texts[i]]) for i in range(5)]

# Объедините вступление и видео с ручками
final_video = concatenate_videoclips([intro] + videos)

# Загрузите аудио
audio = AudioFileClip("654728__sergequadrado__comfort.wav")

# Обрежьте аудио, чтобы оно соответствовало общей продолжительности видео
audio = audio.subclip(0, final_video.duration)

# Установите аудио для видео
final_video = final_video.set_audio(audio)

# Экспортируйте видео
final_video.write_videofile("final_video.mp4", fps=24)