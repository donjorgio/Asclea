import React, { createContext, useContext, useState, useRef } from 'react';
import { Snackbar } from 'react-native-paper';

// Create context
const SnackbarContext = createContext();

// Custom hook to use the snackbar context
export const useSnackbar = () => useContext(SnackbarContext);

// Snackbar provider component
export const SnackbarProvider = ({ children }) => {
  const [visible, setVisible] = useState(false);
  const [message, setMessage] = useState('');
  const [type, setType] = useState('default'); // default, error, success
  
  const timeoutRef = useRef(null);
  
  // Show snackbar
  const showSnackbar = (message, type = 'default', duration = 3000) => {
    setMessage(message);
    setType(type);
    setVisible(true);
    
    // Clear any existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    // Set new timeout to hide the snackbar
    timeoutRef.current = setTimeout(() => {
      setVisible(false);
    }, duration);
  };
  
  // Hide snackbar
  const hideSnackbar = () => {
    setVisible(false);
  };
  
  // Get the color based on type
  const getColor = () => {
    switch (type) {
      case 'error':
        return '#f44336';
      case 'success':
        return '#4caf50';
      default:
        return '#2196f3';
    }
  };
  
  return (
    <SnackbarContext.Provider value={{ showSnackbar }}>
      {children}
      <Snackbar
        visible={visible}
        onDismiss={hideSnackbar}
        duration={4000}
        style={{ backgroundColor: getColor() }}
        action={{
          label: 'Dismiss',
          onPress: hideSnackbar,
        }}
      >
        {message}
      </Snackbar>
    </SnackbarContext.Provider>
  );
};