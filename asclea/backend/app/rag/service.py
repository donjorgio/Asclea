import os
from pathlib import Path
import asyncio
from typing import Dict, List, Any, Optional, Tuple
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import json
import logging
from datetime import datetime
from app.core.config import settings
from app.db.session import get_db
from app.db.models import MedicalSource
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import pandas as pd

logger = logging.getLogger(__name__)

# Globale Variablen
embedding_model = None
vector_index = None
document_lookup = {}  # Speichert Dokument-IDs und ihre Metadaten

async def initialize_rag_service():
    """Initialisiert den RAG-Service"""
    global embedding_model, vector_index, document_lookup
    
    # Embedding-Modell laden
    try:
        loop = asyncio.get_event_loop()
        embedding_model = await loop.run_in_executor(
            None,
            lambda: SentenceTransformer(settings.EMBEDDING_MODEL)
        )
        logger.info(f"Embedding-Modell geladen: {settings.EMBEDDING_MODEL}")
    except Exception as e:
        logger.error(f"Fehler beim Laden des Embedding-Modells: {str(e)}")
        raise
    
    # Vektorindex laden oder erstellen
    vector_db_path = Path(settings.VECTOR_DB_PATH)
    index_file = vector_db_path / "faiss_index.bin"
    lookup_file = vector_db_path / "document_lookup.json"
    
    if index_file.exists() and lookup_file.exists():
        try:
            # Vorhandenen Index laden
            vector_index = faiss.read_index(str(index_file))
            
            # Dokument-Lookup laden
            with open(lookup_file, 'r', encoding='utf-8') as f:
                document_lookup = json.load(f)
                
            logger.info(f"Vektorindex geladen: {len(document_lookup)} Dokumente")
        except Exception as e:
            logger.error(f"Fehler beim Laden des Vektorindex: {str(e)}")
            # Fallback: Erstelle einen neuen Index wenn der Ladevorgang fehlschlägt
            dimension = embedding_model.get_sentence_embedding_dimension()
            vector_index = faiss.IndexFlatL2(dimension)
            document_lookup = {}
            logger.warning(f"Fallback: Neuer Vektorindex erstellt mit Dimension {dimension}")
    else:
        # Verzeichnis erstellen, falls es nicht existiert
        vector_db_path.mkdir(parents=True, exist_ok=True)
        
        # Neuen Index erstellen (leer)
        dimension = embedding_model.get_sentence_embedding_dimension()
        vector_index = faiss.IndexFlatL2(dimension)
        document_lookup = {}
        
        # Index und Lookup speichern
        faiss.write_index(vector_index, str(index_file))
        with open(lookup_file, 'w', encoding='utf-8') as f:
            json.dump(document_lookup, f)
            
        logger.info(f"Neuer Vektorindex erstellt mit Dimension {dimension}")

async def process_document(source_id: int, db_session):
    """
    Verarbeitet ein medizinisches Dokument und fügt es zum Vektorindex hinzu
    
    Args:
        source_id: ID des Dokuments in der Datenbank
        db_session: Datenbankverbindung
    """
    global embedding_model, vector_index, document_lookup
    
    # Dokument aus der Datenbank laden
    source = db_session.query(MedicalSource).filter(MedicalSource.id == source_id).first()
    if not source:
        logger.error(f"Dokument mit ID {source_id} nicht gefunden")
        return
    
    # Überprüfen, ob das Dokument bereits indiziert wurde
    if source.indexed:
        logger.info(f"Dokument {source.title} bereits indiziert")
        return
    
    # Text aus dem Dokument extrahieren
    try:
        from datetime import datetime
        
        text_chunks = []
        local_path = source.local_path
        file_extension = os.path.splitext(local_path)[1].lower()
        
        if file_extension == '.pdf':
            # PDF-Dokument verarbeiten
            doc = fitz.open(local_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text.strip():  # Leere Seiten überspringen
                    text_chunks.append({
                        "text": text,
                        "metadata": {
                            "source_id": source_id,
                            "source_title": source.title,
                            "source_type": source.source_type,
                            "page": page_num + 1
                        }
                    })
        elif file_extension in ['.html', '.htm']:
            # HTML-Dokument verarbeiten
            with open(local_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Text aus verschiedenen relevanten Tags extrahieren
            for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li']):
                text = element.get_text(strip=True)
                if text:
                    text_chunks.append({
                        "text": text,
                        "metadata": {
                            "source_id": source_id,
                            "source_title": source.title,
                            "source_type": source.source_type,
                            "element": element.name
                        }
                    })
        elif file_extension in ['.txt', '.md']:
            # Textdokument verarbeiten
            with open(local_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Text in Absätze aufteilen
            paragraphs = text.split('\n\n')
            for i, paragraph in enumerate(paragraphs):
                if paragraph.strip():
                    text_chunks.append({
                        "text": paragraph,
                        "metadata": {
                            "source_id": source_id,
                            "source_title": source.title,
                            "source_type": source.source_type,
                            "paragraph": i + 1
                        }
                    })
        elif file_extension in ['.csv', '.xlsx', '.xls']:
            # Tabellendokument verarbeiten
            if file_extension == '.csv':
                df = pd.read_csv(local_path)
            else:
                df = pd.read_excel(local_path)
            
            # Für jede Zeile einen Chunk erstellen
            for i, row in df.iterrows():
                row_text = " | ".join([f"{col}: {val}" for col, val in row.items()])
                text_chunks.append({
                    "text": row_text,
                    "metadata": {
                        "source_id": source_id,
                        "source_title": source.title,
                        "source_type": source.source_type,
                        "row": i + 1
                    }
                })
        else:
            logger.warning(f"Nicht unterstütztes Dateiformat: {file_extension}")
            return
        
        # Embeddings für jeden Chunk erzeugen und zum Index hinzufügen
        for chunk in text_chunks:
            await add_text_to_index(chunk["text"], chunk["metadata"])
        
        # Dokument als indiziert markieren
        source.indexed = True
        source.index_date = datetime.utcnow()
        db_session.commit()
        
        logger.info(f"Dokument {source.title} erfolgreich indiziert: {len(text_chunks)} Chunks")
    except Exception as e:
        logger.error(f"Fehler beim Verarbeiten des Dokuments {source.title}: {str(e)}")
        raise

async def add_text_to_index(text: str, metadata: Dict[str, Any]):
    """
    Fügt einen Textabschnitt zum Vektorindex hinzu
    
    Args:
        text: Der zu indizierende Text
        metadata: Metadaten zum Text (Quelle, Seitenzahl, etc.)
    """
    global embedding_model, vector_index, document_lookup
    
    if not text.strip():
        return
    
    # Embedding erzeugen
    try:
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None,
            lambda: embedding_model.encode([text])[0]
        )
    except Exception as e:
        logger.error(f"Fehler beim Erzeugen des Embeddings: {str(e)}")
        return
    
    # Zum Index hinzufügen
    vector_index.add(np.array([embedding], dtype=np.float32))
    
    # Dokument-ID ist der Index des hinzugefügten Vektors
    doc_id = vector_index.ntotal - 1
    
    # Metadaten speichern
    document_lookup[str(doc_id)] = {
        "text": text,
        "metadata": metadata
    }
    
    # Index und Lookup speichern
    if doc_id % 100 == 0:  # Regelmäßig speichern, um Datenverlust zu vermeiden
        await save_index()

async def save_index():
    """Speichert den Vektorindex und das Dokument-Lookup"""
    vector_db_path = Path(settings.VECTOR_DB_PATH)
    index_file = vector_db_path / "faiss_index.bin"
    lookup_file = vector_db_path / "document_lookup.json"
    
    try:
        # Index speichern
        faiss.write_index(vector_index, str(index_file))
        
        # Lookup speichern
        with open(lookup_file, 'w', encoding='utf-8') as f:
            json.dump(document_lookup, f)
            
        logger.info(f"Vektorindex gespeichert: {vector_index.ntotal} Dokumente")
    except Exception as e:
        logger.error(f"Fehler beim Speichern des Vektorindex: {str(e)}")

async def semantic_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Führt eine semantische Suche durch
    
    Args:
        query: Suchanfrage
        top_k: Anzahl der zurückzugebenden Ergebnisse
        
    Returns:
        Liste der relevantesten Dokumente mit Metadaten
    """
    global embedding_model, vector_index, document_lookup
    
    if vector_index.ntotal == 0:
        logger.warning("Vektorindex ist leer")
        return []
    
    try:
        # Embedding für die Anfrage erzeugen
        loop = asyncio.get_event_loop()
        query_embedding = await loop.run_in_executor(
            None,
            lambda: embedding_model.encode([query])[0]
        )
        
        # Ähnlichkeitssuche durchführen
        D, I = vector_index.search(np.array([query_embedding], dtype=np.float32), top_k)
        
        # Ergebnisse zusammenstellen
        results = []
        for i, (distance, idx) in enumerate(zip(D[0], I[0])):
            if idx != -1:  # -1 bedeutet, kein Ergebnis gefunden
                doc_id = str(idx)
                if doc_id in document_lookup:
                    doc = document_lookup[doc_id]
                    results.append({
                        "text": doc["text"],
                        "metadata": doc["metadata"],
                        "score": float(1.0 / (1.0 + distance))  # Ähnlichkeitsscore (0-1)
                    })
        
        return results
    except Exception as e:
        logger.error(f"Fehler bei der semantischen Suche: {str(e)}")
        return []

async def generate_rag_response(
    query: str,
    patient_info: Optional[Dict[str, Any]] = None,
    temperature: float = 0.1
) -> Dict[str, Any]:
    """
    Generiert eine RAG-basierte Antwort
    
    Args:
        query: Die Anfrage des Benutzers
        patient_info: Optionale strukturierte Patienteninformationen
        temperature: Kreativität der Antwort
        
    Returns:
        Dict mit der generierten Antwort und Quellen
    """
    from app.llm.service import generate_llm_response
    
    # Semantische Suche durchführen
    relevant_docs = await semantic_search(query, top_k=7)
    
    if not relevant_docs:
        logger.warning("Keine relevanten Dokumente gefunden für die Anfrage")
    
    # Kontext aus den relevanten Dokumenten erstellen
    context = ""
    sources = []
    
    for doc in relevant_docs:
        context += f"Information: {doc['text']}\n\n"
        sources.append({
            "title": doc["metadata"].get("source_title", "Unbekannte Quelle"),
            "type": doc["metadata"].get("source_type", "Unbekannt"),
            "relevance": doc["score"]
        })
    
    # Prompt für LLM erstellen
    prompt = create_rag_prompt(query, context, patient_info)
    
    # LLM-Antwort generieren
    llm_response = await generate_llm_response(
        prompt=prompt,
        temperature=temperature,
        max_tokens=2048
    )
    
    return {
        "answer": llm_response["text"],
        "sources": sources,
        "tokens_used": llm_response["total_tokens"]
    }

def create_rag_prompt(
    query: str,
    context: str,
    patient_info: Optional[Dict[str, Any]] = None
) -> str:
    """Erstellt einen Prompt für die RAG-Antwortgenerierung"""
    # Patienten-Kontext formatieren, falls vorhanden
    patient_context = ""
    if patient_info:
        age = patient_info.get("age", "Unbekannt")
        gender = patient_info.get("gender", "Unbekannt")
        symptoms = patient_info.get("symptoms", [])
        
        patient_context = f"""
<PATIENT_CONTEXT>
Alter: {age}
Geschlecht: {gender}
Beschwerden/Symptome: {', '.join(symptoms) if symptoms else 'Keine angegeben'}
</PATIENT_CONTEXT>
"""
    
    # RAG-Prompt
    prompt = f"""<s>
Du bist ASCLEA, ein spezialisierter medizinischer KI-Assistent für Ärzte.
Nutze die folgenden Informationen, um eine präzise, evidenzbasierte Antwort zu geben.
Wenn die Informationen nicht ausreichen, sage das ehrlich und gib an, welche weiteren Informationen hilfreich wären.
Antworte auf Deutsch und in einem professionellen, sachlichen Stil für medizinisches Fachpersonal.
</s>

<QUERY>
{query}
</QUERY>

{patient_context if patient_context else ""}

<RETRIEVED_CONTEXT>
{context}
</RETRIEVED_CONTEXT>

<INSTRUCTIONS>
1. Berücksichtige alle relevanten Informationen aus dem bereitgestellten Kontext.
2. Halte dich an aktuelle medizinische Leitlinien und Standards.
3. Gib klare, strukturierte Antworten mit Differentialdiagnosen, wenn angebracht.
4. Sei präzise bei Dosierungen, Therapieempfehlungen und diagnostischen Kriterien.
5. Zeige Unsicherheiten transparent auf, wenn die Evidenzlage nicht eindeutig ist.
</INSTRUCTIONS>

<ANSWER>
"""
    
    return prompt