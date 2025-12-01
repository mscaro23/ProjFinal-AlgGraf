from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_page_id = Column(Integer, ForeignKey("pages.page_id"), nullable=False)
    target_page_id = Column(Integer, ForeignKey("pages.page_id"), nullable=False)
    target_title = Column(String, nullable=True)
    anchor_text = Column(String, nullable=True)
