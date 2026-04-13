from pydantic import BaseModel


class DocumentCreate(BaseModel):
    title: str
    content: str


class DocumentRead(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        from_attributes = True
