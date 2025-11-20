from app.scraper.api_client import APIClient
from app.scraper.html_parser import HTMLParser
from app.models.graph_objects import PageNode, PageLink


class WikiScraper:

    def __init__(self, api_client=None):
        self.api = api_client or APIClient()
        self.parser = HTMLParser()
        print("[WikiScraper] Initialized.")

    def scrape_page(self, title: str):
        print(f"[WikiScraper] Scraping page: '{title}'")

        # 1 resolve title
        page_id, resolved_title = self.api.resolve_title(title)

        # 2 metadata
        metadata = self.api.fetch_metadata(page_id)
        page_data = metadata["query"]["pages"][str(page_id)]

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

        edges = []
        for target_title, anchor in extracted:
            try:
                target_id, _ = self.api.resolve_title(target_title)
                edge = PageLink(
                    source_page_id=page_id, target_page_id=target_id, anchor_text=anchor
                )
                edges.append(edge)
                print(f"  [WikiScraper] Edge created → {edge}")
            except:
                print(f"  [WikiScraper] Could not resolve target: '{target_title}'")
                continue

        node.links_out_count = len(edges)

        print(f"[WikiScraper] Final: {len(edges)} edges")

        return node, edges
