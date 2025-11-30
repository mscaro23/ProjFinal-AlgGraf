from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import Depends
from db.session import get_db


class PageRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_page_by_id(self, page_id: int) -> dict | None:
        query = text("SELECT * FROM pages WHERE page_id = :page_id")
        result = self.db_session.execute(query, {"page_id": page_id})
        return result.mappings().first()


def get_page_repository(db: Session = Depends(get_db)) -> PageRepository:
    return PageRepository(db)
