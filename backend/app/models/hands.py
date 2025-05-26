import os
import cv2
import json
import mediapipe as mp
import pandas as pd
import numpy as np

# === Parámetros ===
NUM_FRAMES = 20
FEATURES_PER_FRAME = 63
csv_path = "C:/Users/Alberto/Documents/Master/ASLproject/dataset/image_word.csv"         # Cambia si es diferente
videos_path = "C:/Users/Alberto/Documents/Master/ASLproject/dataset/videos"           # Carpeta con los .mp4
output_path = "landmarks_temporal_dataset.json"

# === Cargar CSV ===
df = pd.read_csv(csv_path, dtype={'video_id': str})

# === Inicializar MediaPipe ===
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)

temporal_dataset = []

for _, row in df.iterrows():
    video_id = row['video_id']
    word_id = int(row['word_id'])
    video_file = os.path.join(videos_path, f"{video_id}.mp4")

    cap = cv2.VideoCapture(video_file)
    if not cap.isOpened():
        print(f"❌ No se pudo abrir: {video_file}")
        continue

    sequence = []

    while len(sequence) < NUM_FRAMES and cap.isOpened():
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
                sequence.append(vector)
                break  # Solo la primera mano

    cap.release()

    if len(sequence) == 0:
        continue

    # Rellenar si tiene menos de NUM_FRAMES
    if len(sequence) < NUM_FRAMES:
        padding = [[0.0] * FEATURES_PER_FRAME] * (NUM_FRAMES - len(sequence))
        sequence.extend(padding)
    else:
        sequence = sequence[:NUM_FRAMES]

    temporal_dataset.append({
        "sequence": sequence,
        "label": word_id
    })

# === Guardar JSON ===
with open(output_path, "w") as f:
    json.dump(temporal_dataset, f)

print(f"✅ Dataset temporal guardado como {output_path} — {len(temporal_dataset)} muestras")
