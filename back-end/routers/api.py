from fastapi import APIRouter, Depends, HTTPException, Query

from services.page import PageService, get_page_service
from models.graph_objects import PageResponse
from settings.logging_setup import logger
from db.session import get_db
from sqlalchemy.orm import Session
from services.pagerank_service import calculate_and_update_pagerank
from services.pathfinding import find_paths


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


@router.post("/pagerank/calculate")
def calculate_pagerank_route(
    d: float = 0.85,
    max_iter: int = 100,
    tol: float = 1e-6,
    db: Session = Depends(get_db),
):
    """
    Calcula e atualiza o PageRank para todas as páginas no banco de dados.
    
    Args:
        d: Fator de amortecimento (default: 0.85)
        max_iter: Número máximo de iterações (default: 100)
        tol: Tolerância para convergência (default: 1e-6)
    
    Returns:
        dict: Mensagem de sucesso e estatísticas
    """
    try:
        ranks = calculate_and_update_pagerank(
            session=db,
            d=d,
            max_iter=max_iter,
            tol=tol,
        )
        
        if not ranks:
            return {
                "message": "Nenhuma página encontrada no banco de dados",
                "pages_updated": 0,
            }
        
        return {
            "message": "PageRank calculado e atualizado com sucesso",
            "pages_updated": len(ranks),
            "total_score": sum(ranks.values()),
            "min_score": min(ranks.values()),
            "max_score": max(ranks.values()),
        }
    except Exception as e:
        logger.error(f"Erro ao calcular PageRank: {str(e)}")
        raise HTTPException(500, f"Erro ao calcular PageRank: {str(e)}")


@router.get("/paths")
def find_paths_route(
    source_page_id: int = Query(..., description="ID da página origem"),
    target_page_id: int = Query(..., description="ID da página destino"),
    max_depth: int = Query(10, description="Profundidade máxima para busca lógica"),
    db: Session = Depends(get_db),
):
    """
    Encontra dois caminhos entre duas páginas:
    1. Caminho mais curto (menor número de vértices) - usando BFS
    2. Caminho mais lógico (baseado em PageRank) - priorizando páginas importantes
    
    Args:
        source_page_id: ID da página origem
        target_page_id: ID da página destino
        max_depth: Profundidade máxima para busca lógica (default: 10)
    
    Returns:
        dict com:
            - shortest_path: caminho mais curto (lista de páginas)
            - logical_path: caminho mais lógico (lista de páginas)
            - shortest_length: número de vértices no caminho mais curto
            - logical_length: número de vértices no caminho mais lógico
    """
    try:
        result = find_paths(
            session=db,
            source_page_id=source_page_id,
            target_page_id=target_page_id,
            max_depth=max_depth,
        )
        
        if result["shortest_path"] is None and result["logical_path"] is None:
            raise HTTPException(
                404,
                f"Nenhum caminho encontrado entre as páginas {source_page_id} e {target_page_id}"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar caminhos: {str(e)}")
        raise HTTPException(500, f"Erro ao buscar caminhos: {str(e)}")


@router.get("/test_router")
def test_router():
    return {"message": "Router is working"}
