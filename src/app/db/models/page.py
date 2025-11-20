from sqlalchemy import Column, Integer, String
from app.db.base import Base


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
