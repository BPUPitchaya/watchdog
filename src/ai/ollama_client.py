import requests
import json

class OllamaClient: 
    def __init__(self, model='llama3.2:3b', base_url='http://localhost:11434'):
        self.model = model
        self.base_url = base_url

    def query(self, prompt):
        """Non-streaming query - returns full response."""
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
    
    def query_stream(self, prompt, callback):
        """Streaming query - calls callback with each chunk as it arrives."""
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True
        }
        full_response = ""
        try:
            response = requests.post(url, json=payload, stream=True, timeout=120)
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if 'message' in data and 'content' in data['message']:
                            chunk = data['message']['content']
                            full_response += chunk
                            callback(chunk, full_response)
                        if data.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue
            return full_response
        except requests.RequestException as e:
            error_msg = f"Error querying Ollama: {str(e)}"
            callback(error_msg, error_msg)
            return error_msg
