import os
import io
import wave
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from faster_whisper import WhisperModel  # <-- BENAR (menggunakan garis bawah _)

app = FastAPI(title="TeacherLiveCaption ASR Engine")

# Path penyimpanan model lokal di dalam Docker volume
MODEL_PATH = "/app/Python/Whisper/Model/models"
os.makedirs(MODEL_PATH, exist_ok=True)

print("Memuat Model Faster-Whisper (base)...")
# Memuat model Faster-Whisper (100% Offline)
model = WhisperModel("base", device="cpu", compute_type="int8", download_root=MODEL_PATH)
print("Model Whisper Siap!")

@app.get("/")
def health_check():
    return {"status": "online", "engine": "Faster-Whisper (Local Int8)"}

@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    """
    Endpoint WebSocket untuk menerima stream audio bytes dari Rust/Tauri
    dan mengembalikan teks transkripsi real-time.
    """
    await websocket.accept()
    print("Tauri App terhubung via WebSocket!")
    
    try:
        while True:
            # Menerima data audio mentah (bytes PCM/WAV) dari Tauri
            audio_bytes = await websocket.receive_bytes()
            
            if not audio_bytes:
                continue

            # Konversi audio bytes ke format numpy array yang dibaca Whisper
            audio_stream = io.BytesIO(audio_bytes)
            
            # Proses inferensi ASR secara offline
            segments, info = model.transcribe(
                audio_stream,
                language="id",
                beam_size=1,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=300)
            )
            
            # Gabungkan hasil teks transkripsi
            transcript_text = " ".join([seg.text for seg in segments]).strip()
            
            if transcript_text:
                # Kirim teks subtitle kembali ke Tauri/React
                await websocket.send_json({
                    "status": "success",
                    "text": transcript_text
                })
                
    except WebSocketDisconnect:
        print("Tauri App terputus.")
    except Exception as e:
        print(f"Error ASR: {e}")