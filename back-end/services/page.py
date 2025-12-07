from fastapi import Depends
from db.repositories.page import (
    PageRepository,
    get_page_repository,
)
from models.graph_objects import PageResponse
from scraper.wiki_scraper import WikiScraper
from services.graph_builder import save_graph


class PageService:
    def __init__(self, page_repository: PageRepository):
        self.repository = page_repository
        self.scraper = WikiScraper()

    def get_page_by_id(self, page_id: int) -> PageResponse | None:
        page_dict = self.repository.get_page_by_id(page_id)
        if not page_dict:
            return None
        # Converte dict para PageResponse (validação automática)
        return PageResponse(**page_dict)

    def get_or_scrape_page_by_title(self, title: str) -> PageResponse | None:
        """
        Busca página por título. Se não existir, faz scraping da Wikipedia e salva.
        """
        # Primeiro tenta buscar no banco
        page_dict = self.repository.get_page_by_title(title)
        if page_dict:
            return PageResponse(**page_dict)

        # Se não encontrou, faz scraping
        try:
            print(f"[PageService] Página '{title}' não encontrada. Fazendo scraping...")
            node, edges = self.scraper.scrape_page(title)

            # Salva no banco
            self.repository.save_page_with_links(node, edges)

            # Busca novamente para retornar com o formato correto
            page_dict = self.repository.get_page_by_id(node.page_id)
            if page_dict:
                return PageResponse(**page_dict)

            return None
        except Exception as e:
            print(f"[PageService] Erro ao fazer scraping: {e}")
            return None


def get_page_service(
    page_repository: PageRepository = Depends(get_page_repository),
) -> PageService:
    """Dependency injection factory para PageService"""
    return PageService(page_repository)
