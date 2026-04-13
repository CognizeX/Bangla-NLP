from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.controllers.api_controller import router as api_router
from app.controllers.web_controller import router as web_router
from app.core.database import Base, engine
from app.services.vector_store import ensure_collection

app = FastAPI(title="NLP Project", description="Natural Language Processing project", version="1.0.0")
app.mount("/static", StaticFiles(directory="app/views/static"), name="static")

app.include_router(web_router)
app.include_router(api_router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_collection()
