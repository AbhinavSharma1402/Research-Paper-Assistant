import os
from typing import Any, Dict, List, Optional

import requests


class APIClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://localhost:8000/api")
        self.session = requests.Session()
        self.token = None

    def set_token(self, token: str):
        self.token = token
        self.session.headers.update({"Authorization": f"Bearer {token}", "Accept": "application/json"})

    def register(self, email: str, password: str) -> Dict[str, Any]:
        response = self.session.post(f"{self.base_url}/auth/register", json={"email": email, "password": password})
        response.raise_for_status()
        data = response.json()
        self.set_token(data["access_token"])
        return data

    def login(self, email: str, password: str) -> Dict[str, Any]:
        response = self.session.post(f"{self.base_url}/auth/login", json={"email": email, "password": password})
        response.raise_for_status()
        data = response.json()
        self.set_token(data["access_token"])
        return data

    def get_me(self) -> Dict[str, Any]:
        response = self.session.get(f"{self.base_url}/users/me")
        response.raise_for_status()
        return response.json()

    def upload_documents(self, files: List[Any]) -> Dict[str, Any]:
        upload_files = []
        for upload in files:
            upload_files.append(("files", (upload.name, upload.getvalue(), upload.type)))
        response = self.session.post(f"{self.base_url}/documents/upload", files=upload_files)
        response.raise_for_status()
        return response.json()

    def list_documents(self) -> Dict[str, Any]:
        response = self.session.get(f"{self.base_url}/documents/")
        response.raise_for_status()
        return response.json()

    def create_chat(self, title: str) -> Dict[str, Any]:
        response = self.session.post(f"{self.base_url}/chats/", json={"title": title})
        response.raise_for_status()
        return response.json()

    def list_chats(self) -> List[Dict[str, Any]]:
        response = self.session.get(f"{self.base_url}/chats/")
        response.raise_for_status()
        return response.json()

    def get_chat_messages(self, chat_id: int) -> List[Dict[str, Any]]:
        response = self.session.get(f"{self.base_url}/chats/{chat_id}/messages")
        response.raise_for_status()
        return response.json()

    def query_chat(self, chat_id: int, question: str) -> Dict[str, Any]:
        response = self.session.post(f"{self.base_url}/chats/{chat_id}/query", json={"question": question})
        response.raise_for_status()
        return response.json()
