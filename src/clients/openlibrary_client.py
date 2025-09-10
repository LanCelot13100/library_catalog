from src.core.base_api_client import BaseApiClient


class OpenLibraryClient(BaseApiClient):
    def __init__(self):
        super().__init__("https://openlibrary.org")

    def get(self, endpoint: str, params: dict = None):
        return self._request("GET", endpoint, params=params)

    def post(self, *args, **kwargs):
        raise NotImplementedError("OpenLibrary не поддерживает POST")

    def put(self, *args, **kwargs):
        raise NotImplementedError("OpenLibrary не поддерживает PUT")

    def search_book(self, title: str, author: str = None):
        params = {"title": title}
        if author:
            params["author"] = author
        data = self.get("/search.json", params=params)
        if not data.get("docs"):
            return None
        doc = data["docs"][0]
        return {
            "openlibrary_id": doc.get("key"),
            "title": doc.get("title"),
            "author": doc.get("author_name", [None])[0],
            "year": doc.get("first_publish_year"),
            "cover_url": f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-L.jpg"
            if doc.get("cover_i") else None,
        }

    def get_book_details(self, work_id: str):
        data = self.get(f"{work_id}.json")
        return {
            "description": (
                data.get("description", {}).get("value")
                if isinstance(data.get("description"), dict)
                else data.get("description")
            ),
            "subjects": data.get("subjects", []),
        }
