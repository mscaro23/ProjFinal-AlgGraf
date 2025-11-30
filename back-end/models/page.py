from pydantic import BaseModel
from typing import Optional, List


class PageBase(BaseModel):
    title: str
    url: str
    length_chars: Optional[int] = None
    num_editors: Optional[int] = None
    num_revisions: Optional[int] = None
    links_out_count: Optional[int] = None
    links_in_count: Optional[int] = None
    pagerank_score: Optional[float] = 0.0


class PageCreate(PageBase):
    pass


class PageUpdate(BaseModel):
    pagerank_score: Optional[float] = None


class PageResponse(PageBase):
    page_id: int

    class Config:
        orm_mode = True
