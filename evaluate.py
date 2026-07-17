import requests
import time

BASE_URL = "http://localhost:8000"

GOLDEN_DATASET = [
    {"question": "What is Celery used for?", "expected_keyword": "asynchronous task queue"},
    {"question": "Why use Redis?", "expected_keyword": "in-memory data structure store"}
]

def ingest_data():
    print("Ingesting golden documents...")
    docs = [
        "Celery is an asynchronous task queue/job queue based on distributed message passing.",
        "Redis is an open source, in-memory data structure store, used as a database, cache, and message broker."
    ]
    for doc in docs:
        resp = requests.post(f"{BASE_URL}/ingest", json={"text": doc})
        print(f"Ingested doc: {resp.json()}")

def evaluate():
    latencies = []
    hits = 0
    total = len(GOLDEN_DATASET)
    
    print("\nEvaluating RAG pipeline...")
    for item in GOLDEN_DATASET:
        start_time = time.time()
        resp = requests.post(f"{BASE_URL}/query", json={"question": item["question"]})
        latency = time.time() - start_time
        latencies.append(latency)
        
        data = resp.json()
        answer = data.get("answer", "").lower()
        # In a real system, you'd check context sources. For this mock evaluation, we check if the LLM output contained the expected keyword.
        if item["expected_keyword"].lower() in answer:
            hits += 1
            
        print(f"Q: {item['question']} | Latency: {latency:.2f}s | Cache: {resp.headers.get('X-Cache')} | Answer: {answer[:30]}...")
        
    avg_latency = sum(latencies) / total if total > 0 else 0
    hit_rate = (hits / total) * 100 if total > 0 else 0
    
    print("\n--- Evaluation Summary ---")
    print(f"Average Latency: {avg_latency:.2f}s")
    print(f"Retrieval Accuracy (Hit Rate): {hit_rate:.2f}%")

if __name__ == "__main__":
    try:
        # Check health first
        requests.get(f"{BASE_URL}/health")
        ingest_data()
        print("Waiting 5 seconds for Celery to process embeddings...")
        time.sleep(5)
        evaluate()
    except Exception as e:
        print(f"Failed to connect to API: {e}")
