# Transcribe audio files using OpenAI's Whisper model
import whisper, os

import sys
print(f"Using Python interpreter: {sys.executable}")

file_path = "D:/Python Projects/NLP_Customer_Audit_Project/Data/archive/call_recording_02.wav"
if os.path.exists(file_path):
    print("File exists!")
else:
    print("File not found!")

model = whisper.load_model("base")
result = model.transcribe(r"D:\Python Projects\NLP_Customer_Audit_Project\recordings\recording_20250618_153432.wav")

# Save transcription to a text file
output_file = "D:/Python Projects/NLP_Customer_Audit_Project/transcripts/transcription2.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(result["text"])

print(f'Transcription saved to {output_file}')