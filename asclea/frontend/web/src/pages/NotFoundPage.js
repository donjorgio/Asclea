import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Box, Typography, Button, Container } from '@mui/material';
import { Home as HomeIcon } from '@mui/icons-material';

const NotFoundPage = () => {
  return (
    <Container maxWidth="md">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          textAlign: 'center',
        }}
      >
        <Typography variant="h1" component="h1" gutterBottom>
          404
        </Typography>
        <Typography variant="h4" component="h2" gutterBottom>
          Seite nicht gefunden
        </Typography>
        <Typography variant="body1" paragraph>
          Die von Ihnen gesuchte Seite existiert nicht oder wurde verschoben.
        </Typography>
        <Button
          component={RouterLink}
          to="/"
          variant="contained"
          color="primary"
          startIcon={<HomeIcon />}
          sx={{ mt: 2 }}
        >
          Zurück zur Startseite
        </Button>
      </Box>
    </Container>
  );
};

export default NotFoundPage;