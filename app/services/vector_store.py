import hashlib
from typing import List

from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.core.config import QDRANT_COLLECTION, QDRANT_URL

_VECTOR_SIZE = 16


def _client() -> QdrantClient:
    return QdrantClient(url=QDRANT_URL)


def _embed_text(text: str) -> List[float]:
    # Simple deterministic embedding placeholder for MVP.
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    values = [b / 255.0 for b in digest[:_VECTOR_SIZE]]
    return values


def ensure_collection() -> None:
    client = _client()
    collections = client.get_collections().collections
    names = {c.name for c in collections}
    if QDRANT_COLLECTION not in names:
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=models.VectorParams(size=_VECTOR_SIZE, distance=models.Distance.COSINE),
        )


def upsert_document(doc_id: int, title: str, content: str) -> None:
    client = _client()
    vector = _embed_text(f"{title}\n{content}")
    point = models.PointStruct(
        id=doc_id,
        vector=vector,
        payload={"title": title, "content": content},
    )
    client.upsert(collection_name=QDRANT_COLLECTION, points=[point])
