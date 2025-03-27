import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Box, CircularProgress } from '@mui/material';

const AdminGuard = () => {
  const { isAuthenticated, isLoading, user } = useAuth();
  
  if (isLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }
  
  // Überprüfen, ob der Benutzer angemeldet und Administrator ist
  if (!isAuthenticated || !user || !user.is_admin) {
    return <Navigate to="/dashboard" />;
  }
  
  return <Outlet />;
};

export default AdminGuard;