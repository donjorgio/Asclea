import axios from 'axios';

// API-Basis-URL
const API_URL = process.env.REACT_APP_API_URL || '/api';

// Chat-Service
export const chatService = {
  // Chat-Liste abrufen
  getChats: async () => {
    const response = await axios.get(`${API_URL}/chat/`);
    return response.data;
  },
  
  // Neuen Chat erstellen
  createChat: async (title = 'Neuer medizinischer Chat') => {
    const response = await axios.post(`${API_URL}/chat/`, null, {
      params: { title }
    });
    return response.data;
  },
  
  // Chat-Details abrufen
  getChat: async (chatId) => {
    const response = await axios.get(`${API_URL}/chat/${chatId}`);
    return response.data;
  },
  
  // Nachricht senden
  sendMessage: async (chatId, message) => {
    const response = await axios.post(`${API_URL}/chat/${chatId}/messages`, {
      content: message
    });
    return response.data;
  },
  
  // Chat löschen
  deleteChat: async (chatId) => {
    await axios.delete(`${API_URL}/chat/${chatId}`);
    return true;
  },
  
  // Chat-Titel aktualisieren
  updateChatTitle: async (chatId, title) => {
    const response = await axios.put(`${API_URL}/chat/${chatId}`, null, {
      params: { title }
    });
    return response.data;
  },
  
  // Direkte medizinische Anfrage (ohne Chat)
  medicalQuery: async (query, patientInfo = null, useRag = true, temperature = 0.1) => {
    const response = await axios.post(`${API_URL}/chat/query`, {
      query,
      patient_info: patientInfo,
      use_rag: useRag,
      temperature
    });
    return response.data;
  }
};

// Quellen-Service (für Administratoren)
export const sourceService = {
  // Quellen abrufen
  getSources: async () => {
    const response = await axios.get(`${API_URL}/admin/sources`);
    return response.data;
  },
  
  // Quelle hochladen
  uploadSource: async (title, sourceType, publisher, file) => {
    const formData = new FormData();
    formData.append('title', title);
    formData.append('source_type', sourceType);
    if (publisher) {
      formData.append('publisher', publisher);
    }
    formData.append('file', file);
    
    const response = await axios.post(`${API_URL}/admin/sources`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },
  
  // Quelle indizieren
  indexSource: async (sourceId) => {
    const response = await axios.post(`${API_URL}/admin/sources/${sourceId}/index`);
    return response.data;
  },
  
  // Quelle löschen
  deleteSource: async (sourceId) => {
    await axios.delete(`${API_URL}/admin/sources/${sourceId}`);
    return true;
  }
};