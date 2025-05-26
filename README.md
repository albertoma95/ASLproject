# 🤟 Traductor de Lengua de Señas en Tiempo Real

Este proyecto utiliza **inteligencia artificial**, **visión por computadora** y una interfaz web para traducir señas de lenguaje de señas en tiempo real usando una cámara web. Es ideal como herramienta educativa o asistiva para mejorar la comunicación entre personas sordas y oyentes.

---

## 📸 Demo

![Demo App](docs/demo_app.png) <!-- Reemplaza con tu imagen de demo -->

---

## 🧠 Tecnologías Utilizadas

- **Frontend**: React + TypeScript + MUI + Framer Motion
- **Backend**: FastAPI + TensorFlow + OpenCV + MediaPipe
- **Modelo IA**: Secuencias con RNN/LSTM entrenadas para traducir gestos a texto
- **Tokenización**: Tokenizer de Keras para traducción de índices a palabras

---

## 📦 Estructura del Proyecto

```
├── frontend/             # Aplicación React
├── backend/
│   ├── main.py           # Entrada de FastAPI
│   ├── router.py         # Endpoint /upload/
│   └── models/
│       ├── modelo_traductor_frases.h5
│       └── tokenizer_frases.json
├── README.md
└── requirements.txt
```

---

## 🚀 Instalación Rápida

### 1. Clona el repositorio

```bash
git clone https://github.com/usuario/proyecto-senas.git
cd proyecto-senas
```

### 2. Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # en Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend (React)

```bash
cd ../frontend
npm install
npm run dev
```

Abre en tu navegador: [http://localhost:3000](http://localhost:3000)

---

## 🕹️ ¿Cómo usarlo?

1. Acepta los permisos de cámara cuando abras la app.
2. Haz clic en **"Iniciar Traducción"**.
3. Realiza una seña frente a la cámara.
4. La predicción aparecerá a la derecha tras procesar suficientes frames (30).

---

## 📂 Entrenamiento del Modelo (opcional)

Si deseas entrenar tu propio modelo:

- Recolecta secuencias de landmarks de MediaPipe.
- Preprocesa las secuencias (padding, normalización).
- Entrena una red LSTM o Transformer para traducir secuencias a frases.
- Guarda el modelo `.h5` y el tokenizer como JSON.
