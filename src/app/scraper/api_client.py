import requests
from app.config.settings import WIKI_API, USER_AGENT


class APIClient:

    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        print("[APIClient] Session initialized.")

    def call_api(self, params: dict):
        print(f"[APIClient] Calling API with params: {params}")
        params["format"] = "json"
        r = self.session.get(WIKI_API, params=params)
        print(f"[APIClient] HTTP {r.status_code}")
        r.raise_for_status()
        return r.json()

    def resolve_title(self, title):
        print(f"[APIClient] Resolving title: {title}")
        data = self.call_api({"action": "query", "titles": title, "redirects": 1})
        page = next(iter(data["query"]["pages"].values()))
        print(
            f"[APIClient] Resolved to: page_id={page['pageid']}, title={page['title']}"
        )
        if "missing" in page:
            raise ValueError(f"Página '{title}' não encontrada")
        return page["pageid"], page["title"]

    def fetch_metadata(self, page_id):
        print(f"[APIClient] Fetching metadata for page_id={page_id}")
        return self.call_api(
            {
                "action": "query",
                "pageids": page_id,
                "prop": "info|contributors|revisions",
                "inprop": "url",
                "rvprop": "ids",
            }
        )

    def fetch_html(self, page_id):
        print(f"[APIClient] Fetching HTML for page_id={page_id}")
        data = self.call_api({"action": "parse", "pageid": page_id, "prop": "text"})
        print(f"[APIClient] HTML received ({len(data['parse']['text']['*'])} chars).")
        return data["parse"]["text"]["*"]
