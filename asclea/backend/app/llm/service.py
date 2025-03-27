import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import asyncio
from llama_cpp import Llama
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Globale Variable für das LLM-Modell
llm = None

async def initialize_llm_service():
    """Initialisiert das LLM-Modell"""
    global llm
    
    model_path = settings.MODEL_PATH
    
    # Überprüfen, ob das Modell existiert
    if not Path(model_path).exists():
        logger.error(f"Modell nicht gefunden: {model_path}")
        raise FileNotFoundError(f"Modell nicht gefunden: {model_path}")
    
    try:
        # Llama initialisieren - in einem separaten Thread, da es rechenintensiv ist
        loop = asyncio.get_event_loop()
        llm = await loop.run_in_executor(
            None, 
            lambda: Llama(
                model_path=model_path,
                n_ctx=4096,  # Kontextfenster
                n_gpu_layers=-1,  # -1 bedeutet, alle Schichten auf der GPU, wenn möglich
                n_threads=os.cpu_count(),  # Anzahl der CPU-Threads
                seed=42,  # Für Reproduzierbarkeit
                verbose=False
            )
        )
        logger.info(f"LLM-Modell erfolgreich geladen: {model_path}")
    except Exception as e:
        logger.error(f"Fehler beim Laden des LLM-Modells: {str(e)}")
        raise

async def generate_llm_response(
    prompt: str,
    temperature: float = 0.1,
    max_tokens: int = 2048,
    stop_sequences: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generiert eine Antwort mit dem LLM-Modell
    
    Args:
        prompt: Der Eingabetext für das Modell
        temperature: Kreativität der Antwort (0.0 bis 1.0)
        max_tokens: Maximale Länge der generierten Antwort
        stop_sequences: Liste von Zeichenketten, bei denen die Generierung stoppt
        
    Returns:
        Dict mit dem generierten Text und Metadaten
    """
    global llm
    
    if llm is None:
        logger.error("LLM-Modell ist nicht initialisiert")
        raise RuntimeError("LLM-Modell ist nicht initialisiert")
    
    try:
        # Antwort in einem separaten Thread generieren
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: llm.create_completion(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop_sequences,
                echo=False,
                stream=False
            )
        )
        
        # Antwort parsen
        generated_text = response['choices'][0]['text']
        
        return {
            "text": generated_text.strip(),
            "finish_reason": response['choices'][0]['finish_reason'],
            "prompt_tokens": response['usage']['prompt_tokens'],
            "completion_tokens": response['usage']['completion_tokens'],
            "total_tokens": response['usage']['total_tokens']
        }
    except Exception as e:
        logger.error(f"Fehler bei der LLM-Generierung: {str(e)}")
        raise

async def get_medical_reasoning(
    patient_info: Dict[str, Any],
    medical_context: Optional[str] = None,
    temperature: float = 0.1
) -> Dict[str, Any]:
    """
    Generiert eine medizinische Einschätzung basierend auf Patienteninformationen
    
    Args:
        patient_info: Strukturierte Patienteninformationen
        medical_context: Zusätzlicher medizinischer Kontext
        temperature: Kreativität der Antwort
        
    Returns:
        Dict mit der medizinischen Einschätzung
    """
    # Prompt erstellen
    prompt = create_medical_reasoning_prompt(patient_info, medical_context)
    
    # Antwort generieren
    response = await generate_llm_response(
        prompt=prompt,
        temperature=temperature,
        max_tokens=3072,
        stop_sequences=["</ASSESSMENT>"]
    )
    
    # Antwort strukturieren
    return {
        "assessment": response["text"],
        "confidence": estimate_confidence(response["text"]),
        "tokens_used": response["total_tokens"]
    }

def create_medical_reasoning_prompt(
    patient_info: Dict[str, Any],
    medical_context: Optional[str] = None
) -> str:
    """Erstellt einen strukturierten Prompt für die medizinische Einschätzung"""
    # Basisinformationen extrahieren
    age = patient_info.get("age", "Unbekannt")
    gender = patient_info.get("gender", "Unbekannt")
    symptoms = patient_info.get("symptoms", [])
    medical_history = patient_info.get("medical_history", [])
    medications = patient_info.get("medications", [])
    vitals = patient_info.get("vitals", {})
    
    # Strukturierter Prompt
    prompt = f"""<SYSTEM>
Du bist ASCLEA, ein spezialisierter medizinischer KI-Assistent für Ärzte.
Deine Aufgabe ist es, eine strukturierte Differentialdiagnose zu erstellen und Handlungsempfehlungen zu geben.
Antworte auf Deutsch und bleibe faktisch korrekt und evidenzbasiert.
Achte besonders auf Warnzeichen und potentiell lebensbedrohliche Zustände.
</SYSTEM>

<PATIENT_INFORMATION>
Alter: {age}
Geschlecht: {gender}

Beschwerden/Symptome:
{', '.join(symptoms) if symptoms else 'Keine angegeben'}

Vorerkrankungen:
{', '.join(medical_history) if medical_history else 'Keine angegeben'}

Aktuelle Medikation:
{', '.join(medications) if medications else 'Keine angegeben'}

Vitalparameter:
{', '.join([f"{k}: {v}" for k, v in vitals.items()]) if vitals else 'Keine angegeben'}
</PATIENT_INFORMATION>
"""

    # Den problematischen Teil separat behandeln
    if medical_context:
        prompt += f"<ADDITIONAL_CONTEXT>\n{medical_context}\n</ADDITIONAL_CONTEXT>"
    
    prompt += """
<TASK>
1. Erstelle eine priorisierte Liste möglicher Differentialdiagnosen.
2. Gib eine Einschätzung der Dringlichkeit.
3. Empfehle weitere diagnostische Maßnahmen.
4. Schlage therapeutische Optionen vor, falls relevant.
5. Nenne wichtige Warnzeichen, auf die geachtet werden sollte.
</TASK>

<ASSESSMENT>
"""
    
    return prompt

def estimate_confidence(text: str) -> float:
    """
    Schätzt die Konfidenz der Antwort basierend auf Heuristiken
    
    Diese Funktion könnte in der Zukunft durch ein Modell ersetzt werden,
    das die Konfidenz anhand des Textes schätzt.
    """
    # Einfache Heuristik: Länge und Präsenz von Unsicherheitsmarkern
    uncertainty_markers = [
        "unklar", "unsicher", "möglicherweise", "eventuell", "könnte",
        "vielleicht", "nicht sicher", "fraglich", "differentialdiagnostisch",
        "zu erwägen", "nicht auszuschließen"
    ]
    
    # Zählen der Unsicherheitsmarker
    uncertainty_count = sum(1 for marker in uncertainty_markers if marker.lower() in text.lower())
    
    # Länge des Textes (mehr Text = mehr Informationen = höhere Konfidenz)
    length_factor = min(1.0, len(text) / 2000)
    
    # Konfidenz berechnen (zwischen 0.0 und 1.0)
    # Mehr Unsicherheitsmarker = geringere Konfidenz
    uncertainty_factor = max(0.0, 1.0 - (uncertainty_count * 0.05))
    
    # Gewichtete Kombination
    confidence = 0.7 * uncertainty_factor + 0.3 * length_factor
    
    return round(confidence, 2)