from src.worker.celery_app import celery_app
from src.rag.vector_store import vector_store
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.core.logger import logger

@celery_app.task(bind=True, max_retries=3)
def ingest_document_task(self, document_id: str, text: str):
    logger.info("Starting ingestion task", document_id=document_id)
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            is_separator_regex=False,
        )
        chunks = text_splitter.split_text(text)
        
        metadatas = [{"document_id": document_id, "chunk_idx": i} for i in range(len(chunks))]
        
        vector_store.add_texts(chunks, metadatas=metadatas)
        
        logger.info("Ingestion completed successfully", document_id=document_id, chunks_count=len(chunks))
        return {"status": "success", "document_id": document_id, "chunks_inserted": len(chunks)}
    except Exception as e:
        logger.error("Ingestion failed", document_id=document_id, error=str(e))
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
