import hashlib
import json
import uuid
from typing import Optional
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.core.cache import redis_client
from src.core.observability import cache_counter
from src.core.logger import logger
from src.rag.vector_store import vector_store
from src.rag.llm import llm_client
from src.worker.tasks import ingest_document_task

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    variant: Optional[str] = "default"

class IngestRequest(BaseModel):
    text: str

class FeedbackRequest(BaseModel):
    query_id: str
    score: int
    comment: Optional[str] = None

def normalize_text(text: str) -> str:
    return text.lower().strip().rstrip('.,?!')

@router.post("/query")
async def handle_query(request: QueryRequest):
    question = request.question
    variant = request.variant
    
    normalized_q = normalize_text(question)
    q_hash = hashlib.sha256(normalized_q.encode()).hexdigest()
    cache_key = f"rag_cache:{q_hash}"
    
    try:
        cached_response = await redis_client.get(cache_key)
        if cached_response:
            cache_counter.add(1, {"outcome": "hit", "variant": variant})
            return JSONResponse(
                content=json.loads(cached_response), 
                headers={"X-Cache": "HIT"}
            )
    except Exception as e:
        logger.error("redis_cache_error", error=str(e))
        
    cache_counter.add(1, {"outcome": "miss", "variant": variant})
    
    k_chunks = 3
    system_prompt = "You are a helpful assistant. Use the following context to answer the question."
    if variant == "variant_b":
        k_chunks = 5
        system_prompt = "You are an expert technical assistant. Provide a highly detailed answer using the context."

    try:
        context_docs, context_metadata = vector_store.similarity_search(question, k=k_chunks)
    except Exception as e:
        logger.error("vector_db_error", error=str(e))
        return JSONResponse(status_code=503, content={"detail": "Service Unavailable - Vector DB Error"})
        
    context_str = "\n".join(context_docs)
    prompt = f"Context:\n{context_str}\n\nQuestion:\n{question}"
    
    answer = llm_client.generate(prompt=prompt, system_prompt=system_prompt)
    
    response_data = {
        "answer": answer, 
        "sources": context_metadata
    }
    
    try:
        await redis_client.setex(cache_key, 86400, json.dumps(response_data))
    except Exception as e:
        logger.error("redis_set_error", error=str(e))
    
    return JSONResponse(content=response_data, headers={"X-Cache": "MISS"})

@router.post("/ingest", status_code=202)
async def handle_ingest(request: IngestRequest):
    doc_id = str(uuid.uuid4())
    task = ingest_document_task.delay(doc_id, request.text)
    return {"task_id": task.id, "status": "accepted"}

@router.post("/feedback")
async def handle_feedback(request: FeedbackRequest):
    logger.info(
        "user_feedback", 
        query_id=request.query_id, 
        score=request.score, 
        comment=request.comment
    )
    return {"status": "success"}
