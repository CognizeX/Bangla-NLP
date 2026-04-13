from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.document import Document
from app.services.vector_store import upsert_document

templates = Jinja2Templates(directory="app/views/templates")
router = APIRouter(tags=["web"])


@router.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.id.desc()).all()
    return templates.TemplateResponse("index.html", {"request": request, "documents": docs})


@router.post("/documents")
def create_document(
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db),
):
    doc = Document(title=title, content=content)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    upsert_document(doc.id, doc.title, doc.content)
    return RedirectResponse(url="/", status_code=303)
