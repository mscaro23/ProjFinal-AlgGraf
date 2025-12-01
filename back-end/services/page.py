from fastapi import Depends
from sqlalchemy.orm import Session
from db.repositories.page import (
    PageRepository,
    get_page_repository,
)
from models.graph_objects import PageResponse


class PageService:
    def __init__(self, page_repository: PageRepository):
        self.repository = page_repository

    def get_page_by_id(self, page_id: int) -> PageResponse | None:
        page_dict = self.repository.get_page_by_id(page_id)
        if not page_dict:
            return None
        # Converte dict para PageResponse (validação automática)
        return PageResponse(**page_dict)


def get_page_service(
    page_repository: PageRepository = Depends(get_page_repository),
) -> PageService:
    """Dependency injection factory para PageService"""
    return PageService(page_repository)
