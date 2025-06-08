import os
import requests

class SerperDevTool:
    def __init__(self):
        self.api_key = os.getenv("SERPER_API_KEY")
        self.base_url = "https://google.serper.dev/search"

    def search(self, query):
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "num": 3
        }
        response = requests.post(self.base_url, json=payload, headers=headers)
        if response.status_code == 200:
            results = response.json().get("organic", [])
            output = []
            for r in results:
                title = r.get("title", "No title")
                link = r.get("link", "No link")
                output.append(f"{title} - {link}")
            return "\n".join(output)
        else:
            return f"Error: {response.status_code} - {response.text}"
