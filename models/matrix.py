import json
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import to_categorical
from sklearn.metrics import confusion_matrix, classification_report
import pandas as pd
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

# === 8. Reporte por clase ===
report_dict = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
df_report = pd.DataFrame(report_dict).transpose()
df_classes = df_report[df_report.index.str.isdigit()]
df_sorted = df_classes.sort_values(by="f1-score", ascending=True)

print("\n📉 Clases con peor F1-score:")
print(df_sorted.head(10)[["precision", "recall", "f1-score"]])

# === 9. Clases más confundidas ===
# Eliminar la diagonal (aciertos)
np.fill_diagonal(cm, 0)

top_confused_pairs = []
for i in range(len(cm)):
    for j in range(len(cm)):
        if cm[i][j] > 0:
            top_confused_pairs.append((i, j, cm[i][j]))

# Ordenar por número de errores
top_confused_pairs.sort(key=lambda x: x[2], reverse=True)

print("\n🔍 Top 10 clases más confundidas:")
for i, j, count in top_confused_pairs[:10]:
    print(f"Clase real {i} fue confundida con {j} → {count} veces")

# === 10. Visualizar matriz recortada ===
N = 20
plt.figure(figsize=(12, 10))
sns.heatmap(cm[:N, :N], annot=True, fmt="d", cmap="Blues")
plt.title(f"Matriz de confusión (primeras {N} clases)")
plt.xlabel("Predicción")
plt.ylabel("Clase real")
plt.tight_layout()
plt.show()
