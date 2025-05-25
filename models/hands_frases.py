import os
import cv2
import json
import pandas as pd
import numpy as np
import mediapipe as mp

# === Configuración ===
csv_path = "C:/Users/Alberto/Documents/Master/ASLproject/dataset/videos_con_token.csv"
videos_folder = "C:/Users/Alberto/Documents/Master/ASLproject/dataset/videos_frases"
output_json = "frases_dataset.json"
max_frames = 30
features_per_frame = 63  # 21 puntos (x, y, z)

# Inicializar MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)

# Leer CSV
df = pd.read_csv(csv_path)
dataset = []

for _, row in df.iterrows():
    video_file = os.path.join(videos_folder, row["video"])
    sentence = row["sentence"]

    if not os.path.exists(video_file):
        continue

    cap = cv2.VideoCapture(video_file)
    if not cap.isOpened():
        continue

    sequence = []

    while cap.isOpened() and len(sequence) < max_frames:
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

    # Rellenar o recortar
    if len(sequence) < max_frames:
        sequence += [[0.0] * features_per_frame] * (max_frames - len(sequence))
    else:
        sequence = sequence[:max_frames]

    if sequence:
        dataset.append({
            "sequence": sequence,
            "target": sentence
        })

# Guardar dataset como JSON
with open(output_json, "w") as f:
    json.dump(dataset, f)

print(f"✅ Dataset generado con {len(dataset)} ejemplos en: {output_json}")

