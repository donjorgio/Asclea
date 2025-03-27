import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  IconButton,
  InputAdornment,
  Divider,
  Grid,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Save as SaveIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useAuth } from '../contexts/AuthContext';

// Validierungsschema
const validationSchema = Yup.object({
  fullName: Yup.string()
    .required('Name ist erforderlich'),
  password: Yup.string()
    .min(8, 'Passwort muss mindestens 8 Zeichen lang sein'),
  confirmPassword: Yup.string()
    .oneOf([Yup.ref('password'), null], 'Passwörter müssen übereinstimmen'),
});

const ProfilePage = () => {
  const { user, updateProfile } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  
  const handleClickShowPassword = () => {
    setShowPassword(!showPassword);
  };
  
  const formik = useFormik({
    initialValues: {
      fullName: user?.full_name || '',
      password: '',
      confirmPassword: '',
    },
    validationSchema,
    onSubmit: async (values) => {
      setIsSubmitting(true);
      setSuccess(false);
      
      try {
        const updateData = {
          full_name: values.fullName,
        };
        
        // Passwort nur hinzufügen, wenn eines eingegeben wurde
        if (values.password) {
          updateData.password = values.password;
        }
        
        await updateProfile(updateData);
        
        // Passwortfelder zurücksetzen
        formik.setFieldValue('password', '');
        formik.setFieldValue('confirmPassword', '');
        
        setSuccess(true);
      } finally {
        setIsSubmitting(false);
      }
    },
  });
  
  return (
    <Box>
      <Typography variant="h5" component="h1" gutterBottom>
        Mein Profil
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>
              Persönliche Informationen
            </Typography>
            
            {success && (
              <Alert severity="success" sx={{ mb: 3 }}>
                Profil erfolgreich aktualisiert.
              </Alert>
            )}
            
            <form onSubmit={formik.handleSubmit}>
              <TextField
                fullWidth
                id="fullName"
                name="fullName"
                label="Name"
                value={formik.values.fullName}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.fullName && Boolean(formik.errors.fullName)}
                helperText={formik.touched.fullName && formik.errors.fullName}
                margin="normal"
                disabled={isSubmitting}
              />
              
              <TextField
                fullWidth
                disabled
                id="email"
                name="email"
                label="E-Mail"
                value={user?.email || ''}
                margin="normal"
                helperText="Die E-Mail-Adresse kann nicht geändert werden."
              />
              
              <Divider sx={{ my: 3 }} />
              
              <Typography variant="subtitle1" gutterBottom>
                Passwort ändern
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Lassen Sie die Felder leer, wenn Sie Ihr Passwort nicht ändern möchten.
              </Typography>
              
              <TextField
                fullWidth
                id="password"
                name="password"
                label="Neues Passwort"
                type={showPassword ? 'text' : 'password'}
                value={formik.values.password}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.password && Boolean(formik.errors.password)}
                helperText={formik.touched.password && formik.errors.password}
                margin="normal"
                disabled={isSubmitting}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        aria-label="Passwort anzeigen/verbergen"
                        onClick={handleClickShowPassword}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
              
              <TextField
                fullWidth
                id="confirmPassword"
                name="confirmPassword"
                label="Passwort bestätigen"
                type={showPassword ? 'text' : 'password'}
                value={formik.values.confirmPassword}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.confirmPassword && Boolean(formik.errors.confirmPassword)}
                helperText={formik.touched.confirmPassword && formik.errors.confirmPassword}
                margin="normal"
                disabled={isSubmitting || !formik.values.password}
              />
              
              <Button
                fullWidth
                variant="contained"
                color="primary"
                type="submit"
                disabled={isSubmitting || !formik.dirty || !formik.isValid}
                startIcon={isSubmitting ? <CircularProgress size={20} /> : <SaveIcon />}
                sx={{ mt: 3 }}
              >
                Änderungen speichern
              </Button>
            </form>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, borderRadius: 2, bgcolor: '#f5f5f5' }}>
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                mb: 2,
              }}
            >
              <Box
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: '50%',
                  bgcolor: 'primary.main',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  mb: 2,
                }}
              >
                <PersonIcon sx={{ fontSize: 40, color: 'white' }} />
              </Box>
              
              <Typography variant="h6">{user?.full_name}</Typography>
              <Typography variant="body2" color="text.secondary">
                {user?.email}
              </Typography>
            </Box>
            
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="body2" paragraph>
              <strong>Konto erstellt:</strong> {new Date().toLocaleDateString()}
            </Typography>
            
            <Typography variant="body2">
              <strong>Rolle:</strong> {user?.is_admin ? 'Administrator' : 'Arzt'}
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ProfilePage;