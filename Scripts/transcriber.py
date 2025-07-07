import whisper
import os
import sys
from datetime import datetime
from pyannote.audio import Pipeline
from dotenv import load_dotenv


class Transcriber:
    def __init__(self, model_name="base"):
        """
        Initialize the Transcriber with a specified Whisper model and diarization pipeline.
        """
        print(f"Using Python interpreter: {sys.executable}")
        self.model = whisper.load_model(model_name)
        print(f"Loaded Whisper model: {model_name}")

        # Initialize speaker diarization pipeline
        load_dotenv()
        huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
        
        print("Initializing speaker diarization pipeline...")
        try:
            self.diarization_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=huggingface_token  # Replace with your Hugging Face token
            )
            print("Speaker diarization pipeline initialized successfully.")
        except Exception as e:
            print(f"Failed to initialize speaker diarization pipeline: {e}")
            self.diarization_pipeline = None

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

        # Step 1: Perform speaker diarization
        print("Performing speaker diarization...")
        diarization_result = self.diarization_pipeline(audio_path)

        # Step 2: Transcribe the audio
        print("Transcribing audio...")
        transcription_result = self.model.transcribe(audio_path)

        # Step 3: Combine diarization and transcription
        print("Combining diarization and transcription...")
        transcript_with_speakers = self.align_diarization_with_transcription(
            diarization_result, transcription_result["segments"]
        )

        # Generate a unique filename based on the current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"transcription_{timestamp}.txt")

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Save transcription with speaker labels to a text file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcript_with_speakers)

        print(f"Transcription saved to {output_file}")

        return output_file
    
    def align_diarization_with_transcription(self, diarization_result, transcription_segments):
        """
        Align speaker diarization results with transcription segments.

        :param diarization_result: Speaker diarization output.
        :param transcription_segments: Whisper transcription segments.
        :return: A string containing the transcription with speaker labels.
        """
        transcript_with_speakers = ""
        for segment in transcription_segments:
            start_time = segment["start"]
            end_time = segment["end"]
            text = segment["text"]

            # Find the speaker for this segment based on diarization
            speaker = "Speaker"
            for turn, _, speaker_label in diarization_result.itertracks(yield_label=True):
                if turn.start <= start_time and turn.end >= end_time:
                    speaker = speaker_label
                    break

            # Append speaker label and text to the transcript
            transcript_with_speakers += f"{speaker}: {text}\n"
            
        
        # Add breaking line and timestamp
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        transcript_with_speakers += "----------\n"
        transcript_with_speakers += f"{current_timestamp}\n"



        return transcript_with_speakers

# Example usage
if __name__ == "__main__":
    # Create an instance of the Transcriber class
    transcriber = Transcriber(model_name="base")

    # Specify the input audio file and output directory
    audio_file = r"D:\Python Projects\NLP_Customer_Audit_Project\recordings\recording_20250618_153432.wav"
    output_dir = r"D:\Python Projects\NLP_Customer_Audit_Project\transcripts"

    # Transcribe the audio file
    transcriber.transcribe_audio(audio_file, output_dir)