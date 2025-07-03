from transformers import pipeline
from transcriber import Transcriber
from emotion_classifier import EmotionClassifier
from sentiment_analyzer import SentimentAnalyzer
import torch
import os

class ConversationSummarizer:
    def __init__(self):
        self.transcriber = Transcriber(model_name="base")
        print("check ----", torch.cuda.is_available())
        print(torch.cuda.get_device_name(0))
        
        self.summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",  # Better summarization model
            device=0 if torch.cuda.is_available() else -1
        )

    def summarize_conversation(self, input_path, output_dir, input_type="audio"):
        """
        Summarize a conversation by transcribing audio or summarizing a transcription file.

        :param input_path: Path to the audio or transcription file.
        :param output_dir: Directory to save the transcription (if input is audio).
        :param input_type: Type of input - "audio" for audio file, "transcription" for text file.
        :return: A summary of the conversation.
        """
        transcript = None

        if input_type == "audio":
            # Step 1: Transcribe the audio
            print("Transcribing audio...")
            transcription_file = self.transcriber.transcribe_audio(input_path, output_dir)
            if not transcription_file:
                print("Transcription failed.")
                return None

            # Load the transcription
            with open(transcription_file, "r", encoding="utf-8") as f:
                transcript = f.read()

        elif input_type == "transcription":
            # Step 1: Load the transcription directly
            print("Loading transcription...")
            if not os.path.exists(input_path):
                print(f"Transcription file not found: {input_path}")
                return None

            with open(input_path, "r", encoding="utf-8") as f:
                transcript = f.read()

        else:
            print("Invalid input type. Please specify 'audio' or 'transcription'.")
            return None

        # Step 2: Summarize the transcription
        print("Summarizing transcription...")
        summary = self.generate_summary(transcript)

        # Print and return the summary
        print("\n\n[[Summary]]: ")
        print(summary)
        return summary

    def generate_summary(self, text):
        max_input_length = 1024
        chunks = [text[i:i + max_input_length] for i in range(0, len(text), max_input_length)]

        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            print(f"Summarizing chunk {i + 1}/{len(chunks)}...")

            # Skip tiny chunks
            if len(chunk.split()) < 30:
                print("Skipping small chunk (less than 30 words)...")
                continue

            try:
                # Dynamically scale max_length to avoid crash
                chunk_summary = self.summarizer(
                    chunk,
                    max_length=min(300, int(len(chunk.split()) * 0.8)),
                    min_length=50,
                    do_sample=False
                )[0]['summary_text']
                chunk_summaries.append(chunk_summary)

            except RuntimeError as e:
                print(f"RuntimeError during chunk {i + 1}: {str(e)}")
                continue

        if not chunk_summaries:
            return "Summary could not be generated due to short input or model failure."

        combined_summary = " ".join(chunk_summaries)
        if len(text) > max_input_length: #combined_summary
            try:
                final_summary = self.summarizer(
                    text, #combined_summary,
                    max_length=250,
                    min_length=100,
                    do_sample=False
                )[0]['summary_text']
            except RuntimeError as e:
                print(f"Final summarization failed: {str(e)}")
                final_summary = combined_summary
        else:
            final_summary = combined_summary

        return self.clean_summary(final_summary)




    def clean_summary(self, summary):
        """
        Clean the generated summary by removing repetitive or nonsensical text.

        :param summary: The generated summary.
        :return: A cleaned version of the summary.
        """
        # Remove repetitive patterns
        cleaned_summary = summary.replace("\n", " ").replace("  ", " ")
        cleaned_summary = " ".join(dict.fromkeys(cleaned_summary.split()))  # Remove duplicate words
        return cleaned_summary
    
if __name__ == "__main__":
    # Initialize the summarizer
    summarizer = ConversationSummarizer()

    # Specify the input audio file and output directory

    #audio_file = r"D:\Python Projects\NLP_Customer_Audit_Project\recordings\joe_rogan_15.mp4"
    # transcription_file = r"D:\Python Projects\NLP_Customer_Audit_Project\transcripts\transcription_20250702_133735.txt" # 15 minute snippet
    #transcription_file = r"D:\Python Projects\NLP_Customer_Audit_Project\transcripts\transcription_20250701_183407.txt" # full conversation

    transcription_file = r"D:\Python Projects\NLP_Customer_Audit_Project\transcripts\long_conversation.txt" # Claude conversation with message names
    

    
    output_dir = r"D:\Python Projects\NLP_Customer_Audit_Project\transcripts"
    # Run the summarization pipeline
    summary = summarizer.summarize_conversation(transcription_file, output_dir, input_type="transcription")
    print("----------------------------------")
    print("End Summary:")
    print(summary)

# # Example usage
# if __name__ == "__main__":
#     # Initialize the summarizer
#     summarizer = ConversationSummarizer()

#     # Specify the input audio file and output directory
#     # audio_file = r"D:\Python Projects\NLP_Customer_Audit_Project\recordings\malcom-x.wav"
#     audio_file = r"D:\Python Projects\NLP_Customer_Audit_Project\recordings\oliver-anthony.wav"

#     output_dir = r"D:\Python Projects\NLP_Customer_Audit_Project\transcripts"

#     # Run the summarization pipeline
#     summary = summarizer.summarize_conversation(audio_file, output_dir)
#     print("Raw Model Output:", summary)