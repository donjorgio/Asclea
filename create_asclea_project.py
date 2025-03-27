#!/usr/bin/env python3
import os
import shutil
import json

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")

def create_file(path, content=""):
    with open(path, 'w') as f:
        f.write(content)
    print(f"Created file: {path}")

def setup_project():
    project_root = "asclea"
    create_directory(project_root)
    
    # Backend structure
    backend_root = os.path.join(project_root, "backend")
    create_directory(backend_root)
    
    # Backend app directory
    app_dir = os.path.join(backend_root, "app")
    create_directory(app_dir)
    create_file(os.path.join(app_dir, "__init__.py"))
    create_file(os.path.join(app_dir, "main.py"), """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from app.core.config import settings
from app.api.routes import api_router
from app.llm.service import initialize_llm_service
from app.rag.service import initialize_rag_service

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
""")
    
    # API routes
    api_dir = os.path.join(app_dir, "api")
    create_directory(api_dir)
    create_file(os.path.join(api_dir, "__init__.py"))
    
    routes_dir = os.path.join(api_dir, "routes")
    create_directory(routes_dir)
    create_file(os.path.join(routes_dir, "__init__.py"), """from fastapi import APIRouter
from app.api.routes import auth, chat, users, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(admin.router, prefix="/admin", tags=["Administration"])
""")
    for route in ["auth", "chat", "users", "admin"]:
        create_file(os.path.join(routes_dir, f"{route}.py"), f"""from fastapi import APIRouter

router = APIRouter()

# TODO: Implement {route} routes
""")
    
    # Core directory
    core_dir = os.path.join(app_dir, "core")
    create_directory(core_dir)
    create_file(os.path.join(core_dir, "__init__.py"))
    create_file(os.path.join(core_dir, "config.py"), """from pydantic import BaseModel
import os
from typing import List, Optional

class Settings(BaseModel):
    # API settings
    API_VERSION: str = os.getenv("API_VERSION", "v1")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-key-not-for-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./asclea.db")
    
    # LLM
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./models/llama3-70b-medical.gguf")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
    
    # Vector database
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./data/vector_db")

# Initialize settings
settings = Settings()
""")
    create_file(os.path.join(core_dir, "security.py"), """# Security related functions
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# TODO: Implement security functions
""")
    
    # Database directory
    db_dir = os.path.join(app_dir, "db")
    create_directory(db_dir)
    create_file(os.path.join(db_dir, "__init__.py"))
    create_file(os.path.join(db_dir, "models.py"), """from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# TODO: Define database models
""")
    create_file(os.path.join(db_dir, "session.py"), """from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create database connection
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

# Session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for database access
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""")
    
    # Database CRUD
    crud_dir = os.path.join(db_dir, "crud")
    create_directory(crud_dir)
    create_file(os.path.join(crud_dir, "__init__.py"))
    
    # LLM service
    llm_dir = os.path.join(app_dir, "llm")
    create_directory(llm_dir)
    create_file(os.path.join(llm_dir, "__init__.py"))
    create_file(os.path.join(llm_dir, "service.py"), """# LLM service for ASCLEA
import os
from pathlib import Path
import asyncio
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

# Global LLM model
llm = None

async def initialize_llm_service():
    \"\"\"Initialize the LLM model\"\"\"
    # TODO: Implement LLM initialization
    pass

async def generate_llm_response(prompt: str):
    \"\"\"Generate a response using the LLM model\"\"\"
    # TODO: Implement LLM response generation
    pass
""")
    
    # RAG service
    rag_dir = os.path.join(app_dir, "rag")
    create_directory(rag_dir)
    create_file(os.path.join(rag_dir, "__init__.py"))
    create_file(os.path.join(rag_dir, "service.py"), """# RAG service for ASCLEA
import os
from pathlib import Path
import asyncio
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Global variables
embedding_model = None
vector_index = None
document_lookup = {}

async def initialize_rag_service():
    \"\"\"Initialize the RAG service\"\"\"
    # TODO: Implement RAG initialization
    pass

async def add_text_to_index(text: str, metadata: Dict[str, Any]):
    \"\"\"Add text to the vector index\"\"\"
    # TODO: Implement text indexing
    pass

async def semantic_search(query: str, top_k: int = 5):
    \"\"\"Perform semantic search\"\"\"
    # TODO: Implement semantic search
    pass

async def generate_rag_response(query: str):
    \"\"\"Generate a RAG-based response\"\"\"
    # TODO: Implement RAG response generation
    pass
""")
    
    # Utils
    utils_dir = os.path.join(app_dir, "utils")
    create_directory(utils_dir)
    create_file(os.path.join(utils_dir, "__init__.py"))
    
    # Data directories
    data_dir = os.path.join(backend_root, "data")
    create_directory(data_dir)
    create_directory(os.path.join(data_dir, "sources"))
    create_directory(os.path.join(data_dir, "vector_db"))
    
    # Models directory
    create_directory(os.path.join(backend_root, "models"))
    
    # Tests directory
    create_directory(os.path.join(backend_root, "tests"))
    
    # Backend config files
    create_file(os.path.join(backend_root, ".env.example"), """# API Configuration
API_VERSION=v1
DEBUG=True
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/asclea

# LLM Configuration
MODEL_PATH=/app/models/llama3-70b-medical.gguf
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-mpnet-base-v2

# Vector Database
VECTOR_DB_PATH=/app/data/vector_db
""")
    
    create_file(os.path.join(backend_root, "Dockerfile"), """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""")
    
    create_file(os.path.join(backend_root, "requirements.txt"), """fastapi==0.109.2
uvicorn==0.27.1
pydantic==2.6.1
python-dotenv==1.0.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
langchain==0.1.9
llama-cpp-python==0.2.56
sentence-transformers==2.2.2
faiss-cpu==1.7.4
pymupdf==1.23.7
beautifulsoup4==4.12.2
requests==2.31.0
pandas==2.2.0
python-multipart==0.0.9
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
""")
    
    # Frontend structure
    frontend_root = os.path.join(project_root, "frontend")
    create_directory(frontend_root)
    
    # Web frontend
    web_root = os.path.join(frontend_root, "web")
    create_directory(web_root)
    
    # Web public directory
    web_public = os.path.join(web_root, "public")
    create_directory(web_public)
    create_file(os.path.join(web_public, "index.html"), """<!DOCTYPE html>
<html lang="de">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#2196f3" />
    <meta
      name="description"
      content="ASCLEA - Medical AI Assistant for Doctors"
    />
    <link rel="apple-touch-icon" href="%PUBLIC_URL%/logo192.png" />
    <link rel="manifest" href="%PUBLIC_URL%/manifest.json" />
    <link
      rel="stylesheet"
      href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap"
    />
    <title>ASCLEA</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
""")
    create_file(os.path.join(web_public, "manifest.json"), """{
  "short_name": "ASCLEA",
  "name": "ASCLEA - Medical AI Assistant for Doctors",
  "icons": [
    {
      "src": "favicon.ico",
      "sizes": "64x64 32x32 24x24 16x16",
      "type": "image/x-icon"
    },
    {
      "src": "logo192.png",
      "type": "image/png",
      "sizes": "192x192"
    },
    {
      "src": "logo512.png",
      "type": "image/png",
      "sizes": "512x512"
    }
  ],
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#2196f3",
  "background_color": "#ffffff"
}
""")
    
    # Web src directory
    web_src = os.path.join(web_root, "src")
    create_directory(web_src)
    
    # Web src subdirectories
    web_dirs = {
        "contexts": ["AuthContext.js", "SnackbarContext.js"],
        "guards": ["AuthGuard.js", "AdminGuard.js"],
        "layouts": ["MainLayout.js", "AuthLayout.js"],
        "pages/admin": ["SourcesPage.js"],
        "pages/auth": ["LoginPage.js", "RegisterPage.js"],
        "pages": ["ChatListPage.js", "ChatPage.js", "DashboardPage.js", "NotFoundPage.js", "ProfilePage.js"],
        "services": ["api.js"]
    }
    
    for directory, files in web_dirs.items():
        full_dir = os.path.join(web_src, directory)
        create_directory(full_dir)
        for file in files:
            create_file(os.path.join(full_dir, file), f"// TODO: Implement {file}")
    
    # Web src root files
    create_file(os.path.join(web_src, "App.js"), """import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';

// TODO: Complete App component implementation
function App() {
  return (
    <Routes>
      {/* Routes will be defined here */}
    </Routes>
  );
}

export default App;
""")
    create_file(os.path.join(web_src, "index.js"), """import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import App from './App';
import theme from './theme';
import { AuthProvider } from './contexts/AuthContext';
import { SnackbarProvider } from './contexts/SnackbarContext';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <SnackbarProvider>
          <AuthProvider>
            <App />
          </AuthProvider>
        </SnackbarProvider>
      </ThemeProvider>
    </BrowserRouter>
  </React.StrictMode>
);
""")
    create_file(os.path.join(web_src, "theme.js"), """import { createTheme } from '@mui/material/styles';

// Define theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#2196f3',
    },
    secondary: {
      main: '#4caf50',
    },
  },
  // TODO: Complete theme configuration
});

export default theme;
""")
    create_file(os.path.join(web_src, "reportWebVitals.js"), "// TODO: Implement reportWebVitals")
    
    # Web config files
    create_file(os.path.join(web_root, ".env.example"), """REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_VERSION=0.1.0
""")
    
    create_file(os.path.join(web_root, "package.json"), """{
  "name": "asclea-web",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "@emotion/react": "^11.11.1",
    "@emotion/styled": "^11.11.0",
    "@mui/icons-material": "^5.14.19",
    "@mui/lab": "^5.0.0-alpha.153",
    "@mui/material": "^5.14.19",
    "@testing-library/jest-dom": "^5.17.0",
    "@testing-library/react": "^13.4.0",
    "@testing-library/user-event": "^13.5.0",
    "axios": "^1.6.2",
    "date-fns": "^2.30.0",
    "formik": "^2.4.5",
    "jwt-decode": "^4.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-markdown": "^9.0.1",
    "react-router-dom": "^6.20.0",
    "react-scripts": "5.0.1",
    "recharts": "^2.10.1",
    "web-vitals": "^2.1.4",
    "yup": "^1.3.2"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "proxy": "http://localhost:8000"
}
""")
    
    # Mobile frontend
    mobile_root = os.path.join(frontend_root, "mobile")
    create_directory(mobile_root)
    
    # Mobile platform directories
    create_directory(os.path.join(mobile_root, "android"))
    create_directory(os.path.join(mobile_root, "ios"))
    
    # Mobile src directory
    mobile_src = os.path.join(mobile_root, "src")
    create_directory(mobile_src)
    
    # Mobile src subdirectories
    mobile_dirs = {
        "contexts": ["AuthContext.js", "SnackbarContext.js"],
        "navigation": ["AppNavigator.js", "AuthNavigator.js"],
        "screens/auth": ["LoginScreen.js", "RegisterScreen.js"],
        "screens": ["ChatListScreen.js", "ChatScreen.js", "DashboardScreen.js", "ProfileScreen.js"],
        "services": ["api.js"]
    }
    
    for directory, files in mobile_dirs.items():
        full_dir = os.path.join(mobile_src, directory)
        create_directory(full_dir)
        for file in files:
            create_file(os.path.join(full_dir, file), f"// TODO: Implement {file}")
    
    # Mobile root files
    create_file(os.path.join(mobile_root, "App.js"), """import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Provider as PaperProvider } from 'react-native-paper';

// TODO: Implement App component
const App = () => {
  return (
    <SafeAreaProvider>
      <PaperProvider>
        <NavigationContainer>
          {/* Navigation will be defined here */}
        </NavigationContainer>
      </PaperProvider>
    </SafeAreaProvider>
  );
};

export default App;
""")
    
    create_file(os.path.join(mobile_root, "app.json"), """{
  "name": "AscleaMobile",
  "displayName": "ASCLEA"
}
""")
    
    create_file(os.path.join(mobile_root, ".env.example"), """API_URL=http://192.168.1.100:8000/api
APP_VERSION=0.1.0
""")
    
    create_file(os.path.join(mobile_root, "package.json"), """{
  "name": "asclea-mobile",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "android": "react-native run-android",
    "ios": "react-native run-ios",
    "start": "react-native start",
    "test": "jest",
    "lint": "eslint ."
  },
  "dependencies": {
    "@react-native-async-storage/async-storage": "^1.19.3",
    "@react-navigation/bottom-tabs": "^6.5.9",
    "@react-navigation/native": "^6.1.8",
    "@react-navigation/native-stack": "^6.9.14",
    "axios": "^1.5.1",
    "jwt-decode": "^3.1.2",
    "react": "18.2.0",
    "react-native": "0.72.5",
    "react-native-dotenv": "^3.4.9",
    "react-native-markdown-display": "^7.0.0-alpha.2",
    "react-native-paper": "^5.10.6",
    "react-native-safe-area-context": "^4.7.2",
    "react-native-screens": "^3.25.0",
    "react-native-vector-icons": "^10.0.0"
  },
  "devDependencies": {
    "@babel/core": "^7.20.0",
    "@babel/preset-env": "^7.20.0",
    "@babel/runtime": "^7.20.0",
    "@react-native/eslint-config": "^0.72.2",
    "@react-native/metro-config": "^0.72.11",
    "@tsconfig/react-native": "^3.0.0",
    "@types/react": "^18.0.24",
    "babel-jest": "^29.2.1",
    "eslint": "^8.19.0",
    "jest": "^29.2.1",
    "metro-react-native-babel-preset": "0.76.8",
    "prettier": "^2.4.1",
    "react-test-renderer": "18.2.0"
  },
  "engines": {
    "node": ">=16"
  }
}
""")
    
    # Project root files
    create_file(os.path.join(project_root, "docker-compose.yml"), """version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./backend/data:/app/data
      - ./backend/models:/app/models
    environment:
      - DEBUG=True
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/asclea
      - SECRET_KEY=development-secret-key
    depends_on:
      - db
    networks:
      - asclea-network

  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=asclea
    ports:
      - "5432:5432"
    networks:
      - asclea-network

  web:
    build:
      context: ./frontend/web
    ports:
      - "3000:3000"
    volumes:
      - ./frontend/web:/app
    depends_on:
      - backend
    networks:
      - asclea-network

networks:
  asclea-network:

volumes:
  postgres_data:
""")
    
    create_file(os.path.join(project_root, "README.md"), """# ASCLEA

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
""")

if __name__ == "__main__":
    setup_project()
    print("Project structure for ASCLEA has been created successfully!")
