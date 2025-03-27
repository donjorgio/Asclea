# backend/app/api/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import logging
import os
from datetime import datetime
import shutil

from app.core.security import get_current_user
from app.db.session import get_db
from app.db.models import User, MedicalSource
from app.rag.service import process_document

logger = logging.getLogger(__name__)

router = APIRouter()

# Models
class SourceResponse(BaseModel):
    id: int
    title: str
    source_type: str
    publisher: Optional[str]
    publication_date: Optional[str]
    indexed: bool
    index_date: Optional[str]
    created_at: str

class SourceListResponse(BaseModel):
    sources: List[SourceResponse]

@router.get("/sources", response_model=SourceListResponse)
async def list_sources(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Liste aller medizinischen Quellen (nur für Administratoren)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nur Administratoren können auf diese Ressource zugreifen"
        )
    
    sources = db.query(MedicalSource).order_by(MedicalSource.created_at.desc()).all()
    
    return {
        "sources": [
            {
                "id": source.id,
                "title": source.title,
                "source_type": source.source_type,
                "publisher": source.publisher,
                "publication_date": source.publication_date.isoformat() if source.publication_date else None,
                "indexed": source.indexed,
                "index_date": source.index_date.isoformat() if source.index_date else None,
                "created_at": source.created_at.isoformat()
            }
            for source in sources
        ]
    }

@router.post("/sources", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def upload_source(
    title: str,
    source_type: str,
    publisher: Optional[str] = None,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lädt eine neue medizinische Quelle hoch (nur für Administratoren)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nur Administratoren können auf diese Ressource zugreifen"
        )
    
    # Datei speichern
    upload_dir = os.path.join("data", "sources")
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Datei: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fehler beim Speichern der Datei"
        )
    
    # Quelle in der Datenbank speichern
    new_source = MedicalSource(
        title=title,
        source_type=source_type,
        publisher=publisher,
        publication_date=datetime.now(),
        local_path=file_path,
        indexed=False
    )
    
    db.add(new_source)
    db.commit()
    db.refresh(new_source)
    
    return {
        "id": new_source.id,
        "title": new_source.title,
        "source_type": new_source.source_type,
        "publisher": new_source.publisher,
        "publication_date": new_source.publication_date.isoformat() if new_source.publication_date else None,
        "indexed": new_source.indexed,
        "index_date": new_source.index_date.isoformat() if new_source.index_date else None,
        "created_at": new_source.created_at.isoformat()
    }

@router.post("/sources/{source_id}/index", response_model=SourceResponse)
async def index_source(
    source_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Indiziert eine medizinische Quelle für die Vektorsuche (nur für Administratoren)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nur Administratoren können auf diese Ressource zugreifen"
        )
    
    # Quelle aus der Datenbank laden
    source = db.query(MedicalSource).filter(MedicalSource.id == source_id).first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quelle nicht gefunden"
        )
    
    # Quelle indizieren
    try:
        await process_document(source_id, db)
    except Exception as e:
        logger.error(f"Fehler beim Indizieren der Quelle: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Indizieren der Quelle: {str(e)}"
        )
    
    # Aktualisierte Quelle zurückgeben
    db.refresh(source)
    
    return {
        "id": source.id,
        "title": source.title,
        "source_type": source.source_type,
        "publisher": source.publisher,
        "publication_date": source.publication_date.isoformat() if source.publication_date else None,
        "indexed": source.indexed,
        "index_date": source.index_date.isoformat() if source.index_date else None,
        "created_at": source.created_at.isoformat()
    }

@router.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    source_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Löscht eine medizinische Quelle (nur für Administratoren)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nur Administratoren können auf diese Ressource zugreifen"
        )
    
    # Quelle aus der Datenbank laden
    source = db.query(MedicalSource).filter(MedicalSource.id == source_id).first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quelle nicht gefunden"
        )
    
    # Datei löschen
    if source.local_path and os.path.exists(source.local_path):
        try:
            os.remove(source.local_path)
        except Exception as e:
            logger.error(f"Fehler beim Löschen der Datei: {str(e)}")
    
    # Quelle aus der Datenbank löschen
    db.delete(source)
    db.commit()
    
    return None