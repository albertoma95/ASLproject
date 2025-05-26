from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import numpy as np
import cv2
import mediapipe as mp
import tensorflow as tf
import json
import threading
from collections import deque
import os

router = APIRouter()

# === Cargar modelo y tokenizer ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # app/
MODEL_PATH = os.path.join(BASE_DIR, "models", "modelo_traductor_frases.h5")
TOKENIZER_PATH = os.path.join(BASE_DIR, "models", "tokenizer_frases.json")

model = tf.keras.models.load_model(MODEL_PATH)

with open(TOKENIZER_PATH, 'r') as f:
    tokenizer_json = json.load(f)

tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(tokenizer_json)

vocab_size = len(tokenizer.word_index) + 1
max_seq_len = model.input[1].shape[1]
max_frames = 30  # igual que antes

# === Inicializar MediaPipe Hands ===
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)

# === Secuencia compartida e inferencia ===
sequence = deque(maxlen=max_frames)
lock = threading.Lock()

def decode_sequence(encoder_input):
    # Función para decodificar la secuencia con el modelo
    states_value = model.layers[2](encoder_input)[1:]
    target_seq = np.zeros((1, max_seq_len))
    decoded_sentence = []

    for i in range(max_seq_len):
        output_tokens = model.predict([encoder_input, target_seq], verbose=0)
        sampled_token_index = np.argmax(output_tokens[0, i])
        if sampled_token_index == 0:
            break
        sampled_word = next((w for w, idx in tokenizer.word_index.items() if idx == sampled_token_index), '')
        decoded_sentence.append(sampled_word)
        target_seq[0, i] = sampled_token_index

    return ' '.join(decoded_sentence)

def procesar_frame(image_bgr):
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    result = hands.process(image_rgb)
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            vector = []
            for lm in hand_landmarks.landmark:
                vector.extend([lm.x, lm.y, lm.z])
            return vector
    return None

def procesar_imagen_desde_bytes(image_bytes):
    np_array = np.frombuffer(image_bytes, np.uint8)
    img_bgr = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    return procesar_frame(img_bgr)

@router.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    image_bytes = await file.read()
    vector = procesar_imagen_desde_bytes(image_bytes)

    if vector:
        with lock:
            sequence.append(vector)

        if len(sequence) == max_frames:
            with lock:
                input_seq = np.array(sequence)[np.newaxis, :, :]
            try:
                prediction = decode_sequence(input_seq)
                return JSONResponse(content={"prediction": prediction})
            except Exception as e:
                return JSONResponse(content={"error": str(e)}, status_code=500)
        else:
            return JSONResponse(content={
                "message": "Imagen recibida. Aún no hay suficientes frames para predecir.",
                "frames_current": len(sequence),
                "frames_required": max_frames
            })
    else:
        return JSONResponse(content={"error": "No se detectó una mano en la imagen."}, status_code=400)
