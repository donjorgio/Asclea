import React, { useState, useEffect } from 'react';
import { View, StyleSheet, FlatList } from 'react-native';
import { 
  Card, 
  Title, 
  Paragraph, 
  Button, 
  FAB, 
  Text,
  ActivityIndicator,
  useTheme,
  IconButton,
  Dialog,
  Portal,
  Divider,
} from 'react-native-paper';
import { format } from 'date-fns';
import { useSnackbar } from '../contexts/SnackbarContext';
import api from '../services/api';

const ChatListScreen = ({ navigation }) => {
  const { showSnackbar } = useSnackbar();
  const theme = useTheme();
  
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [deleteDialogVisible, setDeleteDialogVisible] = useState(false);
  const [selectedChatId, setSelectedChatId] = useState(null);
  
  // Load chats
  useEffect(() => {
    loadChats();
  }, []);
  
  const loadChats = async () => {
    try {
      setLoading(true);
      const response = await api.getChats();
      setChats(response.chats || []);
    } catch (error) {
      console.error('Failed to load chats:', error);
      showSnackbar('Failed to load chats', 'error');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };
  
  // Refresh chats
  const handleRefresh = () => {
    setRefreshing(true);
    loadChats();
  };
  
  // Create a new chat
  const handleCreateChat = async () => {
    try {
      const newChat = await api.createChat();
      navigation.navigate('Chat', { id: newChat.id, title: newChat.title });
    } catch (error) {
      console.error('Failed to create chat:', error);
      showSnackbar('Failed to create a new chat', 'error');
    }
  };
  
  // Open a chat
  const handleOpenChat = (chat) => {
    navigation.navigate('Chat', { id: chat.id, title: chat.title });
  };
  
  // Delete dialog
  const showDeleteDialog = (chatId) => {
    setSelectedChatId(chatId);
    setDeleteDialogVisible(true);
  };
  
  // Delete a chat
  const handleDeleteChat = async () => {
    if (!selectedChatId) return;
    
    try {
      await api.deleteChat(selectedChatId);
      setChats(chats.filter(chat => chat.id !== selectedChatId));
      showSnackbar('Chat deleted successfully', 'success');
    } catch (error) {
      console.error('Failed to delete chat:', error);
      showSnackbar('Failed to delete chat', 'error');
    } finally {
      setDeleteDialogVisible(false);
      setSelectedChatId(null);
    }
  };
  
  // Render an empty state
  const renderEmptyState = () => {
    if (loading) return null;
    
    return (
      <View style={styles.emptyState}>
        <Text style={styles.emptyStateText}>No chats found</Text>
        <Paragraph style={styles.emptyStateParagraph}>
          Start a new chat to interact with ASCLEA and ask medical questions.
        </Paragraph>
        <Button 
          mode="contained" 
          onPress={handleCreateChat}
          style={styles.emptyStateButton}
        >
          Create First Chat
        </Button>
      </View>
    );
  };
  
  // Render a chat item
  const renderChatItem = ({ item }) => (
    <Card style={styles.chatCard} onPress={() => handleOpenChat(item)}>
      <Card.Content>
        <View style={styles.chatHeader}>
          <Title numberOfLines={1} style={styles.chatTitle}>
            {item.title}
          </Title>
          <IconButton 
            icon="delete" 
            size={20} 
            color={theme.colors.error}
            onPress={() => showDeleteDialog(item.id)}
          />
        </View>
        <Divider style={styles.chatDivider} />
        <View style={styles.chatFooter}>
          <Paragraph style={styles.chatDate}>
            {format(new Date(item.created_at), 'PPP')}
          </Paragraph>
          <IconButton
            icon="chevron-right"
            size={20}
            color={theme.colors.primary}
          />
        </View>
      </Card.Content>
    </Card>
  );
  
  return (
    <View style={styles.container}>
      {loading && !refreshing ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
        </View>
      ) : (
        <FlatList
          data={chats}
          renderItem={renderChatItem}
          keyExtractor={item => item.id.toString()}
          contentContainerStyle={styles.listContent}
          ListEmptyComponent={renderEmptyState}
          refreshing={refreshing}
          onRefresh={handleRefresh}
        />
      )}
      
      <FAB
        style={[styles.fab, { backgroundColor: theme.colors.primary }]}
        icon="plus"
        onPress={handleCreateChat}
      />
      
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
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  listContent: {
    padding: 16,
    paddingBottom: 80, // Add space for FAB
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  chatCard: {
    marginBottom: 16,
  },
  chatHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  chatTitle: {
    flex: 1,
  },
  chatDivider: {
    marginVertical: 8,
  },
  chatFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  chatDate: {
    color: '#666',
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
    marginTop: 60,
  },
  emptyStateText: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  emptyStateParagraph: {
    textAlign: 'center',
    marginBottom: 24,
    color: '#666',
  },
  emptyStateButton: {
    paddingHorizontal: 16,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
  },
});

export default ChatListScreen;