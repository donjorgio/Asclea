import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Tooltip,
  Chip,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  CloudUpload as CloudUploadIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { de } from 'date-fns/locale';
import { sourceService } from '../../services/api';
import { useSnackbar } from '../../contexts/SnackbarContext';

const SourcesPage = () => {
  const { showSnackbar } = useSnackbar();
  
  // States
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedSourceId, setSelectedSourceId] = useState(null);
  const [indexing, setIndexing] = useState({});
  
  // Formulardaten
  const [formData, setFormData] = useState({
    title: '',
    source_type: '',
    publisher: '',
    file: null,
  });
  
  // Quellen laden
  useEffect(() => {
    fetchSources();
  }, []);
  
  const fetchSources = async () => {
    try {
      setLoading(true);
      const response = await sourceService.getSources();
      setSources(response.sources);
    } catch (error) {
      console.error('Fehler beim Laden der Quellen:', error);
      showSnackbar('Fehler beim Laden der Quellen', 'error');
    } finally {
      setLoading(false);
    }
  };
  
  // Formular-Änderungen
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };
  
  // Datei-Upload
  const handleFileChange = (e) => {
    setFormData({
      ...formData,
      file: e.target.files[0],
    });
  };
  
  // Quelle hinzufügen
  const handleAddSource = async () => {
    if (!formData.title || !formData.source_type || !formData.file) {
      showSnackbar('Bitte füllen Sie alle Pflichtfelder aus', 'error');
      return;
    }
    
    try {
      const newSource = await sourceService.uploadSource(
        formData.title,
        formData.source_type,
        formData.publisher,
        formData.file
      );
      
      setSources([newSource, ...sources]);
      showSnackbar('Quelle erfolgreich hinzugefügt', 'success');
      
      // Formular zurücksetzen
      setFormData({
        title: '',
        source_type: '',
        publisher: '',
        file: null,
      });
      
      setAddDialogOpen(false);
    } catch (error) {
      console.error('Fehler beim Hinzufügen der Quelle:', error);
      showSnackbar('Fehler beim Hinzufügen der Quelle', 'error');
    }
  };
  
  // Quelle indizieren
  const handleIndexSource = async (sourceId) => {
    try {
      setIndexing({ ...indexing, [sourceId]: true });
      await sourceService.indexSource(sourceId);
      
      // Quelle aktualisieren
      const updatedSources = sources.map((source) =>
        source.id === sourceId
          ? { ...source, indexed: true, index_date: new Date().toISOString() }
          : source
      );
      
      setSources(updatedSources);
      showSnackbar('Quelle erfolgreich indiziert', 'success');
    } catch (error) {
      console.error('Fehler beim Indizieren der Quelle:', error);
      showSnackbar('Fehler beim Indizieren der Quelle', 'error');
    } finally {
      setIndexing({ ...indexing, [sourceId]: false });
    }
  };
  
  // Quelle löschen Dialog
  const handleDeleteDialog = (sourceId) => {
    setSelectedSourceId(sourceId);
    setDeleteDialogOpen(true);
  };
  
  // Quelle löschen
  const handleDeleteSource = async () => {
    try {
      await sourceService.deleteSource(selectedSourceId);
      
      // Quelle aus der Liste entfernen
      setSources(sources.filter((source) => source.id !== selectedSourceId));
      showSnackbar('Quelle erfolgreich gelöscht', 'success');
    } catch (error) {
      console.error('Fehler beim Löschen der Quelle:', error);
      showSnackbar('Fehler beim Löschen der Quelle', 'error');
    } finally {
      setDeleteDialogOpen(false);
      setSelectedSourceId(null);
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
          Medizinische Quellen verwalten
        </Typography>
        
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={fetchSources}
            sx={{ mr: 1 }}
          >
            Aktualisieren
          </Button>
          
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => setAddDialogOpen(true)}
          >
            Neue Quelle
          </Button>
        </Box>
      </Box>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        Hier können Sie medizinische Quellen wie Leitlinien, Fachinformationen und Lehrbücher hochladen, die von ASCLEA für evidenzbasierte Antworten verwendet werden.
      </Alert>
      
      {loading ? (
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '50vh',
          }}
        >
          <CircularProgress />
        </Box>
      ) : sources.length === 0 ? (
        <Paper
          sx={{
            p: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            textAlign: 'center',
            borderRadius: 2,
          }}
        >
          <Typography variant="h6" gutterBottom>
            Keine Quellen vorhanden
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            Fügen Sie medizinische Quellen hinzu, um die Qualität der Antworten zu verbessern.
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => setAddDialogOpen(true)}
          >
            Erste Quelle hinzufügen
          </Button>
        </Paper>
      ) : (
        <TableContainer component={Paper} sx={{ borderRadius: 2 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><strong>Titel</strong></TableCell>
                <TableCell><strong>Typ</strong></TableCell>
                <TableCell><strong>Herausgeber</strong></TableCell>
                <TableCell><strong>Status</strong></TableCell>
                <TableCell><strong>Hinzugefügt am</strong></TableCell>
                <TableCell><strong>Aktionen</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sources.map((source) => (
                <TableRow key={source.id}>
                  <TableCell>{source.title}</TableCell>
                  <TableCell>{source.source_type}</TableCell>
                  <TableCell>{source.publisher || '-'}</TableCell>
                  <TableCell>
                    {source.indexed ? (
                      <Chip
                        label="Indiziert"
                        color="success"
                        size="small"
                        title={source.index_date ? `Indiziert am: ${new Date(source.index_date).toLocaleString()}` : ''}
                      />
                    ) : (
                      <Chip
                        label="Nicht indiziert"
                        color="warning"
                        size="small"
                      />
                    )}
                  </TableCell>
                  <TableCell>
                    {source.created_at
                      ? format(new Date(source.created_at), 'PPP', { locale: de })
                      : '-'}
                  </TableCell>
                  <TableCell>
                    {!source.indexed && (
                      <Tooltip title="Indizieren">
                        <IconButton
                          color="primary"
                          onClick={() => handleIndexSource(source.id)}
                          disabled={indexing[source.id]}
                        >
                          {indexing[source.id] ? (
                            <CircularProgress size={20} />
                          ) : (
                            <CloudUploadIcon />
                          )}
                        </IconButton>
                      </Tooltip>
                    )}
                    
                    <Tooltip title="Löschen">
                      <IconButton
                        color="error"
                        onClick={() => handleDeleteDialog(source.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
      
      {/* Dialog: Neue Quelle hinzufügen */}
      <Dialog
        open={addDialogOpen}
        onClose={() => setAddDialogOpen(false)}
        fullWidth
        maxWidth="sm"
      >
        <DialogTitle>Neue medizinische Quelle hinzufügen</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="title"
            label="Titel"
            fullWidth
            variant="outlined"
            value={formData.title}
            onChange={handleFormChange}
            required
          />
          
          <FormControl fullWidth margin="dense" required>
            <InputLabel>Typ</InputLabel>
            <Select
              name="source_type"
              value={formData.source_type}
              onChange={handleFormChange}
              label="Typ"
            >
              <MenuItem value="guideline">Leitlinie</MenuItem>
              <MenuItem value="textbook">Lehrbuch</MenuItem>
              <MenuItem value="article">Fachartikel</MenuItem>
              <MenuItem value="drug_info">Arzneimittelinformation</MenuItem>
              <MenuItem value="other">Sonstiges</MenuItem>
            </Select>
          </FormControl>
          
          <TextField
            margin="dense"
            name="publisher"
            label="Herausgeber"
            fullWidth
            variant="outlined"
            value={formData.publisher}
            onChange={handleFormChange}
          />
          
          <Box sx={{ mt: 2 }}>
            <input
              accept=".pdf,.html,.txt,.md,.csv,.xlsx"
              id="source-file"
              type="file"
              style={{ display: 'none' }}
              onChange={handleFileChange}
            />
            <label htmlFor="source-file">
              <Button
                variant="outlined"
                component="span"
                startIcon={<CloudUploadIcon />}
                fullWidth
              >
                Datei auswählen
              </Button>
            </label>
            
            {formData.file && (
              <Typography variant="body2" sx={{ mt: 1 }}>
                Ausgewählte Datei: {formData.file.name}
              </Typography>
            )}
          </Box>
          
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
            Unterstützte Dateiformate: PDF, HTML, TXT, MD, CSV, XLSX
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddDialogOpen(false)}>Abbrechen</Button>
          <Button onClick={handleAddSource} color="primary">
            Hinzufügen
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Dialog: Quelle löschen */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Quelle löschen</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Möchten Sie diese Quelle wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Abbrechen</Button>
          <Button onClick={handleDeleteSource} color="error" autoFocus>
            Löschen
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SourcesPage;