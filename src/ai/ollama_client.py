import json
import time

import requests


class OllamaClient:
    def __init__(
        self,
        model: str = "llama3.2:1b",
        base_url: str = "http://localhost:11434",
        keep_alive: int = 30,
        context_window: int = 1024,
        explanation_detail: int = 3,
    ) -> None:
        self.model = model
        self.base_url = base_url
        self.keep_alive = keep_alive  # minutes
        self.context_window = context_window  # tokens
        self.explanation_detail = explanation_detail  # 1-5 scale
        self._last_query_time = None
        self._keepalive_timer = None

    def query(self, prompt: str) -> str:
        """Non-streaming query - returns full response."""
        self._update_last_query()
        url = f"{self.base_url}/api/chat"

        # Add detail instruction to prompt
        detail_instruction = self._get_detail_instruction()
        enhanced_prompt = f"{detail_instruction}\n\n{prompt}"

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": enhanced_prompt}],
            "stream": False,
            "options": {"num_ctx": self.context_window, "keep_alive": f"{self.keep_alive}m"},
        }
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
        except requests.RequestException as e:
            return f"Error querying Ollama: {str(e)}"

    def query_stream(self, prompt: str, callback) -> str:
        """Streaming query - calls callback with each chunk as it arrives."""
        self._update_last_query()
        url = f"{self.base_url}/api/chat"

        # Add detail instruction to prompt
        detail_instruction = self._get_detail_instruction()
        enhanced_prompt = f"{detail_instruction}\n\n{prompt}"

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": enhanced_prompt}],
            "stream": True,
            "options": {"num_ctx": self.context_window, "keep_alive": f"{self.keep_alive}m"},
        }
        full_response = ""
        try:
            response = requests.post(url, json=payload, stream=True, timeout=120)
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode("utf-8"))
                        if "message" in data and "content" in data["message"]:
                            chunk = data["message"]["content"]
                            full_response += chunk
                            callback(chunk, full_response)
                        if data.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue
            return full_response
        except requests.RequestException as e:
            error_msg = f"Error querying Ollama: {str(e)}"
            callback(error_msg, error_msg)
            return error_msg

    def _update_last_query(self) -> None:
        """Update the last query time and manage keep-alive timer."""
        self._last_query_time = time.time()
        # Cancel existing timer if any
        if self._keepalive_timer:
            self._keepalive_timer.cancel()

    def set_keep_alive(self, minutes: int) -> None:
        """Update the keep-alive timer duration."""
        self.keep_alive = minutes
        print(f"Keep-alive timer updated to {minutes} minutes")

    def set_context_window(self, tokens: int) -> None:
        """Update the context window size."""
        self.context_window = tokens
        print(f"Context window updated to {tokens} tokens")

    def set_model(self, model: str) -> None:
        """Update the AI model."""
        self.model = model
        print(f"AI model updated to {model}")

    def set_explanation_detail(self, detail: int) -> None:
        """Update the explanation detail level (1-5)."""
        self.explanation_detail = detail
        print(f"Explanation detail updated to {detail}")

    def _get_detail_instruction(self) -> str:
        """Get instruction string based on detail level."""
        instructions = {
            1: "Provide a brief, one-sentence explanation.",
            2: "Provide a concise explanation in 2-3 sentences.",
            3: "Provide a standard explanation with key details.",
            4: "Provide a detailed explanation with examples.",
            5: "Provide a comprehensive explanation with all relevant details.",
        }
        return instructions.get(self.explanation_detail, instructions[3])
