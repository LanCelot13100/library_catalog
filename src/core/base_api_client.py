import logging
import requests
from abc import ABC, abstractmethod
from src.core.exceptions import ApiClientError


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)


class BaseApiClient(ABC): # Абстрактный базовый клиент для HTTP-запросов

    def __init__(self, base_url: str, headers: dict = None):
        self.base_url = base_url
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)

    def _request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}{endpoint}"
        logger.info(f"{method} {url} | params={kwargs.get('params')} json={kwargs.get('json')}")
        try:
            resp = self.session.request(method, url, **kwargs)
            resp.raise_for_status()
            logger.info(f"Response {resp.status_code}: {resp.text[:200]}...")
            return resp.json()
        except requests.RequestException as e:
            logger.error(f"HTTP error: {e}")
            raise ApiClientError(str(e))

    @abstractmethod
    def get(self, *args, **kwargs):
        pass

    @abstractmethod
    def post(self, *args, **kwargs):
        pass

    @abstractmethod
    def put(self, *args, **kwargs):
        pass
