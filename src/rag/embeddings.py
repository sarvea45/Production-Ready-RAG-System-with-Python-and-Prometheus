from sentence_transformers import SentenceTransformer
import os

class Embedder:
    def __init__(self):
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        embedding = self.model.encode(text)
        return embedding.tolist()

embedder = Embedder()
