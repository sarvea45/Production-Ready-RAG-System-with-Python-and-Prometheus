# System Architecture

## Overview
This project implements a Production-Ready Retrieval-Augmented Generation (RAG) system based on a microservices architecture. It prioritizes decoupled processing, observability, and caching to ensure scalable and cost-efficient operations.

## Components

1. **Application Layer (FastAPI)**: 
   - Exposes REST endpoints (`/ingest`, `/query`, `/feedback`, `/health`, `/metrics`).
   - Handles A/B testing variants and user feedback.
   - Synchronously queries the Vector DB and LLM for answers if the cache misses.
   - Orchestrates background tasks for ingestion.

2. **Asynchronous Worker Layer (Celery)**:
   - Offloads CPU and I/O intensive tasks (document chunking, embedding generation).
   - Allows the main FastAPI loop to remain highly responsive.
   - Uses Redis as a broker and result backend.

3. **State & Broker Layer (Redis)**:
   - Serves as the message broker for Celery.
   - Acts as an exact-match caching layer for LLM responses. Cached responses are hashed (SHA-256) and stored with a 24-hour TTL to prevent stale data accumulation.

4. **Vector Database (ChromaDB)**:
   - Stores text chunks and their embeddings.
   - Mounted to a persistent Docker volume to survive container restarts.

5. **LLM & Embedding Models**:
   - Embeddings are generated using local `sentence-transformers` models to eliminate API costs and reduce network latency.
   - LLM generation defaults to a local `Ollama` container running `llama3` for true production equivalence without incurring commercial API costs. (It can be swapped to OpenAI via environment variables).

6. **Observability Stack (OpenTelemetry, Prometheus, Grafana)**:
   - The application is instrumented using `opentelemetry-python`.
   - Custom meters track API RPS, Latencies, Cache Hit Rates, and LLM Token Cost.
   - Prometheus scrapes `/metrics` every 15 seconds.
   - Grafana auto-provisions a default dashboard to visualize RED (Rate, Errors, Duration) metrics.

## Trade-offs
- **Exact-Match vs Semantic Caching**: Exact-match caching was chosen for simplicity and zero false-positive risk. A semantic cache could further improve hit rates but introduces complexity and latency to the caching layer itself.
- **Local Embedding vs API**: Running `sentence-transformers` in the Celery worker uses more CPU but avoids rate limits and costs associated with external APIs like OpenAI's `text-embedding-ada-002`.
