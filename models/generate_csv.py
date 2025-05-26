import pandas as pd
import os

# === CONFIGURACIÓN ===
tsv_path = "D:/OpenASL/data/openasl-v1.0.tsv"         # Ruta al archivo .tsv original
videos_folder = "C:/Users/Alberto/Documents/Master/ASLproject/dataset/videos_frases"            # Carpeta donde están los videos .mp4
output_csv = "videos_con_token.csv"  # Nombre del CSV de salida

# === 1. Cargar TSV ===
df = pd.read_csv(tsv_path, sep='\t')

# === 2. Convertir nombre de archivo (: → _) para hacer match con el sistema de archivos ===
def convertir_vid_a_filename(vid):
    return vid.replace(":", "_") + ".mp4"

df["video_filename"] = df["vid"].apply(convertir_vid_a_filename)

# === 3. Filtrar solo los videos que realmente existen en la carpeta ===
video_files = set(os.listdir(videos_folder))
df_filtrada = df[df["video_filename"].isin(video_files)].copy()

# === 4. Crear nueva columna 'sentence' con el texto tokenizado ===
df_filtrada["sentence"] = df_filtrada["tokenized-text"]

# === 5. Crear y guardar CSV final ===
csv_df = df_filtrada[["video_filename", "sentence", "start", "end"]].rename(
    columns={"video_filename": "video"}
)

csv_df.to_csv(output_csv, index=False)

print(f"✅ CSV generado con {len(csv_df)} frases: {output_csv}")

