import json
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

# === 1. Cargar el dataset JSON ===
with open("landmarks_dataset.json", "r") as f:
    data = json.load(f)

# === 2. Separar features y etiquetas ===
X = np.array([item["features"] for item in data])
y = np.array([item["label"] for item in data])

# === 3. Normalizar las features ===
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# === 4. Preparar etiquetas one-hot ===
num_classes = len(np.unique(y))
y_encoded = to_categorical(y, num_classes=num_classes)

# === 5. Dividir en entrenamiento y validación ===
X_train, X_val, y_train, y_val = train_test_split(
    X_scaled, y_encoded, test_size=0.2, random_state=42
)

# === 6. Modelo más profundo ===
model = Sequential([
    Dense(512, activation='relu', input_shape=(X.shape[1],)),
    Dropout(0.4),
    Dense(512, activation='relu'),
    Dropout(0.4),
    Dense(num_classes, activation='softmax')
])

model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# === 7. Entrenamiento con EarlyStopping ===
early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=25,
    batch_size=64,
    callbacks=[early_stop],
    verbose=2
)

# === 8. Evaluación final ===
loss, accuracy = model.evaluate(X_val, y_val)
print(f"Precisión en validación: {accuracy:.4f}")

# === 9. Guardar el modelo entrenado ===
model.save("modelo_signos_mejorado.h5")
print("✅ Modelo guardado como modelo_signos_mejorado.h5")
