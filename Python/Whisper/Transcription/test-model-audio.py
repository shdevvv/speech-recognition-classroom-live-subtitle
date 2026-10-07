import os
import subprocess
import wave
import time
from pathlib import Path
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

# testing kalo misal pake sample audio yang di-simulasiin jadi real time input
# for live input from the device's actual mic see test-model-live.py (<- this will be the baseline used for the actual app nanti)

RATE = 16000
CHUNK = 1024
PAUSE_SECONDS = 0.8
STEP_SECONDS = 0.1 # ask whisper to transcribe audio again per step seconds
MAX_SECONDS = 10 # max seconds of audio put in

SAMPLE_FILE = Path(__file__).with_name("sampleAudio.wav")
MODEL_DIR = Path(__file__).parent.parent / "Model"

model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8",
    download_root="../Model/",
)

# main function to call the model to transcribe, input 0.5 - 10 seconds of audio
def transcribe(audio: np.ndarray):
    segments, _ = model.transcribe(
        audio,
        language="id",
        vad_filter=True,
        beam_size=1,
    )


    segments = list(segments)
    if len(segments) <= 0:
        return "", 0
    # print(segments)
    # join into full text
    text = " ".join(s.text.strip() for s in segments).strip()
    last_end = segments[-1].end
    return text, last_end

# ================== load sample file for simulation =========================================

with wave.open(str(SAMPLE_FILE), "rb") as audio_file:
    channels = audio_file.getnchannels()
    sample_rate = audio_file.getframerate()
    if audio_file.getsampwidth() != 2:
        raise ValueError(f"sampleAudio.wav must use 16-bit PCM.")
    raw_audio = audio_file.readframes(audio_file.getnframes())

# convert raw audio bytes to array, normalize to [-1, 1]
input_audio = np.frombuffer(raw_audio, dtype=np.int16).reshape(-1, channels)
input_audio = input_audio.mean(axis=1).astype(np.float32) / 32768.0

if sample_rate != RATE:
    source_positions = np.arange(len(input_audio))
    target_length = round(len(input_audio) * RATE / sample_rate)
    target_positions = np.linspace(0, len(input_audio) - 1, target_length)
    # resample to 16000 Hz
    input_audio = np.interp(target_positions, source_positions, input_audio).astype(np.float32)

# =============================================================================================
# LIVE TRANSCRIPTION SIMULATION

def show_text(full_text: str, text: str) -> None:
    subprocess.run('cls' if os.name == 'nt' else 'clear', shell=True)
    print("\r" + (full_text + text).ljust(120), end="", flush=True) 

full_text = ""
current_text = ""
buffer = np.zeros(0, dtype=np.float32) # temporary buffer for audio chunks
pos = 0 # how much audio already taken
step = int(RATE * STEP_SECONDS) # 16khz * 0.5 -> 8khz per step

# start audio and timer
sd.play(input_audio, RATE)
start = time.monotonic()

while pos < len(input_audio):
    # time from start record in rate format
    arrived = min(len(input_audio), int((time.monotonic() - start) * RATE))

    # if frames now - previous less that step frames and still audio left, continue waiting
    if (arrived - pos) < step and arrived < len(input_audio):
        time.sleep(0.02)
        continue

    # add steps to the buffer
    buffer = np.concatenate([buffer, input_audio[pos:arrived]])
    pos = arrived # update last frames

    duration = len(buffer) / RATE
    if duration < STEP_SECONDS:
        continue

    # transcribe buffer
    text, last_end = transcribe(buffer)

    if not text:
        # only silence: keep just the last second, so we don't grow forever
        buffer = buffer[-RATE:]
        continue

    paused = (duration - last_end) >= PAUSE_SECONDS
    too_long = duration >= MAX_SECONDS

    if paused or too_long:
        print("\rpaused and duration too long, clear buffer", flush=True)
        show_text(full_text, text)
        # empty the bucket
        buffer = np.zeros(0, dtype=np.float32) 
        full_text += text
    else:
        show_text(full_text, text)
        # print(text)

if len(buffer) > 0:
    text, _ = transcribe(buffer)
    if text:
        show_text(text)

sd.wait()


# samples: list[np.ndarray] = []
# window_size = RATE * WINDOW_SECONDS
# buffered_samples = 0

# # for each chunk in the audio
# for start in range(0, len(input_audio), CHUNK):
#     chunk = input_audio[start : start + CHUNK]
#     samples.append(chunk)
#     buffered_samples += len(chunk)

#     # Match the timing of a live microphone producing this chunk.
#     time.sleep(len(chunk) / RATE)

#     # when buffer window is filled, transcribe audio chunk
#     if buffered_samples >= window_size:
#         transcribe(samples)
#         samples = []
#         buffered_samples = 0

# transcribe(samples)