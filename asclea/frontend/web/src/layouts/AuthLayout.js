import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { Container, Box, Paper, Typography } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

const AuthLayout = () => {
  const { isAuthenticated, isLoading } = useAuth();
  
  // Wenn der Benutzer bereits angemeldet ist, zur Dashboard-Seite weiterleiten
  if (isAuthenticated && !isLoading) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          py: 4,
        }}
      >
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            mb: 4,
          }}
        >
          <Typography
            variant="h4"
            component="h1"
            gutterBottom
            color="primary"
            fontWeight="bold"
          >
            ASCLEA
          </Typography>
          <Typography variant="subtitle1" color="text.secondary" align="center">
            Medizinischer KI-Assistent für Ärzte
          </Typography>
        </Box>
        
        <Paper
          elevation={3}
          sx={{
            p: 4,
            width: '100%',
            borderRadius: 2,
          }}
        >
          <Outlet />
        </Paper>
        
        <Box mt={3}>
          <Typography variant="caption" color="text.secondary">
            &copy; {new Date().getFullYear()} ASCLEA. Alle Rechte vorbehalten.
          </Typography>
        </Box>
      </Box>
    </Container>
  );
};

export default AuthLayout;