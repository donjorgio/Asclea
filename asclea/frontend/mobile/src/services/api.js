import axios from 'axios';
import Config from 'react-native-dotenv';

// Create axios instance
const instance = axios.create({
  baseURL: Config.API_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Function to set auth token in axios headers
const setAuthToken = (token) => {
  if (token) {
    instance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete instance.defaults.headers.common['Authorization'];
  }
};

// API service methods
const api = {
  // Auth
  login: async (email, password) => {
    const response = await instance.post('/auth/token', {
      username: email,
      password: password,
    }, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },
  
  // Users
  getProfile: async () => {
    const response = await instance.get('/users/me');
    return response.data;
  },
  
  updateProfile: async (userData) => {
    const response = await instance.put('/users/me', userData);
    return response.data;
  },
  
  register: async (userData) => {
    const response = await instance.post('/users', userData);
    return response.data;
  },
  
  // Chats
  getChats: async () => {
    const response = await instance.get('/chat');
    return response.data;
  },
  
  getChat: async (chatId) => {
    const response = await instance.get(`/chat/${chatId}`);
    return response.data;
  },
  
  createChat: async (title) => {
    const response = await instance.post('/chat', null, {
      params: { title },
    });
    return response.data;
  },
  
  sendMessage: async (chatId, content) => {
    const response = await instance.post(`/chat/${chatId}/messages`, {
      content,
    });
    return response.data;
  },
  
  deleteChat: async (chatId) => {
    await instance.delete(`/chat/${chatId}`);
    return true;
  },
  
  // Medical query
  medicalQuery: async (query, patientInfo = null, useRag = true) => {
    const response = await instance.post('/chat/query', {
      query,
      patient_info: patientInfo,
      use_rag: useRag,
    });
    return response.data;
  },
  
  // Helper utility
  setAuthToken,
  
  // Expose the axios instance for other requests
  get: instance.get,
  post: instance.post,
  put: instance.put,
  delete: instance.delete,
};

export default api;