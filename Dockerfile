# Gunakan base image Python 3.10 slim
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install dependencies sistem (FFmpeg & driver audio/PortAudio)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    portaudio19-dev \
    python3-pyaudio \
    libsndfile1 \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy file kebutuhan instalasi
COPY requirements.txt .

# Install semua library Python
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh source code proyek ke dalam container
COPY . .

# Expose port untuk koneksi WebSocket/HTTP ke Tauri
EXPOSE 8000

# Jalankan server FastAPI saat container start
CMD ["uvicorn", "Python.Whisper.Transcription.server:app", "--host", "0.0.0.0", "--port", "8000"]