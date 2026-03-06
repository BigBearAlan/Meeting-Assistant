import subprocess
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np

TRANSCRIPT_FILE = "transcript.txt"

SAMPLE_RATE = 16000
DURATION = 4  # seconds

def record_audio():
    print("Recording...")
    audio = sd.rec(int(DURATION * SAMPLE_RATE),
                   samplerate=SAMPLE_RATE,
                   channels=1,
                   dtype="int16")
    sd.wait()
    wav.write("audio.wav", SAMPLE_RATE, audio)

while True:

    record_audio()

    cmd = [
        "/Users/bearsmacbook16/whisper.cpp/build/bin/whisper-cli",
        "-m", "/Users/bearsmacbook16/whisper.cpp/models/ggml-base.en.bin",
        "-f", "audio.wav",
        "-nt"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    transcript = result.stdout.strip()

    print("Transcript:", transcript)

    with open(TRANSCRIPT_FILE, "a") as f:
        f.write(transcript + "\n")
