from pydantic import BaseModel
from typing import Optional, List

"""
Como boa prática, utilizar uma classe/model para cada tipo de requisição
    ModelBase -> Model padrao
    ModelCreate -> criar novo model (POST)
    ModelUpdate -> atualizar model (PUT, PATCH)
    ModelResponse -> retornar model (GET)
    ModelInput -> payload (POST, PUT, PATCH)
"""


# ---------- PAGE ----------
class PageBase(BaseModel):
    page_id: int
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
    class Config:
        from_attributes = True


# ---------- LINK ----------
class LinkBase(BaseModel):
    source_page_id: int
    target_page_id: int
    anchor_text: Optional[str] = None


class LinkCreate(LinkBase):
    pass


class LinkResponse(LinkBase):
    id: int

    class Config:
        from_attributes = True


# ---------- GRAFO ----------
class GraphInput(BaseModel):
    pages: List[PageCreate]
    links: List[LinkCreate]


class GraphLink(BaseModel):
    """Link para resposta do grafo (fonte e alvo como strings - títulos das páginas)"""

    source: str
    target: str


class GraphResponse(BaseModel):
    """Resposta do grafo com nodes (títulos) e links"""

    nodes: List[str]
    links: List[GraphLink]


class PageRankResponse(BaseModel):
    """Resposta do cálculo de PageRank"""

    pagerank: dict[str, float]
