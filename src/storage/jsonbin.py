from typing import List, Dict, Any
from src.storage.base import StorageClient
from src.clients.async_http_client_manager import AsyncHttpClientManager
from src.core.logger import get_logger

logger = get_logger(__name__)

class JsonBinStorageClient(StorageClient):
    """Хранилище данных через JSONBin.io внешний сервис"""

    def __init__(self, base_url: str, headers: Dict[str, str]):
        self.base_url = base_url.rstrip('/')
        self.headers = headers
        logger.info(f"JsonBinStorageClient initialized with URL: {base_url}")

    async def get_data(self) -> List[Dict[str, Any]]:
        """Загружает данные из JSONBin.io"""
        logger.info("Loading data from JSONBin")

        try:
            session = await AsyncHttpClientManager.get_session()

            async with session.get(self.base_url, headers=self.headers) as resp:
                resp.raise_for_status()
                data = await resp.json()

                records = data.get("record", [])
                logger.info(f"Loaded {len(records)} records from JSONBin")
                return records

        except Exception as e:
            logger.error(f"Error loading data from JSONBin: {e}")
            return []

    async def save_data(self, data: List[Dict[str, Any]]) -> None:
        """Сохраняет данные в JSONBin.io"""
        logger.info(f"Saving {len(data)} records to JSONBin")

        try:
            session = await AsyncHttpClientManager.get_session()

            payload = {"record": data}
            async with session.put(self.base_url, headers=self.headers, json=payload) as resp:
                resp.raise_for_status()

            logger.info(f"Successfully saved {len(data)} records to JSONBin")

        except Exception as e:
            logger.error(f"Error saving data to JSONBin: {e}")
            raise