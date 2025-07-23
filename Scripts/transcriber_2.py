import os
import random
import string
import subprocess
from pyannote.audio import Pipeline
from whisper import load_model
from pyannote.core import Segment
import time  # Import the time module

# Step 1: Convert MP4 to WAV
def convert_mp4_to_wav(input_file, output_file):
    """
    Convert an MP4 file to a WAV file using ffmpeg.

    Args:
        input_file (str): Path to the input MP4 file.
        output_file (str): Path to the output WAV file.
    """
    command = [
        "ffmpeg",
        "-i", input_file,
        "-ac", "1",  # Mono channel
        "-ar", "22050",  # Sample rate
        output_file
    ]
    subprocess.run(command, check=True)
    print(f"Converted {input_file} to {output_file}")

# Step 2: Perform Speaker Diarization
def perform_diarization(audio_file, diarization_pipeline):
    """
    Perform speaker diarization on the audio file.

    Args:
        audio_file (str): Path to the WAV file.
        diarization_pipeline (Pipeline): Pyannote diarization pipeline.

    Returns:
        diarization_result: Diarization result from Pyannote.
    """
    print("Performing speaker diarization...")
    diarization_result = diarization_pipeline(audio_file)
    return diarization_result

# Step 3: Transcribe Audio
def transcribe_audio(audio_file, whisper_model):
    """
    Transcribe the audio file using Whisper.

    Args:
        audio_file (str): Path to the WAV file.
        whisper_model: Whisper model instance.

    Returns:
        dict: Transcription result from Whisper.
    """
    print("Transcribing audio...")
    transcription_result = whisper_model.transcribe(audio_file)
    return transcription_result

# Step 4: Combine Diarization and Transcription
def combine_diarization_and_transcription(diarization_result, transcription_segments):
    """
    Combine diarization and transcription results into a speaker-labeled transcript.

    Args:
        diarization_result: Diarization result from Pyannote.
        transcription_segments (list): Transcription segments from Whisper.

    Returns:
        str: Combined transcript with speaker labels.
    """
    print("Combining diarization and transcription...")
    transcript_with_speakers = ""
    speaker_mapping = {}
    speaker_counter = 1

    for segment in transcription_segments:
        start_time = segment["start"]
        end_time = segment["end"]
        text = segment["text"]

        # Find the speaker for this segment
        speaker = "Unknown"
        for turn, _, speaker_label in diarization_result.itertracks(yield_label=True):
            if turn.start <= start_time and turn.end >= end_time:
                if speaker_label not in speaker_mapping:
                    speaker_mapping[speaker_label] = f"Speaker {speaker_counter}"
                    speaker_counter += 1
                speaker = speaker_mapping[speaker_label]
                break

        # Append speaker label and text to the transcript
        transcript_with_speakers += f"{speaker}: {text}\n"

    return transcript_with_speakers

# Step 5: Main Function
def main():
    # Start the timer
    start_time = time.time()

    # Input and output paths
    wav_file = "recordings/joe_rogan_15_wav.wav"  # Use the existing WAV file
    output_file = "recordings/Joe_Rogan.txt"

    # Initialize diarization pipeline
    diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")

    # Perform diarization
    diarization_result = perform_diarization(wav_file, diarization_pipeline)

    # Load Whisper model
    whisper_model = load_model("base")

    # Transcribe audio
    transcription_result = transcribe_audio(wav_file, whisper_model)

    # Combine diarization and transcription
    transcript_with_speakers = combine_diarization_and_transcription(
        diarization_result, transcription_result["segments"]
    )

    # Save the transcript to a file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(transcript_with_speakers)

    print(f"Transcription saved to {output_file}")

    # End the timer
    end_time = time.time()

    # Calculate and print the total execution time
    elapsed_time = end_time - start_time
    print(f"Total execution time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
