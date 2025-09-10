import os
from dotenv import load_dotenv
from src.core.base_api_client import BaseApiClient

load_dotenv()

API_KEY = os.getenv("JSONBIN_API_KEY")
BIN_ID = os.getenv("JSONBIN_BIN_ID")

class JsonBinClient(BaseApiClient):
    def __init__(self):
        headers = {
            "X-Master-Key": API_KEY,
            "Content-Type": "application/json"
        }
        base_url = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
        super().__init__(base_url, headers)

    def get(self):
        return self._request("GET", "")

    def put(self, payload: dict):
        return self._request("PUT", "", json=payload)

    def post(self, *args, **kwargs):
        raise NotImplementedError("JsonBin не поддерживает POST")
