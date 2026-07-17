# Runbook: Operations and Maintenance

## 1. Verifying System Health
Use Docker commands to verify the health of the entire stack:
```bash
docker-compose ps
```
Look for `Up (healthy)` under the `api` and `redis` services.
Alternatively, query the health endpoint directly:
```bash
curl http://localhost:8000/health
```

## 2. Managing the LLM Engine (Ollama)
The system defaults to using Ollama. Before making live queries, ensure the model is pulled inside the Ollama container:
```bash
docker exec -it <ollama_container_id> ollama pull llama3
```
If you encounter `ollama_generation_error` logs, verify the model has been pulled.

## 3. Interpreting Grafana Dashboards
Access Grafana at `http://localhost:3000` (credentials: `admin` / `admin`).
- **Latency Spikes**: Check the "Latency Distribution" panel. If p99 latency spikes significantly above p50, it often indicates LLM API degradation or rate-limiting delays.
- **Cache Hit Rate**: If the hit rate is 0%, verify that identical questions are actually being sent, or check Redis connectivity.

## 4. Clearing Redis Cache (Poisoned Data)
If a bad response was cached, you can manually flush the Redis database:
```bash
docker-compose exec redis redis-cli FLUSHALL
```
Or target a specific key:
```bash
docker-compose exec redis redis-cli DEL "rag_cache:<hash>"
```

## 5. Restarting a Stuck Celery Worker
If ingestion tasks are not progressing, restart the worker gracefully without dropping queued tasks (they persist in Redis):
```bash
docker-compose restart worker
```
Check logs:
```bash
docker-compose logs -f worker
```
