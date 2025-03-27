# backend/app/api/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging
import asyncio

from app.core.security import get_current_user
from app.db.session import get_db
from app.db.models import User, Chat, Message
from app.llm.service import generate_llm_response, get_medical_reasoning
from app.rag.service import generate_rag_response

logger = logging.getLogger(__name__)

router = APIRouter()

# Request und Response Models
class MessageCreate(BaseModel):
    content: str = Field(..., description="Inhalt der Nachricht")
    
class PatientInfoModel(BaseModel):
    age: Optional[int] = Field(None, description="Alter des Patienten")
    gender: Optional[str] = Field(None, description="Geschlecht des Patienten")
    symptoms: Optional[List[str]] = Field(None, description="Liste der Symptome")
    medical_history: Optional[List[str]] = Field(None, description="Vorerkrankungen")
    medications: Optional[List[str]] = Field(None, description="Aktuelle Medikation")
    vitals: Optional[Dict[str, Any]] = Field(None, description="Vitalparameter")
    travel_history: Optional[List[str]] = Field(None, description="Reiseanamnese")
    
class MedicalQueryModel(BaseModel):
    query: str = Field(..., description="Medizinische Anfrage")
    patient_info: Optional[PatientInfoModel] = Field(None, description="Patienteninformationen")
    use_rag: bool = Field(True, description="RAG-System verwenden")
    temperature: float = Field(0.1, description="Kreativität der Antwort (0.0-1.0)")
    
class SourceInfo(BaseModel):
    title: str
    type: str
    relevance: float
    
class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: str
    sources: Optional[List[SourceInfo]] = None
    confidence: Optional[float] = None
    
class ChatModel(BaseModel):
    id: int
    title: str
    created_at: str
    updated_at: str
    
class ChatListResponse(BaseModel):
    chats: List[ChatModel]
    
class ChatDetailResponse(BaseModel):
    chat: ChatModel
    messages: List[MessageResponse]

@router.post("/query", response_model=Dict[str, Any])
async def medical_query(
    query: MedicalQueryModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Stellt eine medizinische Anfrage ohne einen Chat zu erstellen
    """
    try:
        if query.use_rag:
            # RAG-basierte Antwort generieren
            response = await generate_rag_response(
                query=query.query,
                patient_info=query.patient_info.dict() if query.patient_info else None,
                temperature=query.temperature
            )
            return {
                "answer": response["answer"],
                "sources": response["sources"],
                "tokens_used": response["tokens_used"]
            }
        else:
            # Direkte LLM-Antwort generieren
            if query.patient_info:
                # Medizinische Einschätzung mit Patienteninformationen
                response = await get_medical_reasoning(
                    patient_info=query.patient_info.dict(),
                    medical_context=query.query,
                    temperature=query.temperature
                )
                return {
                    "answer": response["assessment"],
                    "confidence": response["confidence"],
                    "tokens_used": response["tokens_used"]
                }
            else:
                # Einfache Antwort ohne Patientenkontext
                prompt = f"""<s>
Du bist MEDICUS, ein spezialisierter medizinischer KI-Assistent für Ärzte.
Beantworte die folgende medizinische Frage präzise und evidenzbasiert.
Antworte auf Deutsch und in einem professionellen, sachlichen Stil für medizinisches Fachpersonal.
</s>

<QUERY>
{query.query}
</QUERY>

<ANSWER>
"""
                response = await generate_llm_response(
                    prompt=prompt,
                    temperature=query.temperature
                )
                return {
                    "answer": response["text"],
                    "tokens_used": response["total_tokens"]
                }
    except Exception as e:
        logger.error(f"Fehler bei der medizinischen Anfrage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ein Fehler ist bei der Verarbeitung Ihrer Anfrage aufgetreten."
        )

@router.get("/", response_model=ChatListResponse)
async def list_chats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Liste aller Chats des Benutzers
    """
    chats = db.query(Chat).filter(Chat.user_id == current_user.id).order_by(Chat.updated_at.desc()).all()
    
    return {
        "chats": [
            {
                "id": chat.id,
                "title": chat.title,
                "created_at": chat.created_at.isoformat(),
                "updated_at": chat.updated_at.isoformat() if chat.updated_at else chat.created_at.isoformat()
            }
            for chat in chats
        ]
    }

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ChatModel)
async def create_chat(
    title: str = "Neuer medizinischer Chat",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Erstellt einen neuen Chat
    """
    chat = Chat(
        user_id=current_user.id,
        title=title
    )
    
    db.add(chat)
    db.commit()
    db.refresh(chat)
    
    return {
        "id": chat.id,
        "title": chat.title,
        "created_at": chat.created_at.isoformat(),
        "updated_at": chat.updated_at.isoformat() if chat.updated_at else chat.created_at.isoformat()
    }

@router.get("/{chat_id}", response_model=ChatDetailResponse)
async def get_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ruft einen Chat mit allen Nachrichten ab
    """
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat nicht gefunden"
        )
    
    messages = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at).all()
    
    return {
        "chat": {
            "id": chat.id,
            "title": chat.title,
            "created_at": chat.created_at.isoformat(),
            "updated_at": chat.updated_at.isoformat() if chat.updated_at else chat.created_at.isoformat()
        },
        "messages": [
            {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
                "sources": message.sources,
                "confidence": message.confidence
            }
            for message in messages
        ]
    }

@router.post("/{chat_id}/messages", response_model=MessageResponse)
async def add_message(
    chat_id: int,
    message: MessageCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fügt eine Nachricht zum Chat hinzu und generiert eine Antwort
    """
    # Chat überprüfen
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat nicht gefunden"
        )
    
    # Benutzernachricht speichern
    user_message = Message(
        chat_id=chat_id,
        role="user",
        content=message.content
    )
    
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    # Chat-Titel aktualisieren, falls es die erste Nachricht ist
    if chat.title == "Neuer medizinischer Chat":
        # Titel aus der ersten Nachricht ableiten
        title = message.content[:50] + "..." if len(message.content) > 50 else message.content
        chat.title = title
        db.commit()
    
    # Assistentennachricht in der Datenbank anlegen (wird später aktualisiert)
    assistant_message = Message(
        chat_id=chat_id,
        role="assistant",
        content="Ihre Anfrage wird verarbeitet..."
    )
    
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)
    
    # Antwort im Hintergrund generieren
    background_tasks.add_task(
        process_assistant_response,
        chat_id=chat_id,
        message_id=assistant_message.id,
        user_message=message.content,
        db_session=db
    )
    
    return {
        "id": user_message.id,
        "role": user_message.role,
        "content": user_message.content,
        "created_at": user_message.created_at.isoformat(),
        "sources": None,
        "confidence": None
    }

async def process_assistant_response(
    chat_id: int,
    message_id: int,
    user_message: str,
    db_session: Session
):
    """
    Verarbeitet die Antwort des Assistenten im Hintergrund
    """
    try:
        # Vorherige Nachrichten abrufen, um Kontext zu erhalten
        previous_messages = db_session.query(Message).filter(
            Message.chat_id == chat_id,
            Message.id < message_id
        ).order_by(Message.created_at).all()
        
        # Kontext aus den vorherigen Nachrichten erstellen
        conversation_history = "\n".join([
            f"{'Arzt' if msg.role == 'user' else 'MEDICUS'}: {msg.content}"
            for msg in previous_messages[-5:]  # Nur die letzten 5 Nachrichten für Kontext
        ])
        
        # RAG-basierte Antwort generieren
        response = await generate_rag_response(
            query=user_message,
            patient_info=None,  # Könnte in Zukunft aus dem Chatverlauf extrahiert werden
            temperature=0.1
        )
        
        # Assistentennachricht aktualisieren
        message = db_session.query(Message).filter(Message.id == message_id).first()
        if message:
            message.content = response["answer"]
            message.sources = response["sources"]
            
            db_session.commit()
            logger.info(f"Assistentenantwort für Nachricht {message_id} generiert")
        else:
            logger.error(f"Nachricht {message_id} nicht gefunden")
            
    except Exception as e:
        logger.error(f"Fehler bei der Generierung der Assistentenantwort: {str(e)}")
        
        # Fehlermeldung in der Nachricht speichern
        message = db_session.query(Message).filter(Message.id == message_id).first()
        if message:
            message.content = "Es ist ein Fehler bei der Verarbeitung Ihrer Anfrage aufgetreten. Bitte versuchen Sie es erneut."
            db_session.commit()

@router.put("/{chat_id}", response_model=ChatModel)
async def update_chat(
    chat_id: int,
    title: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Aktualisiert den Titel eines Chats
    """
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat nicht gefunden"
        )
    
    chat.title = title
    db.commit()
    db.refresh(chat)
    
    return {
        "id": chat.id,
        "title": chat.title,
        "created_at": chat.created_at.isoformat(),
        "updated_at": chat.updated_at.isoformat() if chat.updated_at else chat.created_at.isoformat()
    }

@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Löscht einen Chat und alle zugehörigen Nachrichten
    """
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat nicht gefunden"
        )
    
    # Alle Nachrichten löschen
    db.query(Message).filter(Message.chat_id == chat_id).delete()
    
    # Chat löschen
    db.delete(chat)
    db.commit()
    
    return None
