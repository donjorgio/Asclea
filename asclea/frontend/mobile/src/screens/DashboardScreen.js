import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { 
  TextInput, 
  Button, 
  Card, 
  Title, 
  Paragraph, 
  Switch, 
  Text,
  ActivityIndicator,
  useTheme,
  Divider,
  IconButton,
  List,
  Surface
} from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import Markdown from 'react-native-markdown-display';
import { useAuth } from '../contexts/AuthContext';
import { useSnackbar } from '../contexts/SnackbarContext';
import api from '../services/api';

const DashboardScreen = ({ navigation }) => {
  const { user } = useAuth();
  const { showSnackbar } = useSnackbar();
  const theme = useTheme();
  
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [useRag, setUseRag] = useState(true);
  const [showSources, setShowSources] = useState(false);
  
  // Send a medical query
  const handleSendQuery = async () => {
    if (!query.trim()) {
      showSnackbar('Please enter a medical query', 'error');
      return;
    }
    
    setLoading(true);
    try {
      const result = await api.medicalQuery(query, null, useRag);
      setResponse(result);
    } catch (error) {
      console.error('Query error:', error);
      showSnackbar('Failed to process your query', 'error');
    } finally {
      setLoading(false);
    }
  };
  
  // Create a new chat
  const handleCreateChat = async () => {
    try {
      const newChat = await api.createChat();
      navigation.navigate('Chats', { 
        screen: 'Chat', 
        params: { id: newChat.id, title: newChat.title } 
      });
    } catch (error) {
      console.error('Error creating chat:', error);
      showSnackbar('Failed to create a new chat', 'error');
    }
  };
  
  // Navigate to chats list
  const navigateToChats = () => {
    navigation.navigate('Chats', { screen: 'ChatList' });
  };
  
  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : null}
      style={styles.container}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 64 : 0}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Title style={styles.welcomeTitle}>
          Welcome, {user?.full_name || 'Doctor'}!
        </Title>
        
        <Card style={styles.queryCard}>
          <Card.Content>
            <Title>Quick Medical Query</Title>
            <Paragraph>Ask a medical question to get an immediate response.</Paragraph>
            
            <TextInput
              mode="outlined"
              label="Medical Query"
              value={query}
              onChangeText={setQuery}
              placeholder="Describe a case or ask a medical question..."
              multiline
              numberOfLines={3}
              style={styles.queryInput}
              disabled={loading}
            />
            
            <View style={styles.ragToggle}>
              <Text>Use evidence-based sources</Text>
              <Switch
                value={useRag}
                onValueChange={setUseRag}
                disabled={loading}
                color={theme.colors.primary}
              />
            </View>
            
            <Button
              mode="contained"
              onPress={handleSendQuery}
              loading={loading}
              disabled={loading || !query.trim()}
              icon="send"
              style={styles.sendButton}
            >
              Send Query
            </Button>
          </Card.Content>
          
          {response && (
            <View>
              <Divider style={styles.divider} />
              <Card.Content>
                <Title>Response:</Title>
                <Surface style={styles.responseSurface}>
                  <Markdown style={markdownStyles}>
                    {response.answer}
                  </Markdown>
                  
                  {response.sources && response.sources.length > 0 && (
                    <View>
                      <Button
                        mode="text"
                        onPress={() => setShowSources(!showSources)}
                        icon={showSources ? "chevron-up" : "chevron-down"}
                      >
                        {showSources ? "Hide Sources" : "Show Sources"}
                      </Button>
                      
                      {showSources && (
                        <List.Section>
                          <List.Subheader>Sources</List.Subheader>
                          {response.sources.map((source, index) => (
                            <List.Item
                              key={index}
                              title={source.title}
                              description={`${source.type} - Relevance: ${Math.round(source.relevance * 100)}%`}
                              left={props => <List.Icon {...props} icon="book" />}
                            />
                          ))}
                        </List.Section>
                      )}
                    </View>
                  )}
                </Surface>
              </Card.Content>
            </View>
          )}
        </Card>
        
        <View style={styles.cardsContainer}>
          <Card style={styles.actionCard} onPress={handleCreateChat}>
            <Card.Content style={styles.actionCardContent}>
              <Icon name="chat-plus" size={48} color={theme.colors.primary} />
              <Title style={styles.cardTitle}>New Chat</Title>
              <Paragraph>Start a new medical conversation</Paragraph>
            </Card.Content>
          </Card>
          
          <Card style={styles.actionCard} onPress={navigateToChats}>
            <Card.Content style={styles.actionCardContent}>
              <Icon name="chat-processing" size={48} color={theme.colors.accent} />
              <Title style={styles.cardTitle}>My Chats</Title>
              <Paragraph>View your previous chats</Paragraph>
            </Card.Content>
          </Card>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollContent: {
    padding: 16,
  },
  welcomeTitle: {
    fontSize: 24,
    marginBottom: 16,
  },
  queryCard: {
    marginBottom: 16,
  },
  queryInput: {
    marginTop: 16,
  },
  ragToggle: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: 8,
    marginBottom: 8,
  },
  sendButton: {
    marginTop: 16,
  },
  divider: {
    marginTop: 16,
    marginBottom: 16,
  },
  responseSurface: {
    padding: 16,
    marginTop: 8,
    borderRadius: 8,
    backgroundColor: '#f9f9f9',
  },
  cardsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  actionCard: {
    width: '48%',
  },
  actionCardContent: {
    alignItems: 'center',
    padding: 16,
  },
  cardTitle: {
    marginTop: 16,
    textAlign: 'center',
  },
});

const markdownStyles = {
  body: {
    fontSize: 16,
    lineHeight: 24,
  },
  heading1: {
    fontSize: 24,
    marginTop: 12,
    marginBottom: 8,
    fontWeight: 'bold',
  },
  heading2: {
    fontSize: 20,
    marginTop: 10,
    marginBottom: 6,
    fontWeight: 'bold',
  },
  heading3: {
    fontSize: 18,
    marginTop: 8,
    marginBottom: 4,
    fontWeight: 'bold',
  },
  paragraph: {
    marginTop: 4,
    marginBottom: 8,
  },
  listItem: {
    marginBottom: 4,
  },
};

export default DashboardScreen;