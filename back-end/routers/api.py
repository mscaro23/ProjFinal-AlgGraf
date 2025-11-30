from fastapi import APIRouter


router = APIRouter(tags=["api"])


@router.get("/test_router")
def test_router():
    return {"message": "Router is working"}
