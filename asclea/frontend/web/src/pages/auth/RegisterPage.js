import React, { useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  TextField,
  Button,
  Typography,
  Box,
  Link,
  InputAdornment,
  IconButton,
  CircularProgress,
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useAuth } from '../../contexts/AuthContext';

// Validierungsschema
const validationSchema = Yup.object({
  fullName: Yup.string()
    .required('Name ist erforderlich'),
  email: Yup.string()
    .email('Geben Sie eine gültige E-Mail-Adresse ein')
    .required('E-Mail ist erforderlich'),
  password: Yup.string()
    .min(8, 'Passwort muss mindestens 8 Zeichen lang sein')
    .required('Passwort ist erforderlich'),
  confirmPassword: Yup.string()
    .oneOf([Yup.ref('password'), null], 'Passwörter müssen übereinstimmen')
    .required('Passwortbestätigung ist erforderlich'),
});

const RegisterPage = () => {
  const { register } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const handleClickShowPassword = () => {
    setShowPassword(!showPassword);
  };
  
  const formik = useFormik({
    initialValues: {
      fullName: '',
      email: '',
      password: '',
      confirmPassword: '',
    },
    validationSchema,
    onSubmit: async (values) => {
      setIsSubmitting(true);
      try {
        await register(values.email, values.password, values.fullName);
      } finally {
        setIsSubmitting(false);
      }
    },
  });
  
  return (
    <Box>
      <Typography variant="h5" component="h2" gutterBottom>
        Registrieren
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Erstellen Sie ein neues Konto.
      </Typography>
      
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
          id="email"
          name="email"
          label="E-Mail"
          value={formik.values.email}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.email && Boolean(formik.errors.email)}
          helperText={formik.touched.email && formik.errors.email}
          margin="normal"
          disabled={isSubmitting}
        />
        
        <TextField
          fullWidth
          id="password"
          name="password"
          label="Passwort"
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
          disabled={isSubmitting}
        />
        
        <Button
          fullWidth
          variant="contained"
          color="primary"
          type="submit"
          disabled={isSubmitting}
          sx={{ mt: 3, mb: 2 }}
        >
          {isSubmitting ? <CircularProgress size={24} color="inherit" /> : 'Registrieren'}
        </Button>
      </form>
      
      <Box textAlign="center" mt={2}>
        <Typography variant="body2">
          Haben Sie bereits ein Konto?{' '}
          <Link component={RouterLink} to="/login" color="primary">
            Anmelden
          </Link>
        </Typography>
      </Box>
    </Box>
  );
};
