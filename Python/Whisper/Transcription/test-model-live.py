import os
import queue
import subprocess
from pathlib import Path
import torch

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

# testing for live audio input transcription 
# uses a queue to store audio input in a seperate thread, while another thread transcribes the audio

# the audio queue will be fetched and fed to the model every 0.5 seconds
# it uses a "bucket" (buffer variable) to store full chunks of the audio for until it detects silence/pause or until audio in the bucket reaches 5 seconds
# so it will first transcribe quickly the first few chunks of the audio, but as the bucket grows naturally the model will receive more audio, more context, so it can correct the words and form full sentences.

# jujur there might be a better way to make it faster and accurate (wordsnya gak kepotong / overlap between buffers) but it kinda works so we'll keep it for now

# future improvements probably: 
# 1. create word-by-word locking for in between bucket clears so gak putus in the middle of a word 
# 2. use a whisper model fine-tuned with indonesian speech
# 3. custom common words as hotwords param for whisper

RATE = 16000
CHUNK = 1024
STEP_SECONDS = 0.2
MAX_SECONDS = 5
MIN_SECONDS = 0.5 
PAUSE_SECONDS = 0.8

CHANNELS = 1

OUTPUT_FILE = "./recordedAudio.wav"
MODEL_DIR = Path(__file__).parent.parent / "Model"

if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"
print(f"loaded device with {device}")
 
# currently uses the smallest faster-whisper model
model = WhisperModel(
    "small",
    device=device,
    compute_type="int8",
    download_root=str(MODEL_DIR),
)

def transcribe(audio: np.ndarray, prev_text):
    segments, _ = model.transcribe(
        audio,
        language="id",
        vad_filter=True,
        beam_size=1,
        initial_prompt=prev_text or None,
        repetition_penalty=1.1,
    )

    segments = list(segments)
    if len(segments) <= 0:
        return "", 0
    text = " ".join(s.text.strip() for s in segments).strip()
    last_end = segments[-1].end
    return text, last_end

# not yet implemented, use for segments
def good_segment(s):
    if s.no_speech_prob > 0.6 and s.avg_logprob < -1.0:
        return False      # silence or noise
    if s.compression_ratio > 2.4:
        return False      # repeat
    if s.avg_logprob < -1.5:
        return False      # unsure
    return True

def show_text(full_text: str, text: str) -> None:
    subprocess.run('cls' if os.name == 'nt' else 'clear', shell=True)
    print("\r" + (full_text + text).ljust(120), end="", flush=True) 

# open stream to audio input from device
audio_queue = queue.Queue()

def on_audio(indata, frames, time_info, status):
    audio_queue.put(indata[:, 0].copy()) 

frames = [] # to store the full audio

full_text = ""
buffer = np.zeros(0, dtype=np.float32) # temporary buffer for audio chunks
new_frames = 0 # how much audio already taken
step = int(RATE * STEP_SECONDS) # 16khz * 0.5 -> 8khz per step

# open the audio input stream
try:
    with sd.InputStream(
        samplerate=RATE,
        channels=1,
        dtype="float32",
        blocksize=CHUNK,
        device=None,
        callback=on_audio,
    ):
        print("recording start")

        # 
        while True:
            try:
                # get audio chunk from queue every 0.5 seconds
                chunks = [audio_queue.get(timeout=0.5)]
                frames.append(chunks)
            except queue.Empty:
                continue

            while not audio_queue.empty():
                chunks.append(audio_queue.get_nowait())

            # gabungin chunksnya
            # gabungin chunks to the current buffer
            # track how many frames the bucket currently have
            new_audio = np.concatenate(chunks)
            buffer = np.concatenate([buffer, new_audio])
            new_frames += len(new_audio)

            # skip if frames are less then min frames (8khz) or duration less than 0.5
            duration = len(buffer) / RATE
            if new_frames < step or duration < MIN_SECONDS:
                continue
            new_frames = 0

            # transcribe text from current buffer
            text, last_end = transcribe(buffer, prev_text=full_text[-200:])

            # skip if no text (means the audio is silent or no words)
            if not text:
                buffer = buffer[-RATE:]
                continue

            paused = (duration - last_end) >= PAUSE_SECONDS
            too_long = duration >= MAX_SECONDS

            if paused or too_long:
                # move on, append to full text and clear buffer
                full_text += text + " "
                show_text(full_text, "")
                buffer = np.zeros(0, dtype=np.float32)
            else:
                show_text(full_text, text)

    # transcribe remaining audio in buffer if any
    if len(buffer) > 0:
        text, _ = transcribe(buffer)
        if text:
            full_text += text + " "
            show_text(full_text, "")
        print("\nStopped.")

except KeyboardInterrupt:
    print("Exit")

# waveFile = wave.open(OUTPUT_FILE, 'wb')
# waveFile.setnchannels(CHANNELS)
# waveFile.setframerate(RATE)
# waveFile.writeframes(b''.join(frames))
# waveFile.close()
# print("recording saved")

