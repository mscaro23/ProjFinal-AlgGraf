from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import Depends
from db.session import get_db
from db.db_models import Page, Link
from models.graph_objects import PageBase, LinkBase


class PageRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_page_by_id(self, page_id: int) -> dict | None:
        query = text("SELECT * FROM pages WHERE page_id = :page_id")
        result = self.db_session.execute(query, {"page_id": page_id})
        return result.mappings().first()

    def get_page_by_title(self, title: str) -> dict | None:
        query = text("SELECT * FROM pages WHERE title = :title")
        result = self.db_session.execute(query, {"title": title})
        return result.mappings().first()

    def get_subgraph(self, page_ids: list[int]) -> tuple[list[dict], list[dict]]:
        """Retorna todas as páginas e links de um conjunto de page_ids."""
        if not page_ids:
            return [], []
        
        # Buscar páginas
        pages_query = text("SELECT * FROM pages WHERE page_id = ANY(:page_ids)")
        pages_result = self.db_session.execute(pages_query, {"page_ids": page_ids})
        pages = [dict(row) for row in pages_result.mappings()]
        
        # Buscar links entre essas páginas
        links_query = text(
            "SELECT * FROM links WHERE source_page_id = ANY(:page_ids) AND target_page_id = ANY(:page_ids)"
        )
        links_result = self.db_session.execute(links_query, {"page_ids": page_ids})
        links = [dict(row) for row in links_result.mappings()]
        
        return pages, links

    def save_page(self, page_data: PageBase) -> None:
        """Salva ou atualiza uma página no banco de dados."""
        existing_page = (
            self.db_session.query(Page).filter_by(page_id=page_data.page_id).first()
        )

        if existing_page:
            existing_page.title = page_data.title
            existing_page.url = page_data.url
            existing_page.length_chars = page_data.length_chars
            existing_page.num_editors = page_data.num_editors
            existing_page.num_revisions = page_data.num_revisions
            existing_page.links_out_count = page_data.links_out_count
        else:
            new_page = Page(
                page_id=page_data.page_id,
                title=page_data.title,
                url=page_data.url,
                length_chars=page_data.length_chars,
                num_editors=page_data.num_editors,
                num_revisions=page_data.num_revisions,
                links_out_count=page_data.links_out_count,
                links_in_count=0,
                pagerank_score=0.0,
            )
            self.db_session.add(new_page)

    def delete_links_by_source(self, source_page_id: int) -> None:
        """Remove todos os links de uma página fonte."""
        self.db_session.query(Link).filter_by(source_page_id=source_page_id).delete()

    def save_links(self, links: list[LinkBase]) -> None:
        """Salva múltiplos links no banco de dados."""
        for link in links:
            new_link = Link(
                source_page_id=link.source_page_id,
                target_page_id=link.target_page_id,
                anchor_text=link.anchor_text,
            )
            self.db_session.add(new_link)

    def save_page_with_links(self, page_data: PageBase, links: list[LinkBase]) -> None:
        """Salva uma página e seus links no banco de dados."""
        self.save_page(page_data)
        self.delete_links_by_source(page_data.page_id)
        self.save_links(links)
        self.db_session.commit()


def get_page_repository(db: Session = Depends(get_db)) -> PageRepository:
    return PageRepository(db)
