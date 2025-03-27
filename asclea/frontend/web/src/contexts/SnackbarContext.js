import React, { createContext, useContext, useState } from 'react';
import { Snackbar, Alert } from '@mui/material';

// Kontext erstellen
const SnackbarContext = createContext();

// Custom Hook für den Zugriff auf den Snackbar-Kontext
export const useSnackbar = () => useContext(SnackbarContext);

// Snackbar Provider Component
export const SnackbarProvider = ({ children }) => {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [severity, setSeverity] = useState('info');
  
  // Funktion zum Anzeigen einer Snackbar
  const showSnackbar = (message, severity = 'info') => {
    setMessage(message);
    setSeverity(severity);
    setOpen(true);
  };
  
  // Funktion zum Schließen der Snackbar
  const closeSnackbar = () => {
    setOpen(false);
  };
  
  return (
    <SnackbarContext.Provider value={{ showSnackbar }}>
      {children}
      <Snackbar
        open={open}
        autoHideDuration={6000}
        onClose={closeSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={closeSnackbar} severity={severity} sx={{ width: '100%' }}>
          {message}
        </Alert>
      </Snackbar>
    </SnackbarContext.Provider>
  );
};