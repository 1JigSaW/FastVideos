import os
import pickle
from tkinter import Tk, Label, Button, Listbox, Canvas, Scrollbar, Frame, filedialog
from urllib.request import urlopen

from bs4 import BeautifulSoup
from get_chrome_driver import GetChromeDriver
import time
import random
import requests
from instagram_private_api_extensions import media
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager as CM
from chromedriver_py import binary_path

import openai
from google_images_search import GoogleImagesSearch
import subprocess
import json
import datetime
from dotenv import load_dotenv
from moviepy.editor import *
from moviepy.video.VideoClip import ColorClip
from PIL import Image, ImageOps, ImageTk
import numpy as np
from textwrap import wrap
import shutil

from tiktok_uploader.upload import upload_videos
from tiktok_uploader.auth import AuthBackend


def wrap_text(text, max_width):
    return '\n'.join(wrap(text, max_width))


load_dotenv()

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

    scale_factor = width / img_w
    new_img_w = int(img_w * scale_factor)
    new_img_h = int(img_h * scale_factor)

    img = img.resize((new_img_w, new_img_h), Image.Resampling.LANCZOS)

    bg = Image.new('RGB', (width, height), (0, 0, 0))  # Задаем черный цвет фона
    offset = ((width - new_img_w) // 2, (height - new_img_h) // 2)
    bg.paste(img, offset)

    return bg


def run_js_script(script_path, argument1, argument2):
    try:
        output = subprocess.check_output(["node", script_path, argument1, argument2], stderr=subprocess.STDOUT)
        print(f"Output from JS script: {output.decode('utf-8')}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.output.decode('utf-8')}")


def clean_name(name):
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        name = name.replace(char, '')
    return name


def delete_video_folders(directories):
    for directory in directories:
        if os.path.exists(directory):
            for folder_name in os.listdir(directory):
                folder_path = os.path.join(directory, folder_name)

                if not folder_name.startswith(f'{VAR}_'):
                    if os.path.isdir(folder_path):
                        shutil.rmtree(folder_path)


def search(query):
    delete_video_folders(['downloads', 'background'])

    _search_params = {
        'q': query,
        'num': 5,
        'fileType': 'jpg|png',
        'imgSize': 'imgSizeUndefined',
    }

    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime('%Y-%m-%d_%H-%M-%S')

    directory_name = os.path.join('downloads', f"{VAR}_{formatted_datetime}")
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

    gis.search(search_params=_search_params)
    for image in gis.results():
        image.download(directory_name)
    return get_first_image_from_folder(directory_name)


def make_request():
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are ChatGPT, a large language model."},
            {"role": "user", "content": f""" Write the 5 most expensive {VAR} in the world as json where the key is the
            name and the value is the price and sign of currency and sort from the cheapest in the list to the most expensive
            For example: {{
                "La Modernista Diamonds by Caran d’Ache": "$265,000",
                "Mystery Masterpiece by Mont Blanc and Van Cleef & Arpels": "$730,000",
                "Heaven Gold Pen by Anita Tan": "$995,000",
                "Boheme Royal by Mont Blanc": "$1,500,000",
                "Fulgor Nocturnus by Tibaldi": "$8,000,000"
            }}
            """},
        ]
    )
    return response


def make_request_hashtag():
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are ChatGPT, a large language model."},
            {"role": "user", "content": f""" Generate 10 popular video hashtags titled "Top 5 most expensive {VAR} in 
            the world" and output them as json like this {{
                "1": "#money",
                "2": "#people",
                "3": "#computers",
                "4": "#smile",
                "5": "#health"
            }}
            """},
        ]
    )
    return response


def get_data_and_download_images():
    output = None
    for i in range(3):
        try:
            response = make_request()
            output = json.loads(response['choices'][0]['message']['content'])
            print(output)
            break
        except json.JSONDecodeError:
            print("JSON Decode Error, retrying...")
    else:
        print("Failed to get a valid response after 3 attempts.")

    output_hashtag = None
    for i in range(3):
        try:
            response = make_request_hashtag()
            output_hashtag = json.loads(response['choices'][0]['message']['content'])
            print(output)
            break
        except json.JSONDecodeError:
            print("JSON Decode Error, retrying...")
    else:
        print("Failed to get a valid response after 3 attempts.")

    list_items = output
    hashtags = output_hashtag

    hashtags_list = [hashtags[key] for key in hashtags]

    hashtags_str = ', '.join(hashtags_list)

    hashtags_str = f"TOP 5 MOST EXPENSIVE {VAR.upper()} IN THE WORLD " + hashtags_str

    with open('hashtags.txt', 'w') as f:
        f.write(hashtags_str)

    def price_to_int(price_str):
        price_str = price_str.replace("$", "").split(".")[0]
        return int(price_str.replace(",", ""))

    list_items = dict(sorted(list_items.items(), key=lambda item: price_to_int(item[1])))

    mj_query = f'Create a beautiful background for a video titled: Write the 5 most expensive {VAR} in the world'
    run_js_script("mj.js", mj_query, VAR)

    data_list = []

    for name, price in list_items.items():
        image_path = search(name)
        data_list.append({
            'name': name,
            'price': price,
            'image_path': image_path
        })

    return data_list


def prepare_video(data_list):
    background_folder = "background"
    downloads_folder = "downloads"

    background_folders = [folder for folder in os.listdir(background_folder) if folder.startswith(VAR)]

    if background_folders:
        images = os.listdir(os.path.join(background_folder, background_folders[0]))
        if images:
            background_image_path = os.path.join(background_folder, background_folders[0], images[0])
            print("Фоновое изображение:", background_image_path)
        else:
            print(f"В папке {background_folders[0]} нет изображений.")
    else:
        print(f"Не найдено папок с ключевым словом '{VAR}' в папке background.")

    folders = [folder for folder in os.listdir(downloads_folder) if folder.startswith(VAR)]

    image_paths = []
    for folder in folders:
        images = os.listdir(os.path.join(downloads_folder, folder))
        if images:
            image_path = os.path.join(downloads_folder, folder, images[0])
            image_paths.append(image_path)

    print("Пути к первым изображениям в каждой папке:", image_paths[0])

    resolution = (1080, 1920)

    intro_text1 = TextClip("Top 5 most expensive", fontsize=60, color='white', font='Ubuntu-Mono-Bold').set_duration(
        3).fadeout(0.5)
    intro_text2 = TextClip(f"{VAR} in the world", fontsize=60, color='white', font='Ubuntu-Mono-Bold').set_duration(
        3).fadeout(0.5)

    intro_text_size1 = intro_text1.size
    intro_text_size2 = intro_text2.size

    intro_text_bg = ColorClip(size=(resolution[0], intro_text_size1[1] + intro_text_size2[1] + 50),
                              color=[0, 0, 0]).set_opacity(0.5).set_position(('center', 'center')).set_duration(3)
    intro_image = (ImageClip(np.array(resize_and_center(background_image_path, *resolution)), ismask=False)
                   .set_duration(3)
                   .fadeout(0.5))

    intro = CompositeVideoClip([intro_image, intro_text_bg, intro_text1.set_position(
        ('center', (resolution[1] - intro_text_size1[1] - intro_text_size2[1]) // 2)), intro_text2.set_position(
        ('center', (resolution[1] + intro_text_size1[1] - intro_text_size2[1]) // 2))])
    print(data_list)

    def get_first_image_from_directory(directory):
        image_files = [f for f in os.listdir(directory) if
                       os.path.isfile(os.path.join(directory, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if image_files:
            return os.path.join(directory, image_files[0])
        return None

    def get_image_or_existing(image_path, resolution):
        if not os.path.exists(image_path):
            image_path = get_first_image_from_directory(os.path.dirname(image_path))
        return ImageClip(np.array(resize_and_center(image_path, *resolution)), ismask=False)

    clips = [
        get_image_or_existing(item['image_path'], resolution).set_duration(3).fadein(0.5).fadeout(0.5)
        for item in data_list
    ]

    max_width = 25
    texts = []
    for i, item in enumerate(data_list):
        name = item['name']
        text_content = wrap_text(f'{5 - i} place: {name}', max_width) + "\n\n"
        text_clip = TextClip(text_content, fontsize=50, color='white', font='Ubuntu-Mono-Bold').set_pos(
            'center').set_duration(3)
        texts.append(text_clip)

    texts2 = [TextClip(f"{item['price']}", fontsize=70, color='yellow', font='Ubuntu-Mono-Bold').set_position(
        ('center', resolution[1] / 2 + 50)).set_duration(3) for item in data_list]
    text_bgs = [ColorClip(size=(resolution[0], 270), color=[0, 0, 0]).set_opacity(0.6).set_position(
        ('center', 'center')).set_duration(3) for i in range(5)]

    videos = [CompositeVideoClip([clips[i], text_bgs[i], texts[i], texts2[i]]) for i in range(5)]

    final_video = concatenate_videoclips([intro] + videos)

    audio = AudioFileClip("music.mp3")

    audio = audio.subclip(0, final_video.duration)

    final_video = final_video.set_audio(audio)

    final_video.write_videofile(f"final_video_{VAR}.mp4", fps=60, bitrate="5000k")


def select_image(folder):
    root = Tk()
    root.title('Выберите изображение')

    images = [file for file in os.listdir(folder) if file.lower().endswith(('png', 'jpg', 'jpeg'))]
    img_objects = []
    img_labels = []

    def confirm_selection(img_name):
        for img in images:
            if img != img_name:
                os.remove(os.path.join(folder, img))
        root.destroy()

    def load_from_computer():
        file_path = filedialog.askopenfilename(filetypes=[('Image files', '.png .jpg .jpeg')])
        if file_path:
            # Копируем файл в целевую папку
            shutil.copy(file_path, folder)
            new_file_name = os.path.basename(file_path)

            # Удаляем все другие файлы
            for img in images:
                os.remove(os.path.join(folder, img))

            root.destroy()

    def show_images():
        for i, img in enumerate(images):
            image_path = os.path.join(folder, img)
            img_obj = Image.open(image_path)

            # Уменьшение размера с сохранением пропорций
            base_width, base_height = img_obj.size
            new_width = int(base_width * 0.3)
            new_height = int(base_height * 0.3)
            img_obj = img_obj.resize((new_width, new_height), Image.Resampling.LANCZOS)

            img_tk = ImageTk.PhotoImage(img_obj)

            panel = Label(root, image=img_tk)
            panel.image = img_tk
            panel.grid(column=i, row=0)
            panel.bind("<Button-1>", lambda e, img=img: confirm_selection(img))

            img_objects.append(img_obj)
            img_labels.append(panel)

    show_images()

    load_button = Button(root, text="Загрузить изображение", command=load_from_computer)
    load_button.grid(column=0, row=1)

    root.mainloop()


def downloadVideo(link, id):
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    driver = webdriver.Chrome(options=options)
    # Change the tiktok link
    driver.get("https://www.tiktok.com/@papayaho.cat")
    print(f"Downloading video {id} from: {link}")
    cookies = {
        # Please get this data from the console network activity tool
        # This is explained in the video :)
    }

    headers = {
        # Please get this data from the console network activity tool
        # This is explained in the video :)
    }

    params = {
        'url': 'dl',
    }

    data = {
        'id': link,
        'locale': 'en',
        'tt': '',

    }

    print("STEP 4: Getting the download link")
    print("If this step fails, PLEASE read the steps above")
    response = requests.post('https://ssstik.io/abc', params=params, cookies=cookies, headers=headers, data=data)
    downloadSoup = BeautifulSoup(response.text, "html.parser")

    downloadLink = downloadSoup.a["href"]
    videoTitle = downloadSoup.p.getText().strip()

    print("STEP 5: Saving the video :)")
    mp4File = urlopen(downloadLink)
    # Feel free to change the download directory
    with open(f"videos/{id}-{videoTitle}.mp4", "wb") as output:
        while True:
            data = mp4File.read(4096)
            if data:
                output.write(data)
            else:
                break


def upload_tiktok(title, description):
    videos = [
        {
            'video': title,
            'description': description
        },
    ]

    auth = AuthBackend(cookies='cookies.txt')
    failed_videos = upload_videos(videos=videos, auth=auth)


VAR = 'dog breeds'

# data_list = get_data_and_download_images()
# with open('data_list.json', 'w') as file:
#     json.dump(data_list, file)
#
# directories = ["background", "downloads"]
#
# for directory in directories:
#     for subfolder in os.listdir(directory):
#         full_path = os.path.join(directory, subfolder)
#         if os.path.isdir(full_path):
#             select_image(full_path)
#
# with open('data_list.json', 'r') as file:
#     data_list = json.load(file)
# prepare_video(data_list)
#
# with open("hashtags.txt", "r") as file:
#     content = file.read()
#     print(content)


# upload_tiktok(f'final_video_{VAR}.mp4', content)


