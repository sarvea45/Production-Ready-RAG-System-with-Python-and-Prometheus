import chromadb
from src.core.config import settings
from src.rag.embeddings import embedder
import uuid

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_directory)
        self.collection = self.client.get_or_create_collection(name="rag_collection")

    def add_texts(self, texts: list[str], metadatas: list[dict] = None):
        if not texts:
            return
        embeddings = embedder.embed_documents(texts)
        ids = [str(uuid.uuid4()) for _ in texts]
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas if metadatas else [{"source": "unknown"} for _ in texts]
        )

    def similarity_search(self, query: str, k: int = 3):
        query_embedding = embedder.embed_query(query)
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k
            )
            if not results['documents'] or not results['documents'][0]:
                return [], []
            return results['documents'][0], results['metadatas'][0]
        except Exception:
            return [], []

vector_store = VectorStore()
