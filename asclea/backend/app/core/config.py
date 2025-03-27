# backend/app/core/config.py
from pydantic import BaseModel, Field
import os
from typing import List, Optional

class Settings(BaseModel):
    """
    Anwendungseinstellungen, die aus Umgebungsvariablen geladen werden
    """
    # API
    API_VERSION: str = os.getenv("API_VERSION", "v1")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "entwicklungs-schluessel-nicht-fuer-produktion")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Datenbank
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./asclea.db")
    
    # Redis
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # LLM
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./models/llama3-70b-medical.gguf")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
    
    # Vektordatenbank
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./data/vector_db")
    
    # CORS
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Externe Dienste
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: Optional[int] = int(os.getenv("SMTP_PORT", "0")) or None
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")

# Einstellungen instanziieren
settings = Settings()