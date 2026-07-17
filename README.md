# Production-Ready RAG System

An enterprise-grade, highly observable Retrieval-Augmented Generation (RAG) system with a FastAPI backend, Celery asynchronous processing, multi-level Redis caching, and deep OpenTelemetry instrumentation mapped to a Prometheus/Grafana stack.

## Getting Started

1. Set up the environment variables:
```bash
cp .env.example .env
```
2. Build and start the services:
```bash
docker-compose build
docker-compose up -d
```
3. (Ollama setup) Pull the default LLM model (required for querying):
```bash
docker-compose exec ollama ollama pull llama3
```
4. Access endpoints:
- API: `http://localhost:8000`
- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9090`

## Documentation
- See `ARCHITECTURE.md` for design specifics.
- See `RUNBOOK.md` for operational instructions and troubleshooting.
