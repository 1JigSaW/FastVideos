import requests


class MidjourneyAPI:
    BASE_URL = "https://api.midjourney.com"

    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

    def search(self, query):
        response = requests.get(
            f"{self.BASE_URL}/search",
            headers=self.headers,
            params={"query": query}
        )
        return response.json()