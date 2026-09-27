from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db_session
from app.routers import api_router
from app.services.errors import ServiceError


app = FastAPI(
    title="Private Reservations API",
    version="0.1.0",
)
app.include_router(api_router)


@app.exception_handler(ServiceError)
async def service_error_handler(_: Request, exc: ServiceError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


@app.get("/api/health", tags=["health"])
def health(session: Session = Depends(get_db_session)) -> dict[str, str]:
    session.execute(text("SELECT 1"))
    return {"status": "ok"}

frontend_directory = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=frontend_directory, html=True), name="frontend")
