import React, { useEffect, useRef, useState } from 'react';
import {
  Container,
  Typography,
  Button,
  Box,
  Paper,
  Alert,
} from '@mui/material';

const WebCameraPage: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [streaming, setStreaming] = useState(false);
  const [responseText, setResponseText] = useState('');
  const intervalRef = useRef<number | null>(null);

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

    // Asegura usar el tamaño real del video
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
          console.error('No se pudo capturar la imagen.');
          return;
        }

        const formData = new FormData();
        formData.append('file', blob, 'capture.png');

        try {
          const response = await fetch('http://localhost:8000/upload/', {
            method: 'POST',
            body: formData,
          });

          const text = await response.text();
          setResponseText(`Respuesta backend: ${text}`);
        } catch (err) {
          setResponseText('Error en la conexión');
        }
      }, 'image/png');
    }
  };

  return (
    <Container maxWidth="md" sx={{ textAlign: 'center', py: 5 }}>
      <Typography variant="h4" gutterBottom>
        Streaming de Cámara Web
      </Typography>

      <Paper elevation={3} sx={{ p: 2, display: 'inline-block' }}>
        <video
          ref={videoRef}
          style={{
            borderRadius: '8px',
            border: '2px solid #ccc',
            maxWidth: '100%',
          }}
          autoPlay
          muted
          playsInline
        />
      </Paper>

      <Box mt={3}>
        <Button
          variant={streaming ? 'contained' : 'outlined'}
          color={streaming ? 'error' : 'primary'}
          onClick={streaming ? stopStreaming : startStreaming}>
          {streaming ? 'Detener streaming' : 'Iniciar streaming'}
        </Button>
      </Box>

      <Box mt={2}>
        {responseText && (
          <Alert
            severity={responseText.includes('Error') ? 'error' : 'success'}>
            {responseText}
          </Alert>
        )}
      </Box>

      <canvas ref={canvasRef} style={{ display: 'none' }} />
    </Container>
  );
};

export default WebCameraPage;
