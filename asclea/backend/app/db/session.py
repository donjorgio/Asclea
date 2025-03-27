# backend/app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Datenbankverbindung erstellen
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

# Sessionmaker für Datenbankzugriff
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency-Injection für Datenbankzugriff
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()