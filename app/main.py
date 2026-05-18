from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Monkeypatch posthog to completely silence ChromaDB's telemetry log spam (capture() signature mismatch issue)
try:
    import posthog
    def dummy_capture(*args, **kwargs):
        pass
    posthog.capture = dummy_capture
except ImportError:
    pass

from app.api.endpoints import router as api_router
from app.api.dependencies import get_rag_pipeline

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Enterprise AI Agent Platform",
    description="Backend API for Document Upload and RAG Chat with LLM",
    version="1.0.0",
)

# Configure CORS to allow the Widget to connect from any domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, limit this to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the main API router
app.include_router(api_router, prefix="/api", tags=["chat"])

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing Enterprise AI Agent Platform...")
    # Initialize the RAG Pipeline (which connects to ChromaDB and LLM Router)
    get_rag_pipeline()
    logger.info("Application successfully started and ready to serve requests.")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Enterprise AI Agent"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
