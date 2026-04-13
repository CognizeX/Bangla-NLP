import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nlp:nlp@localhost:5432/nlpdb")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "documents")
