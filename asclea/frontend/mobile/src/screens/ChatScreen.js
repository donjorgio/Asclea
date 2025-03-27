import React, { useState, useEffect, useRef } from 'react';
import { View, StyleSheet, FlatList, KeyboardAvoidingView, Platform } from 'react-native';
import { 
  TextInput, 
  IconButton, 
  Surface, 
  Text,
  ActivityIndicator,
  useTheme,
  Button,
  Dialog,
  Portal,
  Paragraph,
} from 'react-native-paper';
import Markdown from 'react-native-markdown-display';
import { useFocusEffect } from '@react-navigation/native';
import { useSnackbar } from '../contexts/SnackbarContext';
import api from '../services/api';

const ChatScreen = ({ navigation, route }) => {
  const { id: chatId, title } = route.params;
  const { showSnackbar } = useSnackbar();
  const theme = useTheme();
  const flatListRef = useRef(null);
  
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [showSources, setShowSources] = useState({});
  const [refreshing, setRefreshing] = useState(false);
  const [deleteDialogVisible, setDeleteDialogVisible] = useState(false);
  
  // Set header options
  useEffect(() => {
    navigation.setOptions({
      title: title || 'Chat',
      headerRight: () => (
        <IconButton
          icon="delete"
          color={theme.colors.error}
          onPress={() => setDeleteDialogVisible(true)}
        />
      ),
    });
  }, [navigation, title]);
  
  // Load chat messages
  const loadChat = async () => {
    try {
      setLoading(true);
      const response = await api.getChat(chatId);
      
      if (response && response.messages) {
        setMessages(response.messages);
        
        // Update chat title in navigation if needed
        if (title !== response.chat.title) {
          navigation.setParams({ title: response.chat.title });
        }
      }
    } catch (error) {
      console.error('Failed to load chat:', error);
      showSnackbar('Failed to load chat messages', 'error');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };
  
  // Initial load and refresh when screen comes into focus
  useFocusEffect(
    React.useCallback(() => {
      loadChat();
      
      // Add polling for new messages
      const interval = setInterval(() => {
        if (!sending) {
          loadChat();
        }
      }, 5000);
      
      return () => clearInterval(interval);
    }, [chatId, sending])
  );
  
  // Send a message
  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;
    
    try {
      setSending(true);
      
      // Optimistically update UI
      const tempUserMessage = {
        id: Date.now(),
        role: 'user',
        content: newMessage,
        created_at: new Date().toISOString(),
      };
      
      const tempAssistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Processing your request...',
        created_at: new Date().toISOString(),
      };
      
      setMessages([...messages, tempUserMessage, tempAssistantMessage]);
      setNewMessage('');
      
      // Scroll to bottom
      setTimeout(() => {
        flatListRef.current?.scrollToEnd();
      }, 100);
      
      // Actually send the message
      await api.sendMessage(chatId, newMessage);
      
      // Reload chat to get the real response
      await loadChat();
    } catch (error) {
      console.error('Failed to send message:', error);
      showSnackbar('Failed to send message', 'error');
    } finally {
      setSending(false);
    }
  };
  
  // Delete chat
  const handleDeleteChat = async () => {
    try {
      await api.deleteChat(chatId);
      showSnackbar('Chat deleted successfully', 'success');
      navigation.goBack();
    } catch (error) {
      console.error('Failed to delete chat:', error);
      showSnackbar('Failed to delete chat', 'error');
    } finally {
      setDeleteDialogVisible(false);
    }
  };
  
  // Toggle sources visibility
  const toggleSources = (messageId) => {
    setShowSources({
      ...showSources,
      [messageId]: !showSources[messageId],
    });
  };
  
  // Render a message bubble
  const renderMessage = ({ item }) => {
    const isUser = item.role === 'user';
    const isPending = item.role === 'assistant' && item.content === 'Processing your request...';
    
    return (
      <View style={[
        styles.messageContainer,
        isUser ? styles.userMessageContainer : styles.assistantMessageContainer
      ]}>
        <Surface style={[
          styles.messageBubble,
          isUser ? styles.userBubble : styles.assistantBubble
        ]}>
          {isPending ? (
            <View style={styles.pendingContainer}>
              <ActivityIndicator size="small" color="#fff" />
              <Text style={styles.pendingText}>Processing...</Text>
            </View>
          ) : (
            <View>
              <Markdown style={markdownStyles}>
                {item.content}
              </Markdown>
              
              {!isUser && item.sources && item.sources.length > 0 && (
                <View style={styles.sourcesContainer}>
                  <Button
                    mode="text"
                    compact
                    onPress={() => toggleSources(item.id)}
                    style={styles.sourcesButton}
                  >
                    {showSources[item.id] ? 'Hide Sources' : 'Show Sources'}
                  </Button>
                  
                  {showSources[item.id] && (
                    <View style={styles.sourcesList}>
                      <Text style={styles.sourcesTitle}>Sources:</Text>
                      {item.sources.map((source, index) => (
                        <Text key={index} style={styles.sourceItem}>
                          • {source.title} ({source.type})
                          {source.relevance ? ` - Relevance: ${Math.round(source.relevance * 100)}%` : ''}
                        </Text>
                      ))}
                    </View>
                  )}
                </View>
              )}
            </View>
          )}
        </Surface>
        <Text style={[
          styles.messageTime,
          isUser ? styles.userMessageTime : styles.assistantMessageTime
        ]}>
          {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </Text>
      </View>
    );
  };
  
  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : null}
      style={styles.container}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
    >
      {loading && messages.length === 0 ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
        </View>
      ) : (
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderMessage}
          keyExtractor={item => item.id.toString()}
          contentContainerStyle={styles.messagesContainer}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
          onLayout={() => flatListRef.current?.scrollToEnd({ animated: true })}
          refreshing={refreshing}
          onRefresh={() => {
            setRefreshing(true);
            loadChat();
          }}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyText}>No messages yet</Text>
              <Text style={styles.emptySubText}>Start a conversation with ASCLEA</Text>
            </View>
          }
        />
      )}
      
      <Surface style={styles.inputContainer}>
        <TextInput
          mode="outlined"
          placeholder="Ask a medical question..."
          value={newMessage}
          onChangeText={setNewMessage}
          multiline
          style={styles.input}
          disabled={sending}
          right={
            <TextInput.Icon
              icon="send"
              disabled={!newMessage.trim() || sending}
              color={!newMessage.trim() || sending ? '#ccc' : theme.colors.primary}
              onPress={handleSendMessage}
            />
          }
        />
      </Surface>
      
      <Portal>
        <Dialog
          visible={deleteDialogVisible}
          onDismiss={() => setDeleteDialogVisible(false)}
        >
          <Dialog.Title>Delete Chat</Dialog.Title>
          <Dialog.Content>
            <Paragraph>Are you sure you want to delete this chat? This action cannot be undone.</Paragraph>
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={() => setDeleteDialogVisible(false)}>Cancel</Button>
            <Button onPress={handleDeleteChat} color={theme.colors.error}>Delete</Button>
          </Dialog.Actions>
        </Dialog>
      </Portal>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  messagesContainer: {
    padding: 16,
    paddingBottom: 16,
  },
  messageContainer: {
    marginBottom: 16,
    maxWidth: '80%',
  },
  userMessageContainer: {
    alignSelf: 'flex-end',
  },
  assistantMessageContainer: {
    alignSelf: 'flex-start',
  },
  messageBubble: {
    padding: 12,
    borderRadius: 16,
    elevation: 1,
  },
  userBubble: {
    backgroundColor: '#2196f3',
  },
  assistantBubble: {
    backgroundColor: 'white',
  },
  messageTime: {
    fontSize: 12,
    marginTop: 4,
  },
  userMessageTime: {
    alignSelf: 'flex-end',
    color: '#666',
  },
  assistantMessageTime: {
    alignSelf: 'flex-start',
    color: '#666',
  },
  pendingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  pendingText: {
    marginLeft: 8,
    color: '#fff',
  },
  sourcesContainer: {
    marginTop: 8,
  },
  sourcesButton: {
    alignSelf: 'flex-start',
    marginLeft: -8,
  },
  sourcesList: {
    backgroundColor: '#f0f0f0',
    padding: 8,
    borderRadius: 8,
    marginTop: 4,
  },
  sourcesTitle: {
    fontWeight: 'bold',
    marginBottom: 4,
  },
  sourceItem: {
    fontSize: 12,
    marginBottom: 2,
  },
  inputContainer: {
    padding: 8,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  input: {
    maxHeight: 120,
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
    height: 300,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  emptySubText: {
    color: '#666',
  },
});

// Markdown styles
const markdownStyles = {
  body: {
    color: '#333',
  },
  paragraph: {
    marginVertical: 8,
  },
  heading1: {
    fontSize: 20,
    fontWeight: 'bold',
    marginVertical: 8,
  },
  heading2: {
    fontSize: 18,
    fontWeight: 'bold',
    marginVertical: 8,
  },
  heading3: {
    fontSize: 16,
    fontWeight: 'bold',
    marginVertical: 6,
  },
  link: {
    color: '#2196f3',
  },
  blockquote: {
    borderLeftWidth: 4,
    borderLeftColor: '#2196f3',
    paddingLeft: 8,
    fontStyle: 'italic',
  },
  list: {
    marginBottom: 8,
  },
  listItem: {
    marginBottom: 4,
  },
  // Override for user message (white text)
  userText: {
    color: 'white',
  },
};

export default ChatScreen;