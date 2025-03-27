import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Grid,
  TextField,
  Button,
  CircularProgress,
  Card,
  CardContent,
  CardActionArea,
  Divider,
  FormControl,
  FormControlLabel,
  Switch,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
} from '@mui/material';
import {
  Chat as ChatIcon,
  ExpandMore as ExpandMoreIcon,
  Send as SendIcon,
  Person as PersonIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { chatService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { useSnackbar } from '../contexts/SnackbarContext';

const DashboardPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { showSnackbar } = useSnackbar();
  
  // States
  const [query, setQuery] = useState('');
  const [medicalQuery, setMedicalQuery] = useState({
    query: '',
    patient_info: null,
    use_rag: true,
  });
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [useRag, setUseRag] = useState(true);
  
  // Medizinische Anfrage stellen
  const handleSubmitQuery = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) return;
    
    try {
      setLoading(true);
      const result = await chatService.medicalQuery(query, null, useRag);
      setResponse(result);
    } catch (error) {
      console.error('Fehler bei der medizinischen Anfrage:', error);
      showSnackbar('Fehler bei der medizinischen Anfrage', 'error');
    } finally {
      setLoading(false);
    }
  };
  
  // Neuen Chat erstellen
  const handleCreateChat = async () => {
    try {
      const newChat = await chatService.createChat();
      navigate(`/chats/${newChat.id}`);
    } catch (error) {
      console.error('Fehler beim Erstellen des Chats:', error);
      showSnackbar('Fehler beim Erstellen des Chats', 'error');
    }
  };
  
  return (
    <Box>
      <Typography variant="h5" component="h1" gutterBottom>
        Willkommen, {user?.full_name || 'Mediziner'}!
      </Typography>
      
      <Alert
        severity="info"
        sx={{ mb: 3 }}
      >
        ASCLEA ist ein KI-Assistent für Ärzte, der medizinisches Fachwissen bereitstellt und Diagnosen unterstützt.
      </Alert>
      
      <Grid container spacing={3}>
        {/* Schnellanfrage */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, mb: 3, borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>
              Schnelle medizinische Anfrage
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Stellen Sie eine medizinische Frage, um sofort eine Antwort zu erhalten.
            </Typography>
            
            <form onSubmit={handleSubmitQuery}>
              <TextField
                fullWidth
                variant="outlined"
                label="Medizinische Anfrage"
                placeholder="Beschreiben Sie einen Fall oder stellen Sie eine medizinische Frage..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                disabled={loading}
                multiline
                rows={2}
                sx={{ mb: 2 }}
              />
              
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <FormControlLabel
                  control={
                    <Switch
                      checked={useRag}
                      onChange={(e) => setUseRag(e.target.checked)}
                      disabled={loading}
                    />
                  }
                  label="Evidenzbasierte Quellen verwenden"
                />
                
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  disabled={loading || !query.trim()}
                  startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
                >
                  Anfrage senden
                </Button>
              </Box>
            </form>
            
            {response && (
              <Box mt={3}>
                <Divider sx={{ mb: 2 }} />
                <Typography variant="subtitle1" gutterBottom fontWeight="medium">
                  Antwort:
                </Typography>
                <Paper
                  elevation={0}
                  sx={{
                    p: 2,
                    bgcolor: '#f5f5f5',
                    borderRadius: 2,
                  }}
                >
                  <ReactMarkdown
                    children={response.answer}
                    components={{
                      p: ({ node, ...props }) => (
                        <Typography component="p" variant="body1" sx={{ mb: 1 }} {...props} />
                      ),
                      h1: ({ node, ...props }) => (
                        <Typography component="h1" variant="h5" sx={{ mt: 2, mb: 1 }} {...props} />
                      ),
                      h2: ({ node, ...props }) => (
                        <Typography component="h2" variant="h6" sx={{ mt: 2, mb: 1 }} {...props} />
                      ),
                      h3: ({ node, ...props }) => (
                        <Typography component="h3" variant="subtitle1" sx={{ mt: 1.5, mb: 1 }} fontWeight="bold" {...props} />
                      ),
                      li: ({ node, ...props }) => (
                        <Typography component="li" variant="body1" sx={{ mb: 0.5 }} {...props} />
                      ),
                    }}
                  />
                  
                  {response.sources && response.sources.length > 0 && (
                    <Accordion sx={{ mt: 2, bgcolor: 'white' }}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography>Quellen</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <ul style={{ margin: 0, paddingLeft: '20px' }}>
                          {response.sources.map((source, index) => (
                            <li key={index}>
                              <Typography variant="body2">
                                {source.title} ({source.type})
                                {source.relevance && ` - Relevanz: ${Math.round(source.relevance * 100)}%`}
                              </Typography>
                            </li>
                          ))}
                        </ul>
                      </AccordionDetails>
                    </Accordion>
                  )}
                </Paper>
              </Box>
            )}
          </Paper>
        </Grid>
        
        {/* Schnellzugriff-Karten */}
        <Grid item xs={12} md={4}>
          <Card
            sx={{
              height: '100%',
              '&:hover': { boxShadow: 4 },
              borderRadius: 2,
            }}
          >
            <CardActionArea
              onClick={handleCreateChat}
              sx={{ height: '100%' }}
            >
              <CardContent
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  textAlign: 'center',
                  p: 3,
                }}
              >
                <ChatIcon
                  sx={{
                    fontSize: 60,
                    color: 'primary.main',
                    mb: 2,
                  }}
                />
                <Typography variant="h6" gutterBottom>
                  Neuen Chat starten
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Erstellen Sie einen neuen Chat für eine ausführliche medizinische Beratung.
                </Typography>
              </CardContent>
            </CardActionArea>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card
            sx={{
              height: '100%',
              '&:hover': { boxShadow: 4 },
              borderRadius: 2,
            }}
          >
            <CardActionArea
              onClick={() => navigate('/chats')}
              sx={{ height: '100%' }}
            >
              <CardContent
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  textAlign: 'center',
                  p: 3,
                }}
              >
                <ChatIcon
                  sx={{
                    fontSize: 60,
                    color: 'secondary.main',
                    mb: 2,
                  }}
                />
                <Typography variant="h6" gutterBottom>
                  Meine Chats
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Greifen Sie auf Ihre gespeicherten Chats und vergangene Anfragen zu.
                </Typography>
              </CardContent>
            </CardActionArea>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card
            sx={{
              height: '100%',
              '&:hover': { boxShadow: 4 },
              borderRadius: 2,
            }}
          >
            <CardActionArea
              onClick={() => navigate('/profile')}
              sx={{ height: '100%' }}
            >
              <CardContent
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  textAlign: 'center',
                  p: 3,
                }}
              >
                <PersonIcon
                  sx={{
                    fontSize: 60,
                    color: 'info.main',
                    mb: 2,
                  }}
                />
                <Typography variant="h6" gutterBottom>
                  Mein Profil
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Verwalten Sie Ihre persönlichen Einstellungen und Ihr Konto.
                </Typography>
              </CardContent>
            </CardActionArea>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;