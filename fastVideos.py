import os
import openai
from google_images_search import GoogleImagesSearch
import json

from MidjourneyAPI import MidjourneyAPI

VAR = 'pens'

gis = GoogleImagesSearch('AIzaSyAEuu9mWdYZxrqnxTwVUh-vgI9u175lvro', 'a685d0b2eb4ac47ff')

openai.api_key = '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'

api = MidjourneyAPI("YOUR_API_KEY_HERE")

def clean_name(name):
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        name = name.replace(char, '')
    return name


def search(query):
    # Определите параметры поиска
    _search_params = {
        'q': query,
        'num': 3,
        'fileType': 'jpg|png',
        'imgSize': 'imgSizeUndefined',
    }

    # Создайте основную папку "downloads", если она не существует
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    # Создайте папку для изображения внутри "downloads"
    directory_name = os.path.join('downloads', clean_name(query))
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

    # Поиск и загрузка изображения
    gis.search(search_params=_search_params)
    for image in gis.results():
        image.download(directory_name)


# response = openai.ChatCompletion.create(
#     model="gpt-4",
#     messages=[
#         {"role": "system", "content": "You are ChatGPT, a large language model."},
#         {"role": "user", "content": f""" Write the 5 most expensive {VAR} in the world as json where the key is the
#         name and the value is the price and sign of currency and sort from the cheapest in the list to the most expensive
#         For example: {{
#             "La Modernista Diamonds by Caran d’Ache": "$265,000",
#             "Mystery Masterpiece by Mont Blanc and Van Cleef & Arpels": "$730,000",
#             "Heaven Gold Pen by Anita Tan": "$995,000",
#             "Boheme Royal by Mont Blanc": "$1,500,000",
#             "Fulgor Nocturnus by Tibaldi": "$8,000,000"
#         }}
#         """},
#     ]
# )
# output = json.loads(response['choices'][0]['message']['content'])
# print(output)

# list_items = {
#     "La Modernista Diamonds by Caran d’Ache": "$265,000",
#     "Mystery Masterpiece by Mont Blanc and Van Cleef & Arpels": "$730,000",
#     "Heaven Gold Pen by Anita Tan": "$995,000",
#     "Boheme Royal by Mont Blanc": "$1,500,000",
#     "Fulgor Nocturnus by Tibaldi": "$8,000,000"
# }
#
# for name, price in list_items.items():
#     search(name)


