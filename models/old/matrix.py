import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import to_categorical
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# === 1. Cargar el dataset ===
with open("landmarks_dataset.json", "r") as f:
    data = json.load(f)

X = np.array([item["features"] for item in data])
y = np.array([item["label"] for item in data])

# === 2. Normalizar ===
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# === 3. One-hot encoding ===
num_classes = len(np.unique(y))
y_encoded = to_categorical(y, num_classes=num_classes)

# === 4. División en entrenamiento y validación ===
X_train, X_val, y_train, y_val = train_test_split(
    X_scaled, y_encoded, test_size=0.2, random_state=42
)

# === 5. Cargar el modelo ===
model = load_model("modelo_signos_mejorado.h5")

# === 6. Predicciones ===
y_true = np.argmax(y_val, axis=1)
y_pred = np.argmax(model.predict(X_val), axis=1)

# === 7. Matriz de confusión ===
cm = confusion_matrix(y_true, y_pred)

# === 8. Cargar mapeo ID → palabra ===
id_to_word = pd.read_csv("dataset/word.csv").set_index("word_id")["word"].to_dict()

# === 9. Eliminar diagonal y recolectar confusiones > 10 ===
np.fill_diagonal(cm, 0)

confused_pairs = []
for i in range(len(cm)):
    for j in range(len(cm)):
        if cm[i][j] > 10:  # umbral
            confused_pairs.append((i, j, cm[i][j]))

# Ordenar por cantidad de confusiones
confused_pairs.sort(key=lambda x: x[2], reverse=True)

# === 10. Mostrar todas las confusiones por encima del umbral ===
print(f"\n🔍 Clases confundidas más de 10 veces:")
for i, j, count in confused_pairs:
    word_i = id_to_word.get(i, f"ID {i}")
    word_j = id_to_word.get(j, f"ID {j}")
    print(f"'{word_i}' (ID {i}) fue confundida con '{word_j}' (ID {j}) → {count} veces")
