import requests
import time

BASE_URL = "http://localhost:8000"

# Core Requirement: 10-20 domain-specific questions
GOLDEN_DATASET = [
    {"question": "What is Celery used for?", "expected_doc_id": "doc_celery_core"},
    {"question": "Why implement Redis in a RAG stack?", "expected_doc_id": "doc_redis_core"},
    {"question": "What does OpenTelemetry handle?", "expected_doc_id": "doc_otel_core"},
    {"question": "How does Prometheus get application metrics?", "expected_doc_id": "doc_prom_core"},
    {"question": "What visualization role does Grafana serve?", "expected_doc_id": "doc_grafana_core"},
    {"question": "Why is asynchronous data ingestion necessary?", "expected_doc_id": "doc_async_core"},
    {"question": "What is exact-match caching used for?", "expected_doc_id": "doc_cache_core"},
    {"question": "How do you mitigate embedding API rate limits?", "expected_doc_id": "doc_retry_core"},
    {"question": "What role do RED metrics play?", "expected_doc_id": "doc_red_core"},
    {"question": "Why tag metrics with a variant label during A/B tests?", "expected_doc_id": "doc_ab_core"},
]

def ingest_data():
    print("🚀 Ingesting golden documents asynchronously...")
    docs = [
        ("doc_celery_core", "Celery is an asynchronous task queue/job queue based on distributed message passing."),
        ("doc_redis_core", "Redis is an open source, in-memory data structure store, used as a database, cache, and message broker."),
        ("doc_otel_core", "OpenTelemetry provides vendor-agnostic instrumentation to trace requests and collect metrics from Python apps."),
        ("doc_prom_core", "Prometheus is a time-series database that periodically scrapes metrics exposed by the application metrics route."),
        ("doc_grafana_core", "Grafana connects to Prometheus to build real-time dashboards allowing engineers to track system vitals."),
        ("doc_async_core", "Asynchronous ingestion offloads CPU-bound text processing to background queues to maximize primary server loop throughput."),
        ("doc_cache_core", "Exact-match caching saves money and reduces latency by intercepting identical user questions before hitting the LLM."),
        ("doc_retry_core", "Exponential backoff configurations on tasks guarantee that temporary network timeouts or rate limits do not crash the pipeline."),
        ("doc_red_core", "RED metrics quantify Rate, Errors, and Duration to mathematically prove application status at runtime."),
        ("doc_ab_core", "Tagging metrics with a variant string enables continuous evaluation framework validation inside dashboard graphics."),
    ]
    
    for doc_id, text in docs:
        resp = requests.post(f"{BASE_URL}/ingest", json={"text": text})
        print(f"✅ Queued Ingestion: {resp.json()}")

def run_evaluation_pass(label="Initial Pass (Cache Misses)"):
    latencies = []
    retrieval_hits = 0
    total = len(GOLDEN_DATASET)
    
    print(f"\n⚡ Executing Benchmarks: {label}...")
    for item in GOLDEN_DATASET:
        start_time = time.time()
        resp = requests.post(f"{BASE_URL}/query", json={"question": item["question"], "variant": "default"})
        latency = time.time() - start_time
        latencies.append(latency)
        
        data = resp.json()
        sources = data.get("sources", [])
        cache_status = resp.headers.get("X-Cache", "UNKNOWN")
        
        is_retrieved = False
        for source in sources:
            if source.get("chunk_idx") is not None:
                is_retrieved = True
                break
        
        if is_retrieved:
            retrieval_hits += 1
            
        print(f"Q: {item['question'][:30]}... | Latency: {latency:.4f}s | Cache: {cache_status} | Hits Context: {is_retrieved}")
        
    avg_latency = sum(latencies) / total if total > 0 else 0
    hit_rate = (retrieval_hits / total) * 100 if total > 0 else 0
    
    print(f"\n--- {label} Summary ---")
    print(f"Average Latency: {avg_latency:.4f}s")
    print(f"Retrieval Accuracy (Hit Rate): {hit_rate:.2f}%")

if __name__ == "__main__":
    try:
        print("🔍 Testing connection to core cluster topology...")
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        if health.status_code != 200:
            raise Exception("Core application returned unhealthy.")
            
        ingest_data()
        
        print("\n⏳ Pausing 5 seconds for Celery worker processes to clear queue and write embeddings...")
        time.sleep(5)
        
        run_evaluation_pass("Pass 1: Cold Processing Pipeline")
        
        run_evaluation_pass("Pass 2: Warm Cached Execution Path")
        
    except Exception as e:
        print(f"❌ Critical Failure during lifecycle execution: {e}")
