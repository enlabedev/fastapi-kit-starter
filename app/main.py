import uvicorn
from app.config.settings import settings
from app.routes.api import router
from app.utils.exception import AppBaseException
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix=settings.API_PREFIX)


async def base_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


app.add_exception_handler(AppBaseException, base_exception_handler)


@app.get("/api/healthchecker")
def root() -> dict:
    return {"message": "Welcome to FastAPI with SQLAlchemy"}


def start() -> None:
    """Launched with `poetry run start` at root level"""
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
