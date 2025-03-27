# ASCLEA

## Medical AI Assistant for Doctors

ASCLEA is an intelligent system that leverages Llama 3 70B and Retrieval-Augmented Generation (RAG) to provide evidence-based medical assistance to doctors.

## Project Structure

- `backend/`: FastAPI backend with LLM and RAG integration
- `frontend/web/`: React web application
- `frontend/mobile/`: React Native mobile application for iOS and Android

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.10+
- Node.js 16+
- React Native environment (for mobile development)

### Installation

1. Clone the repository
2. Copy example environment files:"
cp backend/.env.example backend/.env
cp frontend/web/.env.example frontend/web/.env
cp frontend/mobile/.env.example frontend/mobile/.env"
3. Start the development environment:"
docker-compose up
## Features

- Medical question answering with evidence-based sources
- Chat interface for extended medical consultations
- Patient case analysis
- Mobile access for doctors on the go

## Development

### Backend
cd backend
pip install -r requirements.txt
uvicorn app.main --reload
### Web Frontend
cd frontend/web
npm install
npm start
### Mobile App
cd frontend/mobile
npm install
npx react-native run-ios  # or run-android
## License

[License information here]


# MEDICUS - Systemarchitektur und Implementierungsplan

## Systemkomponenten

1. **Backend-Services**
   - RAG-Engine (Retrieval-Augmented Generation)
   - LLM-Integration (Llama 3 70B)
   - Medizinische Wissensdatenbank
   - API-Gateway
   - Authentifizierung und Autorisierung
   - Logging und Monitoring

2. **Frontend-Anwendungen**
   - Web-App (Responsive für Desktop/Tablet)
   - Mobile App (iOS/Android)
   - Admin-Portal

3. **Datenquellen**
   - Leitlinien-Datenbank
   - Medikamenten-Interaktionsdatenbank
   - Medizinische Fachartikel und Lehrbücher
   - Strukturierte medizinische Ontologien

## Implementierungsplan

### Phase 1: Core Backend Setup

1. **Python-Backend mit FastAPI**
   - Basisstruktur
   - API-Endpunkte
   - Authentifizierung

2. **Llama 3 70B Integration**
   - Modell-Download und Setup
   - Inferenz-API
   - Prompt-Engineering

3. **RAG-System**
   - Vektorisierung der Wissensbasis
   - Retrieval-Mechanismen
   - Antwortgenerierung

### Phase 2: Frontend-Entwicklung

1. **Web-App mit React**
   - Authentifizierung
   - Chat-Interface
   - Ergebnisdarstellung
   - Responsive Design

2. **Mobile App mit React Native**
   - iOS und Android Unterstützung
   - Offline-Funktionalität
   - Push-Benachrichtigungen

### Phase 3: Fachspezifische Erweiterungen

1. **Medizinische Wissensdatenbank**
   - Import von Leitlinien
   - Strukturierung der Inhalte
   - Regelmäßige Updates

2. **Spezialisierte Features**
   - Diagnoseassistent
   - Medikamenteninteraktionen
   - Exportfunktionen für Dokumentation

## Dateien-Struktur

```
medicus/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── llm/
│   │   ├── rag/
│   │   └── utils/
│   ├── data/
│   ├── models/
│   └── tests/
├── frontend/
│   ├── web/
│   └── mobile/
└── docs/
```

Im Folgenden werde ich den Code für jede Komponente detailliert darstellen.