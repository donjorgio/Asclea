import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { jwtDecode } from 'jwt-decode';
import axios from 'axios';
import { useSnackbar } from './SnackbarContext';
import api from '../services/api';

// Create context
const AuthContext = createContext();

// Custom hook to use the auth context
export const useAuth = () => useContext(AuthContext);

// Auth provider component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [token, setToken] = useState(null);
  
  const { showSnackbar } = useSnackbar();
  
  // Initialize auth state from AsyncStorage
  useEffect(() => {
    const initAuth = async () => {
      try {
        // Load token from storage
        const storedToken = await AsyncStorage.getItem('token');
        
        if (storedToken) {
          // Validate token
          const decodedToken = jwtDecode(storedToken);
          const currentTime = Date.now() / 1000;
          
          if (decodedToken.exp < currentTime) {
            // Token is expired
            await logout();
          } else {
            // Token is valid, set it in state and axios
            setToken(storedToken);
            api.setAuthToken(storedToken);
            
            // Get user info
            try {
              const response = await api.get('/users/me');
              setUser(response.data);
              setIsAuthenticated(true);
            } catch (error) {
              console.error('Failed to get user info:', error);
              await logout();
            }
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        await logout();
      } finally {
        setIsLoading(false);
      }
    };
    
    initAuth();
  }, []);
  
  // Login function
  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/token', {
        username: email,
        password: password
      }, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      
      const { access_token, user } = response.data;
      
      // Save token to storage
      await AsyncStorage.setItem('token', access_token);
      
      // Update state
      setToken(access_token);
      api.setAuthToken(access_token);
      setUser(user);
      setIsAuthenticated(true);
      
      showSnackbar('Successfully logged in');
      
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      
      let errorMessage = 'Login failed';
      if (error.response && error.response.data && error.response.data.detail) {
        errorMessage = error.response.data.detail;
      }
      
      showSnackbar(errorMessage, 'error');
      return false;
    }
  };
  
  // Logout function
  const logout = async () => {
    try {
      // Clear token from storage
      await AsyncStorage.removeItem('token');
      
      // Clear state
      setToken(null);
      api.setAuthToken(null);
      setUser(null);
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };
  
  // Register function
  const register = async (email, password, fullName) => {
    try {
      await api.post('/users/', {
        email,
        password,
        full_name: fullName
      });
      
      showSnackbar('Registration successful. Please log in.');
      return true;
    } catch (error) {
      console.error('Registration failed:', error);
      
      let errorMessage = 'Registration failed';
      if (error.response && error.response.data && error.response.data.detail) {
        errorMessage = error.response.data.detail;
      }
      
      showSnackbar(errorMessage, 'error');
      return false;
    }
  };
  
  // Update profile function
  const updateProfile = async (userData) => {
    try {
      const response = await api.put('/users/me', userData);
      setUser(response.data);
      showSnackbar('Profile updated successfully');
      return true;
    } catch (error) {
      console.error('Failed to update profile:', error);
      showSnackbar('Failed to update profile', 'error');
      return false;
    }
  };
  
  // Context value
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