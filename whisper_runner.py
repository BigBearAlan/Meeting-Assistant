import subprocess

TRANSCRIPT_FILE = "transcript.txt"

cmd = [
    "/Users/bearsmacbook16/whisper.cpp/build/bin/whisper-cli",
    "-m", "/Users/bearsmacbook16/whisper.cpp/models/ggml-base.en.bin",
    "-f", "audio.wav",
    "-nt"
]

result = subprocess.run(cmd, capture_output=True, text=True)

with open(TRANSCRIPT_FILE, "a") as f:
    f.write(result.stdout + "\n")
