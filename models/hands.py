import cv2
import mediapipe as mp
import pandas as pd
import json
import os

# MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)
landmark_data = []

# Leer CSV con id como texto
df = pd.read_csv('C:/Users/Alberto/Documents/Master/ASLproject/dataset/image_word.csv', dtype={'video_id': str})
video_base_path = 'C:/Users/Alberto/Documents/Master/ASLproject/dataset/videos'  # asegúrate de que tenga / al final si concatenas

for index, row in df.iterrows():
    video_id = row['video_id']  # ya es texto, con ceros incluidos
    word_id = int(row['word_id'])
    video_path = os.path.join(video_base_path, f"{video_id}.mp4")

    print(f"Procesando: {video_path}")
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"❌ No se pudo abrir: {video_path}")
        continue

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
                landmark_data.append({
                    "features": vector,
                    "label": word_id
                })

    cap.release()

# Guardar
with open("landmarks_dataset.json", "w") as f:
    json.dump(landmark_data, f)

print("✅ Extracción completada.")
