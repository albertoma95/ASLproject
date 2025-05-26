import React, { useEffect, useRef, useState } from 'react';
import {
  AppBar,
  Box,
  Button,
  Container,
  CssBaseline,
  Toolbar,
  Typography,
  Paper,
  useTheme,
} from '@mui/material';
import { motion } from 'framer-motion';

const WebCameraPage: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [streaming, setStreaming] = useState(false);
  const [responseText, setResponseText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const intervalRef = useRef<number | null>(null);
  const theme = useTheme();

  useEffect(() => {
    initCamera();
    return () => {
      stopStreaming();
      stopCamera();
    };
  }, []);

  const initCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user',
        },
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current?.play();
        };
      }
    } catch (e) {
      console.error('Error al acceder a la cámara:', e);
      setResponseText('No se pudo acceder a la cámara.');
    }
  };

  const stopCamera = () => {
    const stream = videoRef.current?.srcObject as MediaStream;
    stream?.getTracks().forEach((track) => track.stop());
  };

  const startStreaming = () => {
    if (intervalRef.current) return;
    intervalRef.current = window.setInterval(() => {
      captureAndSend();
    }, 200);
    setStreaming(true);
    setResponseText('');
  };

  const stopStreaming = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setStreaming(false);
  };

  const captureAndSend = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const video = videoRef.current;
    const width = video.videoWidth;
    const height = video.videoHeight;

    if (width && height) {
      canvas.width = width;
      canvas.height = height;

      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      ctx.drawImage(video, 0, 0, width, height);

      canvas.toBlob(async (blob) => {
        if (!blob) {
          setIsLoading(false);
          return;
        }
        setIsLoading(true);

        const formData = new FormData();
        formData.append('file', blob, 'capture.png');

        try {
          const response = await fetch('http://localhost:8000/upload/', {
            method: 'POST',
            body: formData,
          });
          const data = await response.json();

          let newText = '';
          if (data.prediction) {
            newText = `🧠 Traducción: ${data.prediction}`;
          } else if (data.message) {
            newText = `ℹ️ ${data.message}`;
          } else if (data.error) {
            newText = `❌ Error: ${data.error}`;
          } else {
            newText = '⚠️ Respuesta desconocida del servidor.';
          }

          // Solo actualizar el texto si es diferente al actual
          setResponseText((current) =>
            current !== newText ? newText : current
          );
        } catch (err) {
          console.error('Error en la solicitud:', err);
          const errorText = 'Error en la conexión con el servidor.';
          setResponseText((current) =>
            current !== errorText ? errorText : current
          );
        } finally {
          setIsLoading(false);
        }
      }, 'image/png');
    }
  };

  return (
    <Box display="flex" flexDirection="column" minHeight="100vh">
      <CssBaseline />
      <AppBar position="static" sx={{ mb: 4 }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Traductor de Lengua de Señas
          </Typography>
        </Toolbar>
      </AppBar>

      <Box flexGrow={1}>
        <Container maxWidth="lg">
          <Paper elevation={3} sx={{ p: 4, borderRadius: 3 }}>
            <Box
              sx={{
                display: 'flex',
                flexDirection: { xs: 'column', md: 'row' },
                gap: 4,
              }}>
              {/* Cámara */}
              <Box sx={{ flex: 1, textAlign: 'center' }}>
                <Typography variant="h6" gutterBottom>
                  Vista de Cámara
                </Typography>
                <Box
                  sx={{
                    borderRadius: 2,
                    overflow: 'hidden',
                    border: `2px solid ${theme.palette.divider}`,
                    display: 'inline-block',
                    width: '100%',
                  }}>
                  <video
                    ref={videoRef}
                    style={{ width: '100%', borderRadius: '4px' }}
                    autoPlay
                    muted
                    playsInline
                  />
                </Box>

                <Box mt={2}>
                  <Button
                    variant={streaming ? 'contained' : 'outlined'}
                    color={streaming ? 'error' : 'primary'}
                    onClick={streaming ? stopStreaming : startStreaming}>
                    {streaming ? 'Detener Traducción' : 'Iniciar Traducción'}
                  </Button>
                </Box>
              </Box>

              {/* Traducción */}
              <Box
                sx={{
                  flex: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}>
                <Typography variant="h6" gutterBottom>
                  Traducción en Tiempo Real
                </Typography>

                <Paper
                  variant="outlined"
                  sx={{
                    flexGrow: 1,
                    p: 2,
                    minHeight: 300,
                    border: '1px dashed',
                    bgcolor: theme.palette.grey[50],
                    whiteSpace: 'pre-line',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}>
                  {isLoading ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{
                        duration: 1,
                        ease: 'linear',
                        repeat: Infinity,
                      }}>
                      <Box
                        sx={{
                          width: 40,
                          height: 40,
                          border: '4px solid #ccc',
                          borderTop: '4px solid #1976d2',
                          borderRadius: '50%',
                        }}
                      />
                    </motion.div>
                  ) : responseText ? (
                    <motion.div
                      key={responseText}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ duration: 0.4 }}>
                      <Typography>{responseText}</Typography>
                    </motion.div>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      Aquí aparecerá la traducción del lenguaje de señas...
                    </Typography>
                  )}
                </Paper>
              </Box>
            </Box>
          </Paper>
        </Container>
      </Box>

      {/* Footer */}
      <Box
        component="footer"
        sx={{
          py: 2,
          textAlign: 'center',
          bgcolor: theme.palette.grey[100],
        }}>
        <Typography variant="body2" color="text.secondary">
          © 2025 Traductor de Señas - Proyecto IA
        </Typography>
      </Box>

      <canvas ref={canvasRef} style={{ display: 'none' }} />
    </Box>
  );
};

export default WebCameraPage;
