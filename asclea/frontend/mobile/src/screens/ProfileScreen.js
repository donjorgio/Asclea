import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import {
  TextInput,
  Button,
  Surface,
  Title,
  Avatar,
  Text,
  Divider,
  useTheme,
  ActivityIndicator,
  IconButton,
} from 'react-native-paper';
import { useAuth } from '../contexts/AuthContext';
import { useSnackbar } from '../contexts/SnackbarContext';

const ProfileScreen = () => {
  const { user, updateProfile, logout } = useAuth();
  const { showSnackbar } = useSnackbar();
  const theme = useTheme();
  
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  
  // Handler for updating the profile
  const handleUpdateProfile = async () => {
    // Validate inputs
    if (!fullName.trim()) {
      showSnackbar('Name is required', 'error');
      return;
    }
    
    if (password && password !== confirmPassword) {
      showSnackbar('Passwords do not match', 'error');
      return;
    }
    
    if (password && password.length < 8) {
      showSnackbar('Password must be at least 8 characters long', 'error');
      return;
    }
    
    try {
      setLoading(true);
      setSuccess(false);
      
      const updateData = {
        full_name: fullName,
      };
      
      // Only include password if provided
      if (password) {
        updateData.password = password;
      }
      
      await updateProfile(updateData);
      
      // Reset password fields
      setPassword('');
      setConfirmPassword('');
      
      setSuccess(true);
      showSnackbar('Profile updated successfully', 'success');
    } catch (error) {
      console.error('Failed to update profile:', error);
      showSnackbar('Failed to update profile', 'error');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.profileHeader}>
          <Avatar.Text
            size={80}
            label={user?.full_name?.charAt(0) || 'U'}
            backgroundColor={theme.colors.primary}
          />
          <Title style={styles.headerTitle}>{user?.full_name || 'User'}</Title>
          <Text style={styles.headerSubtitle}>{user?.email || ''}</Text>
        </View>
        
        <Surface style={styles.formContainer}>
          <Title style={styles.sectionTitle}>Personal Information</Title>
          
          {success && (
            <View style={styles.successBanner}>
              <Text style={styles.successText}>Profile updated successfully!</Text>
            </View>
          )}
          
          <TextInput
            label="Full Name"
            value={fullName}
            onChangeText={setFullName}
            mode="outlined"
            style={styles.input}
            disabled={loading}
          />
          
          <TextInput
            label="Email"
            value={user?.email || ''}
            mode="outlined"
            style={styles.input}
            disabled={true}
            dense
          />
          
          <Divider style={styles.divider} />
          
          <Title style={styles.sectionTitle}>Change Password</Title>
          <Text style={styles.passwordHelp}>Leave blank if you don't want to change your password</Text>
          
          <TextInput
            label="New Password"
            value={password}
            onChangeText={setPassword}
            mode="outlined"
            secureTextEntry={!showPassword}
            style={styles.input}
            disabled={loading}
            right={
              <TextInput.Icon
                icon={showPassword ? 'eye-off' : 'eye'}
                onPress={() => setShowPassword(!showPassword)}
              />
            }
          />
          
          <TextInput
            label="Confirm Password"
            value={confirmPassword}
            onChangeText={setConfirmPassword}
            mode="outlined"
            secureTextEntry={!showPassword}
            style={styles.input}
            disabled={loading || !password}
          />
          
          <Button
            mode="contained"
            onPress={handleUpdateProfile}
            loading={loading}
            disabled={loading || (!fullName.trim() && !password)}
            style={styles.button}
          >
            Update Profile
          </Button>
        </Surface>
        
        <Button
          mode="outlined"
          color={theme.colors.error}
          onPress={logout}
          style={styles.logoutButton}
        >
          Logout
        </Button>
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
  profileHeader: {
    alignItems: 'center',
    padding: 16,
    marginBottom: 16,
  },
  headerTitle: {
    marginTop: 16,
    fontSize: 22,
  },
  headerSubtitle: {
    color: '#666',
  },
  formContainer: {
    padding: 16,
    borderRadius: 8,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    marginBottom: 8,
  },
  input: {
    marginBottom: 16,
  },
  divider: {
    marginVertical: 16,
  },
  passwordHelp: {
    color: '#666',
    marginBottom: 16,
    fontSize: 12,
  },
  button: {
    marginTop: 8,
    paddingVertical: 6,
  },
  logoutButton: {
    marginTop: 8,
    marginBottom: 24,
  },
  successBanner: {
    backgroundColor: '#4CAF50',
    padding: 12,
    borderRadius: 4,
    marginBottom: 16,
  },
  successText: {
    color: 'white',
    textAlign: 'center',
  },
});

export default ProfileScreen;