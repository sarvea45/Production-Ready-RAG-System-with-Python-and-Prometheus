import time
from fastapi import FastAPI, Request
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from src.core.observability import prometheus_app, api_request_counter, api_duration_histogram
from src.api.routes import router

app = FastAPI(title="Production RAG API")

app.mount("/metrics", prometheus_app)

@app.middleware("http")
async def add_metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    labels = {
        "endpoint": request.url.path,
        "method": request.method,
        "http_status": str(response.status_code)
    }
    
    # Do not track metrics endpoint itself to avoid noise
    if request.url.path != "/metrics":
        api_request_counter.add(1, labels)
        api_duration_histogram.record(duration, labels)
    
    return response

app.include_router(router)

FastAPIInstrumentor.instrument_app(app)

@app.get("/health")
def health():
    return {"status": "healthy"}
