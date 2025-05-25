import json
import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, Embedding
from tensorflow.keras.callbacks import EarlyStopping

# === 1. Cargar dataset ===
with open("frases_dataset.json", "r") as f:
    data = json.load(f)

sequences = [np.array(item["sequence"]) for item in data]
texts = [item["target"] for item in data]

# === 2. Tokenización del texto ===
num_words = 10000
tokenizer = Tokenizer(num_words=num_words, oov_token="<OOV>")
tokenizer.fit_on_texts(texts)
sequences_text = tokenizer.texts_to_sequences(texts)

# === 3. Padding de frases ===
max_seq_len = max(len(seq) for seq in sequences_text)
vocab_size = len(tokenizer.word_index) + 1
decoder_input_data = pad_sequences(sequences_text, maxlen=max_seq_len, padding='post')

# === 4. Crear decoder target desplazado (teacher forcing) ===
decoder_target_data = []
for seq in decoder_input_data:
    shifted = np.concatenate([seq[1:], [0]])
    decoder_target_data.append(shifted)
decoder_target_data = np.array(decoder_target_data)

# === 5. Entrada visual (frames × 63) ===
X = np.array(sequences)

# === 6. División entrenamiento/validación ===
X_train, X_val, y_train_in, y_val_in, y_train_out, y_val_out = train_test_split(
    X, decoder_input_data, decoder_target_data, test_size=0.2, random_state=42
)

# === 7. Modelo encoder-decoder ===
latent_dim = 256

encoder_inputs = Input(shape=(X.shape[1], X.shape[2]))
_, state_h, state_c = LSTM(latent_dim, return_state=True)(encoder_inputs)
encoder_states = [state_h, state_c]

decoder_inputs = Input(shape=(max_seq_len,))
decoder_embedding = Embedding(vocab_size, 128, mask_zero=True)(decoder_inputs)
decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True)
decoder_outputs, _, _ = decoder_lstm(decoder_embedding, initial_state=encoder_states)
decoder_dense = Dense(vocab_size, activation='softmax')
decoder_outputs = decoder_dense(decoder_outputs)

model = Model([encoder_inputs, decoder_inputs], decoder_outputs)
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# === 8. Entrenamiento ===
early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

history = model.fit(
    [X_train, y_train_in], y_train_out,
    validation_data=([X_val, y_val_in], y_val_out),
    batch_size=32,
    epochs=20,
    callbacks=[early_stop],
    verbose=2
)

# === 9. Guardar modelo y tokenizer ===
model.save("modelo_traductor_frases2.h5")
with open("tokenizer_frases.json", "w") as f_tok:
    json.dump(tokenizer.to_json(), f_tok)

print("✅ Modelo guardado como modelo_traductor_frases.h5")
