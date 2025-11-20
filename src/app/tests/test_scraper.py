from app.scraper.wiki_scraper import WikiScraper
from app.models.graph_objects import PageNode, PageLink


def test_scrape_page():
    scraper = WikiScraper()

    node, edges = scraper.scrape_page("Engenharia")

    # Testa estrutura do nó
    assert isinstance(node, PageNode)
    assert node.page_id > 0
    assert node.title.startswith("Engenharia")
    assert node.length_chars > 0
    assert node.links_out_count == len(edges)

    # Testa algumas arestas
    assert all(isinstance(e, PageLink) for e in edges)
    assert len(edges) > 5  # A página com certeza tem >5 links

    # Verifica se alguma aresta leva a "Desenho" (como no texto)
    assert any(
        "Desenho" in e.anchor_text or "desenho" in e.anchor_text.lower() for e in edges
    )
