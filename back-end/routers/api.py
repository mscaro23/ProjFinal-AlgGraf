from fastapi import APIRouter, Depends, HTTPException, Query

from services.page import PageService, get_page_service
from models.graph_objects import GraphResponse, PageResponse
from settings.logging_setup import logger


router = APIRouter(tags=["api"])


@router.get("/pages/{page_id}", response_model=PageResponse)
def get_page_by_id_route(
    page_id: int, service: PageService = Depends(get_page_service)
):
    page = service.get_page_by_id(page_id)
    logger.info("Getting page by id " + str(page))
    if not page:
        raise HTTPException(404, "Page not found")
    return page


@router.get("/pages/title/{title}", response_model=PageResponse)
def get_page_by_title_route(
    title: str, service: PageService = Depends(get_page_service)
):
    """
    Busca página por título. Se não existir no banco, faz scraping da Wikipedia.
    """
    page = service.get_or_scrape_page_by_title(title)
    logger.info(f"Getting page by title '{title}': {page}")
    if not page:
        raise HTTPException(404, f"Page '{title}' not found and could not be scraped")
    return page


@router.get("/graph/build", response_model=GraphResponse)
def build_graph_route(
    seed: str = Query(..., description="Título da página semente"),
    depth: int = Query(1, ge=1, le=3, description="Profundidade do BFS (1-3)"),
    service: PageService = Depends(get_page_service),
):
    """
    Gera um grafo a partir do título semente e profundidade usando BFS.
    Faz scraping das páginas necessárias se não existirem no banco.
    """
    logger.info(f"Building graph: seed='{seed}', depth={depth}")
    graph = service.generate_graph(seed, depth)
    if not graph:
        raise HTTPException(404, f"Graph for seed '{seed}' could not be generated")
    return graph


@router.get("/test_router")
def test_router():
    return {"message": "Router is working"}
