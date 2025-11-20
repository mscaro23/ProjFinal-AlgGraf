from bs4 import BeautifulSoup
from urllib.parse import unquote


class HTMLParser:

    def extract_links(self, html: str):
        print(f"[HTMLParser] Parsing HTML ({len(html)} chars)")
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)
            print(f"  [HTMLParser] Found <a>: href='{href}' text='{text}'")

            if href.startswith("/wiki/"):
                title = href.replace("/wiki/", "")
                decoded = unquote(title)
                links.append((decoded, text.lower()))
                print(
                    f"    [HTMLParser] Internal link → title='{decoded}' anchor='{text.lower()}'"
                )

        print(f"[HTMLParser] Extracted {len(links)} links.")
        return links
