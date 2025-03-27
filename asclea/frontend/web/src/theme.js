import { createTheme } from '@mui/material/styles';

// Farbdefinitionen
const primaryColor = '#2196f3';  // Blau
const secondaryColor = '#4caf50';  // Grün
const errorColor = '#f44336';  // Rot
const textPrimary = '#212121';
const textSecondary = '#757575';
const background = '#ffffff';
const surfaceColor = '#f5f5f5';

// Thema erstellen
const theme = createTheme({
  palette: {
    primary: {
      main: primaryColor,
      light: '#6ec6ff',
      dark: '#0069c0',
      contrastText: '#ffffff',
    },
    secondary: {
      main: secondaryColor,
      light: '#80e27e',
      dark: '#087f23',
      contrastText: '#ffffff',
    },
    error: {
      main: errorColor,
    },
    text: {
      primary: textPrimary,
      secondary: textSecondary,
    },
    background: {
      default: background,
      paper: surfaceColor,
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 500,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0px 2px 4px -1px rgba(0,0,0,0.2)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0px 2px 4px -1px rgba(0,0,0,0.1)',
          borderRadius: 12,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        rounded: {
          borderRadius: 12,
        },
      },
    },
  },
});

export default theme;