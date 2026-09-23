# TeacherLiveCaption - Classroom Live Subtitle & Speech Recognition

Sistem aplikasi desktop berbasis **Tauri** (Rust + React & TypeScript) yang terintegrasi dengan pipeline speech recognition **Whisper (Python)** untuk menyediakan live subtitle real-time di ruang kelas beserta pembuatan ringkasan dan catatan kuliah otomatis (Lecture Notes).

---

## 📁 Struktur Direktori (Directory Tree)

```text
TeacherLiveCaption/
├── Tauri/
│   ├── Frontend/
│   │   ├── React/
│   │   ├── TypeScript/
│   │   ├── Control Panel/
│   │   ├── Subtitle Overlay/
│   │   └── Settings/
│   │       └── Speech Provider/
│   │           ├── Whisper Local/
│   │           └── API/
│   └── Rust Backend/
│       ├── App Lifecycle/
│       ├── Window Management/
│       ├── Microphone - Audio Capture/
│       ├── Recording/
│       ├── Whisper Communication/
│       ├── API Communication/
│       └── Frontend Communication/
├── Python/
│   └── Whisper/
│       ├── Model/
│       └── Transcription/
├── API/
│   ├── API Client/
│   ├── API Key Management/
│   └── WebSocket - Streaming/
├── Data Pipeline/
│   ├── Audio Processing/
│   ├── Audio Buffering/
│   ├── Transcription/
│   └── Text Processing/
├── Lecture Notes/
│   ├── Note Generation/
│   ├── Summarization/
│   └── Export/
├── Docker Compose/
│   └── Development Environment/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🧩 Modul & Arsitektur Sistem

### 1. Tauri Desktop App
- **Frontend (React + TypeScript)**:
  - **Control Panel**: Antarmuka kontrol guru/dosen untuk start/stop transkripsi, memilih mikrofon, dan konfigurasi tampilan.
  - **Subtitle Overlay**: Window transparan/overlay frameless yang menampilkan teks subtitle berjalan di atas aplikasi presentasi/slide kelas.
  - **Settings & Speech Provider**: Opsi peralihan antara model Whisper Lokal (offline) atau Cloud API.
- **Rust Backend**:
  - **Microphone & Audio Capture**: Menangkap stream audio langsung dari mic guru dengan latency rendah.
  - **Window Management**: Mengatur status overlay (always on top, click-through, multi-monitor).
  - **Whisper & API Communication**: Menghubungkan audio buffer ke service Python Whisper atau Cloud API via IPC / WebSocket.

### 2. Python Whisper
- **Model**: Manajemen loading model Whisper (`tiny`, `base`, `small`, `medium`, `large-v3`).
- **Transcription**: Engine inference transkripsi speech-to-text berbasis PyTorch/CUDA.

### 3. API & Data Pipeline
- **WebSocket / Streaming**: Aliran data audio chunk masuk dan subtitle keluar secara stream real-time.
- **Audio Buffering & Processing**: VAD (Voice Activity Detection), normalisasi audio, dan chunking.
- **Text Processing**: Punctuation restoration, filtering, dan formatting teks.

### 4. Lecture Notes
- **Note Generation & Summarization**: Merangkum hasil transkripsi sesi kuliah menggunakan model LLM.
- **Export**: Ekspor ringkasan ke format Markdown, PDF, atau Word (.docx).

### 5. Docker Environment
- Menyediakan containerized development environment untuk service Python Whisper dan audio pipeline.

---

## 🚀 Panduan Memulai Cepat

### Prasyarat
- Python 3.10+ & FFmpeg
- Node.js 18+ & Rust / Cargo (untuk pengembangan Tauri)
- Docker & Docker Compose (opsional)

### Instalasi Python Environment
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### Menjalankan dengan Docker Compose
```bash
docker compose up --build
```
