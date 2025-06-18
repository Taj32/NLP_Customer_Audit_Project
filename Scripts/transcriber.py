import whisper
import os
import sys
from datetime import datetime

class Transcriber:
    def __init__(self, model_name="base"):
        """
        Initialize the Transcriber with a specified Whisper model.
        """
        print(f"Using Python interpreter: {sys.executable}")
        self.model = whisper.load_model(model_name)
        print(f"Loaded Whisper model: {model_name}")

    def transcribe_audio(self, audio_path, output_dir):
        """
        Transcribe the given audio file and save the transcription to a text file.

        :param audio_path: Path to the audio file to transcribe.
        :param output_dir: Directory to save the transcription text file.
        """
        if not os.path.exists(audio_path):
            print(f"File not found: {audio_path}")
            return

        print(f"File exists: {audio_path}")
        result = self.model.transcribe(audio_path)

        # Generate a unique filename based on the current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"transcription_{timestamp}.txt")

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Save transcription to a text file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result["text"])

        print(f"Transcription saved to {output_file}")

# Example usage
if __name__ == "__main__":
    # Create an instance of the Transcriber class
    transcriber = Transcriber(model_name="base")

    # Specify the input audio file and output directory
    audio_file = r"D:\Python Projects\NLP_Customer_Audit_Project\recordings\recording_20250618_153432.wav"
    output_dir = r"D:\Python Projects\NLP_Customer_Audit_Project\transcripts"

    # Transcribe the audio file
    transcriber.transcribe_audio(audio_file, output_dir)