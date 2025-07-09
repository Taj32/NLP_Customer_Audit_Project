"""
Conversation Summarizer Module

This module provides functionality to summarize conversations from audio or transcription files.
It uses a pre-trained transformer model for summarization and integrates sentiment and emotion analysis
to enhance the summaries. The `ConversationSummarizer` class is the main component of this module.
"""

from transformers import pipeline
from transcriber import Transcriber
from emotion_classifier import EmotionClassifier
from sentiment_analyzer import SentimentAnalyzer
import torch
import os


class ConversationSummarizer:
    """
    A class to summarize conversations from audio or transcription files.

    Attributes:
        transcriber (Transcriber): Component for transcribing audio files.
        summarizer (transformers.pipeline): Pre-trained summarization pipeline.
    """

    def __init__(self):
        """
        Initialize the ConversationSummarizer with required components and models.
        """
        self.transcriber = Transcriber(model_name="base")
        print("CUDA Availability:", torch.cuda.is_available())
        if torch.cuda.is_available():
            print("CUDA Device Name:", torch.cuda.get_device_name(0))

        # Initialize the summarization pipeline
        self.summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",  # Pre-trained summarization model
            device=0 if torch.cuda.is_available() else -1  # Use GPU if available, otherwise CPU
        )

    def summarize_conversation(self, input_path, output_dir, input_type="audio", sentiment_score=None, emotion_results=None):
        """
        Summarize a conversation by transcribing audio or summarizing a transcription file.

        Args:
            input_path (str): Path to the audio or transcription file.
            output_dir (str): Directory to save the transcription (if input is audio).
            input_type (str): Type of input - "audio" for audio file, "transcription" for text file.
            sentiment_score (dict, optional): Sentiment analysis results.
            emotion_results (list, optional): Emotion classification results.

        Returns:
            str: A summary of the conversation.
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
        if sentiment_score is None or emotion_results is None:
            summary = self.generate_summary_independent(transcript)
        else:
            summary = self.generate_summary(transcript, sentiment_score, emotion_results)

        # Print and return the summary
        print("\n\n[[Summary]]:")
        print(summary)
        return summary

    def summarize_day(self, day, summaries_dir="summaries"):
        """
        Summarize all conversations from a specific day.

        Args:
            day (str): The day to summarize in the format 'YYYYMMDD'.
            summaries_dir (str): The directory containing summary files.

        Returns:
            str: An overall summary of the day's conversations.
        """
        # Ensure the summaries directory exists
        if not os.path.exists(summaries_dir):
            print(f"Summaries directory not found: {summaries_dir}")
            return None

        # Find all summary files for the specified day
        summary_files = glob.glob(os.path.join(summaries_dir, f"summary_{day}_*.txt"))
        if not summary_files:
            print(f"No summaries found for the day: {day}")
            return None

        # Combine all summaries into a single text
        combined_summaries = ""
        for summary_file in summary_files:
            with open(summary_file, "r", encoding="utf-8") as f:
                combined_summaries += f.read() + "\n"

        # Generate an overall summary
        print("Generating overall summary for the day...")
        overall_summary = self.summarizer(
            combined_summaries,
            max_new_tokens=500,  # Allow more tokens for a longer summary
            min_length=200,
            num_return_sequences=1,
            do_sample=False,
            truncation=True
        )[0]['summary_text']

        # Clean and return the overall summary
        return self.clean_summary(overall_summary)

    def generate_summary(self, text, sentiment, emotion):
        """
        Generate a summary using a generative model, incorporating sentiment and emotion metrics.

        Args:
            text (str): The text to summarize.
            sentiment (dict): Sentiment analysis results.
            emotion (list): Emotion classification results.

        Returns:
            str: A summarized version of the text.
        """
        # Define the maximum input length for the model
        max_input_length = 512

        # Split the text into chunks that fit within the model's token limit
        chunks = [text[i:i + max_input_length] for i in range(0, len(text), max_input_length)]

        # Summarize each chunk
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            print(f"Summarizing chunk {i + 1}/{len(chunks)}...")
            prompt = (
                f"Summarize the following conversation in a detailed and coherent way:\n\n"
                f"Sentiment: {sentiment}\nEmotion: {emotion}\n\n"
                f"{chunk}\n\nSummary:"
            )
            response = self.summarizer(
                prompt,
                max_new_tokens=300,
                min_length=150,
                num_return_sequences=1,
                do_sample=False,
                truncation=True
            )
            chunk_summaries.append(response[0]['summary_text'])

        # Combine all chunk summaries into a single text
        combined_summary = " ".join(chunk_summaries)

        # Generate a final summary from the combined summaries
        print("Generating final summary...")
        final_prompt = (
            f"Combine the following summaries into a single detailed and coherent summary:\n\n"
            f"Sentiment: {sentiment}\nEmotion: {emotion}\n\n"
            f"{combined_summary}\n\nFinal Summary:"
        )
        final_response = self.summarizer(
            final_prompt,
            max_new_tokens=400,
            min_length=200,
            num_return_sequences=1,
            do_sample=False,
            truncation=True
        )

        # Post-process the final summary
        final_summary = final_response[0]['generated_text']
        return self.clean_summary(final_summary)

    def generate_summary_independent(self, text):
        """
        Generate a summary without incorporating sentiment or emotion metrics.

        Args:
            text (str): The text to summarize.

        Returns:
            str: A summarized version of the text.
        """
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

        combined_summary = " ".join(chunk_summaries)
        return self.clean_summary(combined_summary)

    def clean_summary(self, summary):
        """
        Clean the generated summary by removing repetitive or nonsensical text.

        Args:
            summary (str): The generated summary.

        Returns:
            str: A cleaned version of the summary.
        """
        cleaned_summary = summary.replace("\n", " ").replace("  ", " ")
        return cleaned_summary


if __name__ == "__main__":
    """
    Example usage of the ConversationSummarizer class.

    This script demonstrates how to summarize a conversation from a transcription file.
    """
    # Initialize the summarizer
    summarizer = ConversationSummarizer()

    # Specify the input transcription file and output directory
    transcription_file = r"D:\Python Projects\NLP_Customer_Audit_Project\transcripts\long_conversation.txt"
    output_dir = r"D:\Python Projects\NLP_Customer_Audit_Project\transcripts"

    # Run the summarization pipeline
    summary = summarizer.summarize_conversation(transcription_file, output_dir, input_type="transcription")
    print("----------------------------------")
    print("End Summary:")
    print(summary)