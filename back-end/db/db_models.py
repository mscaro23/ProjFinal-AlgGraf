from sqlalchemy import Column, Integer, String, ForeignKey, Float
from db.base import Base


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_page_id = Column(Integer, ForeignKey("pages.page_id"), nullable=False)
    target_page_id = Column(Integer, ForeignKey("pages.page_id"), nullable=False)
    anchor_text = Column(String, nullable=True)


class Page(Base):
    __tablename__ = "pages"

    page_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    length_chars = Column(Integer)
    num_editors = Column(Integer)
    num_revisions = Column(Integer)
    links_out_count = Column(Integer)
    links_in_count = Column(Integer)
    pagerank_score = Column(Float, default=0.0)
