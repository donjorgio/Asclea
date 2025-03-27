import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  CardActionArea,
  IconButton,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  CircularProgress,
  Tooltip,
  Divider,
  Grid,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  ArrowForward as ArrowForwardIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { de } from 'date-fns/locale';
import { chatService } from '../services/api';
import { useSnackbar } from '../contexts/SnackbarContext';

const ChatListPage = () => {
  const navigate = useNavigate();
  const { showSnackbar } = useSnackbar();
  
  // States
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedChatId, setSelectedChatId] = useState(null);
  
  // Chats laden
  useEffect(() => {
    const fetchChats = async () => {
      try {
        setLoading(true);
        const response = await chatService.getChats();
        setChats(response.chats);
      } catch (error) {
        console.error('Fehler beim Laden der Chats:', error);
        showSnackbar('Fehler beim Laden der Chats', 'error');
      } finally {
        setLoading(false);
      }
    };
    
    fetchChats();
  }, [showSnackbar]);
  
  // Neuen Chat erstellen
  const handleCreateChat = async () => {
    try {
      setCreating(true);
      const newChat = await chatService.createChat();
      navigate(`/chats/${newChat.id}`);
    } catch (error) {
      console.error('Fehler beim Erstellen des Chats:', error);
      showSnackbar('Fehler beim Erstellen des Chats', 'error');
      setCreating(false);
    }
  };
  
  // Chat öffnen
  const handleOpenChat = (chatId) => {
    navigate(`/chats/${chatId}`);
  };
  
  // Chat löschen vorbereiten
  const handleDeleteDialog = (e, chatId) => {
    e.stopPropagation();
    setSelectedChatId(chatId);
    setDeleteDialogOpen(true);
  };
  
  // Chat löschen
  const handleDeleteChat = async () => {
    try {
      await chatService.deleteChat(selectedChatId);
      setChats(chats.filter((chat) => chat.id !== selectedChatId));
      showSnackbar('Chat erfolgreich gelöscht', 'success');
    } catch (error) {
      console.error('Fehler beim Löschen des Chats:', error);
      showSnackbar('Fehler beim Löschen des Chats', 'error');
    } finally {
      setDeleteDialogOpen(false);
      setSelectedChatId(null);
    }
  };
  
  return (
    <Box>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 3,
        }}
      >
        <Typography variant="h5" component="h1">
          Alle Chats
        </Typography>
        
        <Button
          variant="contained"
          color="primary"
          startIcon={creating ? <CircularProgress size={20} /> : <AddIcon />}
          onClick={handleCreateChat}
          disabled={creating}
        >
          Neuer Chat
        </Button>
      </Box>
      
      {loading ? (
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: 'calc(100vh - 200px)',
          }}
        >
          <CircularProgress />
        </Box>
      ) : chats.length === 0 ? (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            height: 'calc(100vh - 200px)',
            bgcolor: '#f5f5f5',
            borderRadius: 2,
            p: 4,
          }}
        >
          <Typography variant="h6" gutterBottom>
            Noch keine Chats vorhanden
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph textAlign="center">
            Erstellen Sie einen neuen Chat, um mit ASCLEA zu interagieren und medizinische Fragen zu stellen.
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={creating ? <CircularProgress size={20} /> : <AddIcon />}
            onClick={handleCreateChat}
            disabled={creating}
          >
            Ersten Chat erstellen
          </Button>
        </Box>
      ) : (
        <Grid container spacing={2}>
          {chats.map((chat) => (
            <Grid item xs={12} sm={6} md={4} key={chat.id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  '&:hover': {
                    boxShadow: 4,
                  },
                }}
              >
                <CardActionArea
                  onClick={() => handleOpenChat(chat.id)}
                  sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}
                >
                  <CardContent sx={{ flexGrow: 1, pb: 1 }}>
                    <Box
                      sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'flex-start',
                        mb: 1,
                      }}
                    >
                      <Typography
                        variant="h6"
                        component="h2"
                        sx={{
                          fontWeight: 500,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                        }}
                      >
                        {chat.title}
                      </Typography>
                      
                      <IconButton
                        size="small"
                        color="error"
                        onClick={(e) => handleDeleteDialog(e, chat.id)}
                        sx={{ flexShrink: 0, ml: 1 }}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Box>
                    
                    <Divider sx={{ my: 1 }} />
                    
                    <Box
                      sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        mt: 1,
                      }}
                    >
                      <Typography variant="body2" color="text.secondary">
                        {format(new Date(chat.created_at), 'PPP', { locale: de })}
                      </Typography>
                      
                      <Tooltip title="Chat öffnen">
                        <ArrowForwardIcon color="primary" fontSize="small" />
                      </Tooltip>
                    </Box>
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
      
      {/* Lösch-Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Chat löschen</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Möchten Sie diesen Chat wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Abbrechen</Button>
          <Button onClick={handleDeleteChat} color="error" autoFocus>
            Löschen
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ChatListPage;