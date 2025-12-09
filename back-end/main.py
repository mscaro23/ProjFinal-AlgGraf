from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from dotenv import load_dotenv
from uvicorn import Server, Config
from settings.logging_setup import logger

from routers.api import router as api_router
import db.base as db_base
import db.engine as db_engine

db_base.Base.metadata.create_all(bind=db_engine.engine)


app = FastAPI()

# CORS - Configuração completa para desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Adicionar routers depois do CORS
app.include_router(api_router, prefix="/api")


server = Server(
    Config(
        "main:app",
        host="0.0.0.0",
        port=8000,
        proxy_headers=True,
        forwarded_allow_ips="*",
        reload=True,
        server_header=False,
    ),
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logger.error(f"{request}: {exc_str}")
    content = {"status_code": 422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@app.exception_handler(Exception)
async def custom_error_handling(request: Request, exc: Exception):
    return JSONResponse(
        {"detail": "Se o erro persistir, contate o suporte"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(e)
        return Response("Internal server error", status_code=500)


if __name__ == "__main__":
    server.run()
