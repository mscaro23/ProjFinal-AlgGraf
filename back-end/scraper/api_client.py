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
        
        if "missing" in page:
            raise ValueError(f"Página '{title}' não encontrada")
            
        print(
            f"[APIClient] Resolved to: page_id={page['pageid']}, title={page['title']}"
        )
        return page["pageid"], page["title"]

    def fetch_metadata(self, page_id=None, title=None):
        print(f"[APIClient] Fetching metadata for page_id={page_id} or title={title}")
        params = {
            "action": "query",
            "prop": "info|contributors|revisions",
            "inprop": "url",
            "rvprop": "ids",
        }
        if page_id:
            params["pageids"] = page_id
        elif title:
            params["titles"] = title
            params["redirects"] = 1
        else:
            raise ValueError("Must provide page_id or title")
            
        return self.call_api(params)

    def resolve_titles_batch(self, titles: list[str]):
        results = {}
        # Remove duplicates to save bandwidth
        unique_titles = list(set(titles))
        chunk_size = 50
        
        for i in range(0, len(unique_titles), chunk_size):
            chunk = unique_titles[i:i+chunk_size]
            titles_str = "|".join(chunk)
            print(f"[APIClient] Resolving batch of {len(chunk)} titles...")
            
            try:
                data = self.call_api({"action": "query", "titles": titles_str, "redirects": 1})
                query = data.get("query", {})
                
                # 1. Initialize mapping: input -> current_target
                # We need to track how input titles map to the final titles
                # Start with identity mapping for this chunk
                # We need to handle the fact that 'titles' param might be normalized by API immediately
                
                # A simpler way:
                # The API returns 'normalized', 'redirects', and 'pages'.
                # We can trace the path for each input title in 'chunk'.
                
                # Create a map of current_name -> original_names (list)
                # Because multiple inputs might map to same normalized/redirected name
                name_tracker = {name: [name] for name in chunk}
                
                # Apply normalizations
                if "normalized" in query:
                    for n in query["normalized"]:
                        original = n["from"]
                        target = n["to"]
                        if original in name_tracker:
                            names = name_tracker.pop(original)
                            if target in name_tracker:
                                name_tracker[target].extend(names)
                            else:
                                name_tracker[target] = names
                
                # Apply redirects
                if "redirects" in query:
                    for r in query["redirects"]:
                        original = r["from"]
                        target = r["to"]
                        # Redirects apply to the normalized names
                        if original in name_tracker:
                            names = name_tracker.pop(original)
                            if target in name_tracker:
                                name_tracker[target].extend(names)
                            else:
                                name_tracker[target] = names
                                
                # Now name_tracker maps Final Title -> List of Original Input Titles
                
                # Process pages
                pages = query.get("pages", {})
                for page in pages.values():
                    if "missing" in page:
                        continue
                    
                    page_id = page["pageid"]
                    final_title = page["title"]
                    
                    # Find which inputs map to this final title
                    if final_title in name_tracker:
                        original_inputs = name_tracker[final_title]
                        for inp in original_inputs:
                            results[inp] = (page_id, final_title)
                            
            except Exception as e:
                print(f"Error resolving batch: {e}")
                
        return results

    def fetch_html(self, page_id):
        print(f"[APIClient] Fetching HTML for page_id={page_id}")
        data = self.call_api({"action": "parse", "pageid": page_id, "prop": "text"})
        print(f"[APIClient] HTML received ({len(data['parse']['text']['*'])} chars).")
        return data["parse"]["text"]["*"]
