from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from .core.config import settings
from .api.routes import api_router
from .llm.service import initialize_llm_service
from .rag.service import initialize_rag_service

# Load environment variables
load_dotenv()

app = FastAPI(
    title="ASCLEA API",
    description="Medical AI Assistant based on Llama 3 70B with RAG",
    version=os.getenv("API_VERSION", "v1")
)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    # Initialize LLM and RAG services
    await initialize_llm_service()
    await initialize_rag_service()
    print("ASCLEA API is started and ready.")

@app.on_event("shutdown")
async def shutdown_event():
    print("ASCLEA API is shutting down.")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
