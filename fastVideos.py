import os
from google_images_search import GoogleImagesSearch

# Замените YOUR_GCP_API_KEY и YOUR_GCS_CX на ваш действительный API-ключ Google Cloud и значение Google Custom Search CX.
gis = GoogleImagesSearch('AIzaSyAEuu9mWdYZxrqnxTwVUh-vgI9u175lvro', 'a685d0b2eb4ac47ff')

def clean_name(name):
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        name = name.replace(char, '')
    return name

def search(query):
    # Определите параметры поиска
    _search_params = {
        'q': query,
        'num': 1,
        'fileType': 'jpg|png',
        'safe': 'active',
        'imgSize': 'xlarge',
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

list_items = {
    "La Modernista Diamonds by Caran d’Ache": "$265,000",
    "Mystery Masterpiece by Mont Blanc and Van Cleef & Arpels": "$730,000",
    "Heaven Gold Pen by Anita Tan": "$995,000",
    "Boheme Royal by Mont Blanc": "$1,500,000",
    "Fulgor Nocturnus by Tibaldi": "$8,000,000"
}

for name, price in list_items.items():
    search(name)


