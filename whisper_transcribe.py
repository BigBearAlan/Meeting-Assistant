import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile

# Load Whisper model
model = whisper.load_model("base")

SAMPLE_RATE = 16000
CHUNK_DURATION = 5  # seconds

def record_audio(duration):
    print("Recording...")
    audio = sd.rec(int(duration * SAMPLE_RATE),
                   samplerate=SAMPLE_RATE,
                   channels=1,
                   dtype="int16")
    sd.wait()
    return audio

while True:
    audio = record_audio(CHUNK_DURATION)

    # Save temporary audio file
    with tempfile.NamedTemporaryFile(suffix=".wav") as temp:
        wav.write(temp.name, SAMPLE_RATE, audio)

        result = model.transcribe(temp.name)

    print("Transcript:", result["text"])
