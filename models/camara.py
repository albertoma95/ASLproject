
import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
import json
import threading
import time
from collections import deque
from tensorflow.keras.preprocessing.text import tokenizer_from_json

# === Cargar modelo y tokenizer ===
model = tf.keras.models.load_model("modelo_traductor_frases.h5")
with open("tokenizer_frases.json", "r") as f:
    tokenizer = tokenizer_from_json(json.load(f))

vocab_size = len(tokenizer.word_index) + 1
max_seq_len = model.input[1].shape[1]
features_per_frame = 63
max_frames = 30

# === Inicializar MediaPipe Hands ===
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)

# === Secuencia compartida e inferencia ===
sequence = deque(maxlen=max_frames)
latest_prediction = ""
lock = threading.Lock()

def decode_sequence(encoder_input):
    print("🧠 Ejecutando inferencia...")
    states_value = model.layers[2](encoder_input)[1:]
    target_seq = np.zeros((1, max_seq_len))
    decoded_sentence = []
    for i in range(max_seq_len):
        output_tokens = model.predict([encoder_input, target_seq], verbose=0)
        sampled_token_index = np.argmax(output_tokens[0, i])
        print(f"🔢 Token {i}: {sampled_token_index}")
        if sampled_token_index == 0:
            break
        sampled_word = next((w for w, idx in tokenizer.word_index.items() if idx == sampled_token_index), '')
        decoded_sentence.append(sampled_word)
        target_seq[0, i] = sampled_token_index
    return ' '.join(decoded_sentence)

def inferencia_continua():
    global latest_prediction
    while True:
        if len(sequence) == max_frames:
            with lock:
                input_seq = np.array(sequence)[np.newaxis, :, :]
                is_zero = np.allclose(input_seq, 0.0)
            print("📦 Input válido:", not is_zero, "| Forma:", input_seq.shape)
            if not is_zero:
                try:
                    prediction = decode_sequence(input_seq)
                    with lock:
                        latest_prediction = prediction
                    print("📄 Traducción:", prediction)
                except Exception as e:
                    print("❌ Error en inferencia:", e)
        time.sleep(1.0)

# === Iniciar hilo de inferencia ===
threading.Thread(target=inferencia_continua, daemon=True).start()

# === Webcam loop ===
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(image_rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            vector = []
            for lm in hand_landmarks.landmark:
                vector.extend([lm.x, lm.y, lm.z])
            with lock:
                sequence.append(vector)
            break

    with lock:
        if latest_prediction:
            cv2.putText(frame, latest_prediction, (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Traductor (debug)", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()