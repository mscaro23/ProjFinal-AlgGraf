from fastapi import APIRouter, Depends, HTTPException

from services.page import PageService, get_page_service
from models.graph_objects import PageResponse


router = APIRouter(tags=["api"])


@router.get("/pages/{page_id}", response_model=PageResponse)
def get_page_by_id_route(
    page_id: int, service: PageService = Depends(get_page_service)
):
    page = service.get_page_by_id(page_id)
    if not page:
        raise HTTPException(404, "Page not found")
    return page


@router.get("/test_router")
def test_router():
    return {"message": "Router is working"}
