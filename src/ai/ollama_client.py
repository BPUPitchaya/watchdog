import requests
import json

class OllamaClient:
    def __init__(self, model='phi4', base_url='http://localhost:11434'):
        self.model = model
        self.base_url = base_url

    def query(self, prompt):
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data['message']['content']
        except requests.RequestException as e:
            return f"Error querying Ollama: {str(e)}"
