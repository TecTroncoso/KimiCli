import json
import random
import httpx
from .config import Config
from .display import print_status, print_response_start, stream_live

class KimiClient:
    def __init__(self):
        self.config = Config()
        self.cookies = self._load_cookies()
        self.token = self._load_token()
        self.device_id = str(random.randint(10**15, 10**16 - 1))
        self.session_id = None
        self.client = httpx.Client(timeout=60.0)
    
    def _load_cookies(self):
        try:
            with open(self.config.COOKIES_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _load_token(self):
        try:
            with open(self.config.TOKEN_FILE, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None
    
    def _create_session(self):
        if self.session_id:
            return self.session_id
        
        resp = self.client.post(
            f"{self.config.BASE_URL}/api/chat",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "x-msh-device-id": self.device_id,
                "x-msh-platform": "web"
            },
            json={"name": "New Chat"}
        )
        resp.raise_for_status()
        data = resp.json()
        self.session_id = data["id"]
        return self.session_id
    
    def chat(self, prompt):
        if not self.token:
            print_status("No auth token found", "red")
            return
        
        if not self.session_id:
            print_status("Creating chat session...", "cyan")
            session_id = self._create_session()
            if not session_id:
                print_status("Failed to create session", "red")
                return
        else:
            session_id = self.session_id
        
        print_status("Sending message...", "cyan")
        
        payload = {
            "kimiplus_id": "kimi",
            "extend": {"sidebar": True},
            "model": "k2",
            "use_search": False,
            "messages": [{"role": "user", "content": prompt}],
            "refs": [],
            "history": [],
            "scene_labels": [],
            "use_semantic_memory": False,
            "use_deep_research": False
        }
        
        with self.client.stream(
            "POST",
            f"{self.config.BASE_URL}/api/chat/{session_id}/completion/stream",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
                "x-msh-device-id": self.device_id,
                "x-msh-platform": "web",
                "Origin": self.config.BASE_URL,
                "Referer": f"{self.config.BASE_URL}/chat/{session_id}"
            },
            json=payload
        ) as resp:
            if resp.status_code != 200:
                print_status(f"Request failed: {resp.status_code}", "red")
                return
            
            print_response_start()
            
            def content_generator():
                for line in resp.iter_lines():
                    if line.startswith("data:"):
                        json_str = line[5:].strip()
                        if not json_str:
                            continue
                        
                        try:
                            data = json.loads(json_str)
                            if data.get("event") == "cmpl" and data.get("text"):
                                yield data["text"]
                            elif data.get("event") == "all_done":
                                break
                        except json.JSONDecodeError:
                            pass
            
            full_content = stream_live(content_generator())
            return full_content
