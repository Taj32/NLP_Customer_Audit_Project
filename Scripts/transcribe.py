#Transcribe audio files using OpenAI's Whisper model
import whisper, os

import sys
print(f"Using Python interpreter: {sys.executable}")

file_path = "C:/Users/tajvi/OneDrive/Desktop/pythonProjects/NLP_Customer_Audit_Project/Data/call_center_set/call_recording_01.wav"
if os.path.exists(file_path):
    print("File exists!")
else:
    print("File not found!")

model = whisper.load_model("base")
result = model.transcribe("call_recording_01.wav")

print(f' The text in video: \n {result["text"]}')


