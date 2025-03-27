import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  TextField,
  IconButton,
  Paper,
  Divider,
  CircularProgress,
  Avatar,
  Tooltip,
  InputAdornment,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
} from '@mui/material';
import {
  Send as SendIcon,
  Delete as DeleteIcon,
  ArrowBack as ArrowBackIcon,
  Edit as EditIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  Science as ScienceIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { chatService } from '../services/api';
import { useSnackbar } from '../contexts/SnackbarContext';

const ChatPage = () => {
  const { chatId } = useParams();
  const navigate = useNavigate();
  const { showSnackbar } = useSnackbar();
  const messagesEndRef = useRef(null);
  
  // States
  const [chat, setChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [editingTitle, setEditingTitle] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [showSources, setShowSources] = useState({});
  
  // Chat und Nachrichten laden
  useEffect(() => {
    const fetchChat = async () => {
      try {
        setLoading(true);
        const response = await chatService.getChat(chatId);
        setChat(response.chat);
        setMessages(response.messages);
        setNewTitle(response.chat.title);
      } catch (error) {
        console.error('Fehler beim Laden des Chats:', error);
        showSnackbar('Fehler beim Laden des Chats', 'error');
        navigate('/chats');
      } finally {
        setLoading(false);
      }
    };
    
    fetchChat();
    
    // Polling für neue Nachrichten (zur Aktualisierung von Assistentenantworten in Echtzeit)
    const interval = setInterval(() => {
      if (!sending) {
        fetchChat();
      }
    }, 5000);
    
    return () => clearInterval(interval);
  }, [chatId, navigate, showSnackbar, sending]);
  
  // Zum Ende der Nachrichtenliste scrollen
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // Nachricht senden
  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!newMessage.trim()) return;
    
    try {
      setSending(true);
      await chatService.sendMessage(chatId, newMessage);
      setNewMessage('');
      
      // Sofort die neue Benutzernachricht anzeigen
      const tempUserMessage = {
        id: Date.now(),
        role: 'user',
        content: newMessage,
        created_at: new Date().toISOString(),
      };
      
      const tempAssistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Ihre Anfrage wird verarbeitet...',
        created_at: new Date().toISOString(),
      };
      
      setMessages([...messages, tempUserMessage, tempAssistantMessage]);
      
      // Chatnamen aktualisieren, wenn es der erste ist
      if (chat.title === 'Neuer medizinischer Chat') {
        setChat({
          ...chat,
          title: newMessage.length > 50 ? `${newMessage.substring(0, 50)}...` : newMessage,
        });
        setNewTitle(newMessage.length > 50 ? `${newMessage.substring(0, 50)}...` : newMessage);
      }
    } catch (error) {
      console.error('Fehler beim Senden der Nachricht:', error);
      showSnackbar('Fehler beim Senden der Nachricht', 'error');
    } finally {
      setSending(false);
    }
  };
  
  // Chat-Titel bearbeiten
  const handleEditTitle = async () => {
    if (!editingTitle) {
      setEditingTitle(true);
      return;
    }
    
    if (!newTitle.trim()) {
      setNewTitle(chat.title);
      setEditingTitle(false);
      return;
    }
    
    try {
      const updatedChat = await chatService.updateChatTitle(chatId, newTitle);
      setChat({ ...chat, title: updatedChat.title });
      setEditingTitle(false);
    } catch (error) {
      console.error('Fehler beim Aktualisieren des Chat-Titels:', error);
      showSnackbar('Fehler beim Aktualisieren des Chat-Titels', 'error');
    }
  };
  
  // Chat löschen
  const handleDeleteChat = async () => {
    try {
      await chatService.deleteChat(chatId);
      showSnackbar('Chat erfolgreich gelöscht', 'success');
      navigate('/chats');
    } catch (error) {
      console.error('Fehler beim Löschen des Chats:', error);
      showSnackbar('Fehler beim Löschen des Chats', 'error');
    }
  };
  
  // Quellen anzeigen/ausblenden
  const toggleSources = (messageId) => {
    setShowSources({
      ...showSources,
      [messageId]: !showSources[messageId],
    });
  };
  
  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: 'calc(100vh - 64px)',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }
  
  return (
    <Box sx={{ height: 'calc(100vh - 88px)', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          mb: 2,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton onClick={() => navigate('/chats')} sx={{ mr: 1 }}>
            <ArrowBackIcon />
          </IconButton>
          
          {editingTitle ? (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <TextField
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                size="small"
                autoFocus
                sx={{ minWidth: 300 }}
              />
              <IconButton onClick={handleEditTitle} color="primary">
                <CheckIcon />
              </IconButton>
              <IconButton onClick={() => {
                setNewTitle(chat.title);
                setEditingTitle(false);
              }}>
                <CloseIcon />
              </IconButton>
            </Box>
          ) : (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Typography variant="h6" component="h1">
                {chat.title}
              </Typography>
              <IconButton onClick={handleEditTitle} size="small" sx={{ ml: 1 }}>
                <EditIcon fontSize="small" />
              </IconButton>
            </Box>
          )}
        </Box>
        
        <IconButton
          color="error"
          onClick={() => setDeleteDialogOpen(true)}
          title="Chat löschen"
        >
          <DeleteIcon />
        </IconButton>
      </Box>
      
      {/* Nachrichtenbereich */}
      <Paper
        sx={{
          flex: 1,
          p: 2,
          mb: 2,
          overflowY: 'auto',
          bgcolor: '#f5f5f5',
          borderRadius: 2,
        }}
      >
        {messages.length === 0 ? (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              color: 'text.secondary',
            }}
          >
            <Typography variant="body1" gutterBottom>
              Stellen Sie eine medizinische Frage oder beschreiben Sie einen Fall.
            </Typography>
            <Typography variant="body2">
              ASCLEA wird Ihnen mit evidenzbasierten Informationen antworten.
            </Typography>
          </Box>
        ) : (
          messages.map((message) => (
            <Box key={message.id} sx={{ mb: 2 }}>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
                }}
              >
                <Avatar
                  sx={{
                    bgcolor: message.role === 'user' ? 'primary.main' : 'secondary.main',
                    width: 36,
                    height: 36,
                    mx: 1,
                  }}
                >
                  {message.role === 'user' ? 'A' : 'M'}
                </Avatar>
                
                <Paper
                  elevation={1}
                  sx={{
                    p: 2,
                    maxWidth: '70%',
                    borderRadius: 2,
                    bgcolor: message.role === 'user' ? 'primary.light' : 'white',
                    color: message.role === 'user' ? 'white' : 'inherit',
                  }}
                >
                  {message.role === 'assistant' && message.content === 'Ihre Anfrage wird verarbeitet...' ? (
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <CircularProgress size={20} sx={{ mr: 1 }} />
                      <Typography>{message.content}</Typography>
                    </Box>
                  ) : (
                    <Box>
                      <ReactMarkdown
                        children={message.content}
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
                      
                      {message.role === 'assistant' && message.sources && message.sources.length > 0 && (
                        <Box sx={{ mt: 1 }}>
                          <Button
                            size="small"
                            startIcon={<ScienceIcon />}
                            onClick={() => toggleSources(message.id)}
                            sx={{ textTransform: 'none' }}
                          >
                            {showSources[message.id] ? 'Quellen ausblenden' : 'Quellen anzeigen'}
                          </Button>
                          
                          {showSources[message.id] && (
                            <Box sx={{ mt: 1, p: 1, bgcolor: '#f9f9f9', borderRadius: 1, fontSize: '0.85rem' }}>
                              <Typography variant="caption" sx={{ fontWeight: 'bold' }}>
                                Quellen:
                              </Typography>
                              <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
                                {message.sources.map((source, index) => (
                                  <li key={index}>
                                    <Typography variant="caption">
                                      {source.title} ({source.type})
                                      {source.relevance && ` - Relevanz: ${Math.round(source.relevance * 100)}%`}
                                    </Typography>
                                  </li>
                                ))}
                              </ul>
                            </Box>
                          )}
                        </Box>
                      )}
                    </Box>
                  )}
                </Paper>
              </Box>
              
              <Typography
                variant="caption"
                sx={{
                  display: 'block',
                  mt: 0.5,
                  textAlign: message.role === 'user' ? 'right' : 'left',
                  mx: 7,
                  color: 'text.secondary',
                }}
              >
                {new Date(message.created_at).toLocaleTimeString()}
              </Typography>
            </Box>
          ))
        )}
        <div ref={messagesEndRef} />
      </Paper>
      
      {/* Eingabebereich */}
      <Paper
        component="form"
        onSubmit={handleSendMessage}
        sx={{
          p: '2px 4px',
          display: 'flex',
          alignItems: 'center',
          borderRadius: 2,
        }}
      >
        <TextField
          fullWidth
          placeholder="Medizinische Frage stellen..."
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          disabled={sending}
          multiline
          maxRows={4}
          sx={{ flexGrow: 1, '& .MuiOutlinedInput-notchedOutline': { border: 'none' } }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <Tooltip title="Nachricht senden">
                  <span>
                    <IconButton
                      color="primary"
                      type="submit"
                      disabled={!newMessage.trim() || sending}
                    >
                      {sending ? <CircularProgress size={24} /> : <SendIcon />}
                    </IconButton>
                  </span>
                </Tooltip>
              </InputAdornment>
            ),
          }}
        />
      </Paper>
      
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

export default ChatPage;