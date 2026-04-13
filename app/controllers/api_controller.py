from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentRead
from app.services.vector_store import upsert_document

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/documents", response_model=list[DocumentRead])
def list_documents(db: Session = Depends(get_db)):
    return db.query(Document).order_by(Document.id.desc()).all()


@router.post("/documents", response_model=DocumentRead)
def create_document(data: DocumentCreate, db: Session = Depends(get_db)):
    doc = Document(title=data.title, content=data.content)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    upsert_document(doc.id, doc.title, doc.content)
    return doc
