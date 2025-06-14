#Transcribe audio files using OpenAI's Whisper model
import whisper, os

import sys
print(f"Using Python interpreter: {sys.executable}")

file_path = "D:/Python Projects/NLP_Customer_Audit_Project/Data/archive/call_recording_02.wav"
if os.path.exists(file_path):
    print("File exists!")
else:
    print("File not found!")

model = whisper.load_model("base")
result = model.transcribe("D:/Python Projects/NLP_Customer_Audit_Project/Data/archive/call_recording_02.wav")

print(f' The text in video: \n {result["text"]}')


