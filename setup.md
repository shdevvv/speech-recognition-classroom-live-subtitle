# 🚀 Developer & Technical Setup Guide

Dokumen ini menjelaskan fungsi dari setiap berkas konfigurasi utama serta cara menjalankan lingkungan pengembangan lokal untuk proyek **TeacherLiveCaption**.

---

## 1. `Dockerfile` (Buku Resep Environment)
`Dockerfile` adalah panduan otomatis untuk membangun *container* Linux terisolasi yang menjalankan mesin AI. Di dalamnya terdapat instruksi untuk:
* Mengunduh sistem operasi dasar berbasis **Python 3.10 slim**.
* Meng-install *tools* pengolah audio sistem operasi seperti **FFmpeg** dan driver **PortAudio**.
* Memasang seluruh pustaka Python dari `requirements.txt`.
* Menyalin kode sumber proyek ke dalam *container* dan membuka **Port 8000**.
* Menjalankan server FastAPI (`server.py`) secara otomatis saat *container* dinyalakan.

---

## 2. `docker-compose.yml` (Pengatur Layanan Docker)
`docker-compose.yml` bertindak sebagai pengatur (*orchestrator*) layanan *container*. Berkas ini berfungsi untuk:
* Menghubungkan `Dockerfile` dengan port laptop (**`8000:8000`**).
* **Melakukan Mounting Folder (`volumes`):** Memastikan perubahan kode di laptop langsung memperbarui kode di dalam Docker secara *real-time* tanpa perlu membangun ulang (*rebuild*).
* **Menyimpan Cache Model:** Menyimpan file model Whisper yang sudah diunduh ke dalam *Docker Volume* lokal agar tidak perlu diunduh berulang kali setiap kali Docker dinyalakan.

---

## 3. `requirements.txt` (Daftar Pustaka Python)
Berkas ini berisi daftar seluruh pustaka (*library*) Python yang dibutuhkan oleh mesin pemroses suara (ASR), antara lain:
* **`torch` & `torchaudio`:** Framework untuk pemrosesan Deep Learning & komputasi matriks audio.
* **`faster-whisper`:** Mesin utama ASR lokal (*Speech-to-Text*) yang hemat memori.
* **`fastapi`, `uvicorn`, `websockets`:** Library untuk membuat server komunikasi data interaktif.
* **`pyaudio`, `sounddevice`, `librosa`:** Library penangkap dan pengolah sinyal suara mikrofon.
* **`reportlab`:** Library pembuat dan penyusun dokumen ekspor catatan (.pdf).

---

## 4. `Python/Whisper/Transcription/server.py` (Server Penghubung ASR)
Berkas ini adalah kode program **FastAPI WebSocket Server** yang bertindak sebagai "jembatan" antara antarmuka Tauri (layar) dengan mesin Whisper:
* **Membuka Jalur WebSocket (`ws://localhost:8000/ws/transcribe`):** Menunggu dan menerima lemparan data suara (*audio bytes*) dari aplikasi Tauri secara *real-time*.
* **Memuat Model Whisper:** Memanggil model Faster-Whisper secara 100% *offline*.
* **Mengubah Suara Menjadi Teks:** Mengolah potongan suara yang masuk menjadi teks bahasa Indonesia.
* **Mengirim Subtitle:** Mengirimkan kembali hasil transkripsi teks ke antarmuka Tauri secara instan untuk ditampilkan sebagai *overlay* transparan.

---

## 5. Cara Penggunaan (Running the App)

### Prasyarat Laptop:
* **Docker Desktop** (harus aktif)
* **Node.js (v18+) & Rust** (untuk antarmuka Tauri)

### Langkah Menjalankan:

1. **Clone & Sync Repository:**
   ```bash
   git clone [https://github.com/username/TeacherLiveCaption.git](https://github.com/username/TeacherLiveCaption.git)
   cd TeacherLiveCaption