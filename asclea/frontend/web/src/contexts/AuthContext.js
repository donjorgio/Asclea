import React, { createContext, useContext, useState, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useSnackbar } from './SnackbarContext';

// Kontext erstellen
const AuthContext = createContext();

// Custom Hook für den Zugriff auf den Auth-Kontext
export const useAuth = () => useContext(AuthContext);

// Auth Provider Component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));
  
  const navigate = useNavigate();
  const { showSnackbar } = useSnackbar();
  
  // Beim Start prüfen, ob ein gültiges Token vorhanden ist
  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          // Token validieren
          const decodedToken = jwtDecode(token);
          const currentTime = Date.now() / 1000;
          
          if (decodedToken.exp < currentTime) {
            // Token ist abgelaufen
            logout();
          } else {
            // Token ist gültig, Benutzerinformationen abrufen
            setAuthToken(token);
            try {
              const response = await axios.get('/api/users/me');
              setUser(response.data);
              setIsAuthenticated(true);
            } catch (error) {
              console.error('Fehler beim Abrufen der Benutzerinformationen:', error);
              logout();
            }
          }
        } catch (error) {
          // Token ist ungültig
          console.error('Ungültiges Token:', error);
          logout();
        }
      }
      setIsLoading(false);
    };
    
    initAuth();
  }, [token]);
  
  // Funktion zum Setzen des Auth-Tokens in Axios
  const setAuthToken = (token) => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      localStorage.setItem('token', token);
    } else {
      delete axios.defaults.headers.common['Authorization'];
      localStorage.removeItem('token');
    }
  };
  
  // Login-Funktion
  const login = async (email, password) => {
    try {
      const response = await axios.post('/api/auth/token', 
        new URLSearchParams({
          'username': email,
          'password': password
        }), 
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      );
      
      const { access_token, user } = response.data;
      
      setToken(access_token);
      setAuthToken(access_token);
      setUser(user);
      setIsAuthenticated(true);
      
      showSnackbar('Erfolgreich angemeldet', 'success');
      navigate('/dashboard');
      
      return true;
    } catch (error) {
      console.error('Login fehlgeschlagen:', error);
      
      let errorMessage = 'Anmeldung fehlgeschlagen';
      if (error.response && error.response.data && error.response.data.detail) {
        errorMessage = error.response.data.detail;
      }
      
      showSnackbar(errorMessage, 'error');
      return false;
    }
  };
  
  // Logout-Funktion
  const logout = () => {
    setToken(null);
    setAuthToken(null);
    setUser(null);
    setIsAuthenticated(false);
    navigate('/login');
  };
  
  // Registrierungsfunktion
  const register = async (email, password, fullName) => {
    try {
      const response = await axios.post('/api/users/', {
        email,
        password,
        full_name: fullName
      });
      
      showSnackbar('Registrierung erfolgreich. Bitte melden Sie sich an.', 'success');
      navigate('/login');
      return true;
    } catch (error) {
      console.error('Registrierung fehlgeschlagen:', error);
      
      let errorMessage = 'Registrierung fehlgeschlagen';
      if (error.response && error.response.data && error.response.data.detail) {
        errorMessage = error.response.data.detail;
      }
      
      showSnackbar(errorMessage, 'error');
      return false;
    }
  };
  
  // Funktion zum Aktualisieren des Benutzerprofils
  const updateProfile = async (userData) => {
    try {
      const response = await axios.put('/api/users/me', userData);
      setUser(response.data);
      showSnackbar('Profil erfolgreich aktualisiert', 'success');
      return true;
    } catch (error) {
      console.error('Fehler beim Aktualisieren des Profils:', error);
      showSnackbar('Fehler beim Aktualisieren des Profils', 'error');
      return false;
    }
  };
  
  // Werte und Funktionen für den Kontext
  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    register,
    updateProfile
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};