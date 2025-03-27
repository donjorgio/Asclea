# backend/app/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel

from app.core.security import create_access_token, verify_password, Token
from app.db.session import get_db
from app.db.models import User
from app.core.config import settings

router = APIRouter()

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

@router.post("/token", response_model=LoginResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2-kompatible Token-Login, gibt ein JWT-Token zurück
    """
    # Benutzer in der Datenbank suchen
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # Authentifizierung überprüfen
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falsche E-Mail oder Passwort",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Überprüfen, ob der Benutzer aktiv ist
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Benutzer ist deaktiviert",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Token erstellen
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_admin": user.is_admin
        }
    }
