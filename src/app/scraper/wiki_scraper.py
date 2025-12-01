from app.scraper.api_client import APIClient
from app.scraper.html_parser import HTMLParser
from app.models.graph_objects import PageNode, LinkNode


class WikiScraper:

    def __init__(self, api_client=None):
        self.api = api_client or APIClient()
        self.parser = HTMLParser()
        print("[WikiScraper] Initialized.")

    def scrape_page(self, title: str):
        print(f"[WikiScraper] Scraping page: '{title}'")

    def scrape_page(self, title: str):
        print(f"[WikiScraper] Scraping page: '{title}'")

        # 1 metadata (and resolve title)
        metadata = self.api.fetch_metadata(title=title)
        
        # Extract page data
        pages_dict = metadata["query"]["pages"]
        page_data = next(iter(pages_dict.values()))
        
        if "missing" in page_data:
             raise ValueError(f"Página '{title}' não encontrada")

        page_id = page_data["pageid"]
        resolved_title = page_data["title"]

        node = PageNode(
            page_id=page_id,
            title=resolved_title,
            url=page_data["fullurl"],
            length_chars=page_data.get("length", 0),
            num_editors=len(page_data.get("contributors", [])),
            num_revisions=len(page_data.get("revisions", [])),
            links_out_count=0,
        )

        print(f"[WikiScraper] Node created: {node}")

        # 3 HTML
        html = self.api.fetch_html(page_id)

        # 4 parse links
        extracted = self.parser.extract_links(html)
        print(f"[WikiScraper] {len(extracted)} links extracted")

        # Batch resolve all target titles
        target_titles = [t for t, _ in extracted]
        resolved_map = self.api.resolve_titles_batch(target_titles)

        edges = []
        for target_title, anchor in extracted:
            if target_title in resolved_map:
                target_id, resolved_target_title = resolved_map[target_title]
                edge = LinkNode(
                    source_page_id=page_id,
                    target_page_id=target_id,
                    anchor_text=anchor,
                    target_title=resolved_target_title,
                )
                edges.append(edge)
            # else: page missing or error, skip

        node.links_out_count = len(edges)

        print(f"[WikiScraper] Final: {len(edges)} edges")

        return node, edges
