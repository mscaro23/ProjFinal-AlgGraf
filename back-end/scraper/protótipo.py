import requests
from bs4 import BeautifulSoup

WIKI_API = "https://pt.wikipedia.org/w/api.php"
WIKI_BASE_URL = "https://pt.wikipedia.org/wiki/"


# ===============================================================
# SCRAPER
# ===============================================================


class WikiScraper:

    def __init__(self, session=None):
        self.session = session or requests.Session()

    # -------------------------
    # Função auxiliar: chama API
    # -------------------------
    def _call_api(self, params):
        params["format"] = "json"
        response = self.session.get(WIKI_API, params=params)

        if not response.ok:
            raise RuntimeError(f"Erro ao chamar API: {response.status_code}")

        return response.json()

    # -------------------------
    # Resolve título → page_id (inclui redirects)
    # -------------------------
    def resolve_title(self, title):
        data = self._call_api({"action": "query", "titles": title, "redirects": 1})

        pages = data["query"]["pages"]
        page = next(iter(pages.values()))

        if "missing" in page:
            raise ValueError(f"Página '{title}' não encontrada.")

        return page["pageid"], page["title"]

    # -------------------------
    # Baixa metadados do nó (page_id)
    # -------------------------
    def fetch_page_metadata(self, page_id):
        data = self._call_api(
            {
                "action": "query",
                "pageids": page_id,
                "prop": "info|contributors|revisions|categories",
                "inprop": "url",
                "rvprop": "ids",
            }
        )

        page = data["query"]["pages"][str(page_id)]

        # número de editores
        num_editors = len(page.get("contributors", []))

        # número de revisões
        num_revisions = len(page.get("revisions", []))

        # tamanho do conteúdo
        length_chars = page.get("length", 0)

        # categorias
        categories = []
        if "categories" in page:
            categories = [
                c["title"].replace("Categoria:", "") for c in page["categories"]
            ]

        # url
        url = page.get("fullurl", f"{WIKI_BASE_URL}{page['title']}")

        return {
            "page_id": page_id,
            "title": page["title"],
            "url": url,
            "length_chars": length_chars,
            "num_editors": num_editors,
            "num_revisions": num_revisions,
            "categories": categories,
        }

    # -------------------------
    # Baixa HTML da página (body)
    # -------------------------
    def fetch_html(self, page_id):
        data = self._call_api({"action": "parse", "pageid": page_id, "prop": "text"})

        return data["parse"]["text"]["*"]

    # -------------------------
    # Extrai hyperlinks internos com anchor_text
    # -------------------------
    def extract_links(self, html, source_page_id):
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for a in soup.find_all("a"):
            href = a.get("href", "")
            anchor = a.get_text(strip=True)

            # ignorar links que não são para /wiki/...
            if not href.startswith("/wiki/"):
                continue

            # ignorar arquivos, categorias, portal, help, etc.
            if any(
                href.startswith(f"/wiki/{p}:")
                for p in [
                    "Ficheiro",
                    "Arquivo",
                    "Categoria",
                    "Especial",
                    "Ajuda",
                    "Portal",
                ]
            ):
                continue

            # extrair target_title
            target_title = href.replace("/wiki/", "").split("#")[0].replace("_", " ")

            # resolver target → page_id
            try:
                target_id, _ = self.resolve_title(target_title)
            except Exception:
                continue  # ignora redlinks ou páginas que não existem

            links.append(
                PageLink(
                    source_page_id=source_page_id,
                    target_page_id=target_id,
                    anchor_text=anchor,
                )
            )

        return links

    # ===========================================================
    # Função principal: baixa nó + arestas
    # ===========================================================
    def scrape_page(self, title):
        page_id, final_title = self.resolve_title(title)

        # metadados do nó
        meta = self.fetch_page_metadata(page_id)

        # html para extrair links
        html = self.fetch_html(page_id)
        links = self.extract_links(html, page_id)

        node = PageNode(
            page_id=meta["page_id"],
            title=meta["title"],
            url=meta["url"],
            length_chars=meta["length_chars"],
            num_editors=meta["num_editors"],
            num_revisions=meta["num_revisions"],
            categories=meta["categories"],
            links_out_count=len(links),
            links_in_count=0,  # preenchido depois, quando agregarmos várias páginas
        )

        return node, links
