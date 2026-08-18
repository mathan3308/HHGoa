from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.api import health, voice, query, search

app = FastAPI(
    title="Voice-Enabled RAG API",
    description="Production Voice-Enabled Retrieval-Augmented Generation system with multi-strategy chunking, hybrid RRF retrieval, 4 guardrail layers, and latency analytics.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health.router)
app.include_router(voice.router)
app.include_router(query.router)
app.include_router(search.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
