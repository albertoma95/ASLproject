import React from 'react';
import ReactDOM from 'react-dom/client';
import WebCameraPage from './components/WebCameraPage'; // ajusta la ruta según tu estructura

const root = ReactDOM.createRoot(document.getElementById('root')!);
root.render(
  <React.StrictMode>
    <WebCameraPage />
  </React.StrictMode>
);
