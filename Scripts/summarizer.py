"""
Conversation Summarizer Module (Updated for GODEL)
"""

import glob
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from transcriber import Transcriber
from emotion_classifier import EmotionClassifier
from sentiment_analyzer import SentimentAnalyzer
import torch
import os
import nltk
from nltk import sent_tokenize


class ConversationSummarizer:
    def __init__(self):
        #nltk.download('punkt_tab')
        #nltk.download('punkt')
        self.transcriber = Transcriber(model_name="base")
        print("CUDA Availability:", torch.cuda.is_available())
        if torch.cuda.is_available():
            print("CUDA Device Name:", torch.cuda.get_device_name(0))

        # Initialize GODEL summarization pipeline
        model_name = "facebook/bart-large-cnn"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        self.summarizer = pipeline(
            "summarization",
            model=model,
            tokenizer=tokenizer,
            device=0 if torch.cuda.is_available() else -1
        )

    def summarize_conversation(self, input_path, output_dir, input_type="audio", sentiment_score=None, emotion_results=None):
        transcript = None

        if input_type == "audio":
            print("Transcribing audio...")
            transcription_file = self.transcriber.transcribe_audio(input_path, output_dir)
            if not transcription_file:
                print("Transcription failed.")
                return None

            with open(transcription_file, "r", encoding="utf-8") as f:
                transcript = f.read()

        elif input_type == "transcription":
            print("Loading transcription...")
            if not os.path.exists(input_path):
                print(f"Transcription file not found: {input_path}")
                return None

            with open(input_path, "r", encoding="utf-8") as f:
                transcript = f.read()
        else:
            print("Invalid input type. Please specify 'audio' or 'transcription'.")
            return None

        # Optional: Replace speaker tags for clarity
        transcript = transcript.replace("SPEAKER_00:", "Speaker A:")\
                               .replace("SPEAKER_01:", "Speaker B:")\
                               .replace("Speaker:", "Host:")

        print("Summarizing transcription...")
        if sentiment_score is None or emotion_results is None:
            print("independent...")
            summary = self.generate_summary_independent(transcript)
        else:
            print("non-independent...")
            summary = self.generate_summary(transcript, sentiment_score, emotion_results)

        print("\n\n[[Summary]]:")
        print(summary)
        return summary

    def summarize_day(self, day, summaries_dir="summaries"):
        """
        Generate an overall summary for a specific day.

        Args:
            day (str): The day to summarize (e.g., "20250723").
            summaries_dir (str): Directory containing daily summaries.

        Returns:
            str: The overall summary for the day.
        """
        if not os.path.exists(summaries_dir):
            print(f"Summaries directory not found: {summaries_dir}")
            return None

        summary_files = glob.glob(os.path.join(summaries_dir, f"summary_{day}_*.txt"))
        if not summary_files:
            print(f"No summaries found for the day: {day}")
            return None

        combined_summaries = ""
        for summary_file in summary_files:
            with open(summary_file, "r", encoding="utf-8") as f:
                combined_summaries += f.read() + "\n"

        print("Generating overall summary for the day...")
        try:
            overall_summary = self.summarizer(
                f"Summarize the following conversations:\n\n{combined_summaries}",
                max_length=500,
                min_length=200,
                do_sample=False
            )[0]['summary_text']
        except Exception as e:
            print(f"Error generating overall summary: {str(e)}")
            return None

        return self.clean_summary(overall_summary)

    def generate_summary(self, text, sentiment, emotion):
        """
        Generate a summary using the BART model, incorporating sentiment and emotion metrics.

        Args:
            text (str): The text to summarize.
            sentiment (dict): Sentiment analysis results.
            emotion (list): Emotion classification results.

        Returns:
            str: A summarized version of the text.
        """
        chunks = self.chunk_by_sentences(text)
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            print(f"Summarizing chunk {i + 1}/{len(chunks)}...")
            try:
                output = self.summarizer(
                    chunk,
                    max_length=200,  # Adjusted for concise summaries
                    min_length=50,
                    do_sample=False
                )[0]['summary_text']
                chunk_summaries.append(output)
            except Exception as e:
                print(f"Error summarizing chunk {i + 1}: {str(e)}")
                continue

        # Combine all chunk summaries into a single text
        combined_summary = " ".join(chunk_summaries)

        # Deduplicate the final summary
        deduplicated_summary = self.deduplicate_summary(combined_summary)

        # Append sentiment and emotion analysis results
        sentiment_summary = f"\n\nSentiment Analysis:\n{sentiment}"
        emotion_summary = f"\n\nEmotion Analysis:\n{', '.join([f'{e['label']} ({e['score']:.2f})' for e in emotion])}"
        final_summary = deduplicated_summary + sentiment_summary + emotion_summary

        return self.clean_summary(final_summary)

    def generate_summary_independent(self, text):
        """
        Generate a summary without sentiment or emotion metrics.

        Args:
            text (str): The text to summarize.

        Returns:
            str: A summarized version of the text.
        """
        print("Generating summary without sentiment or emotion metrics...")

        # Step 1: Split the text into chunks and summarize each chunk
        chunks = self.chunk_by_sentences(text)
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            print(f"Summarizing chunk {i + 1}/{len(chunks)}...")
            try:
                output = self.summarizer(
                    chunk,
                    max_length=300,  # Adjust for longer summaries if needed
                    min_length=100,
                    do_sample=False
                )[0]['summary_text']
                chunk_summaries.append(output)
            except Exception as e:
                print(f"Error summarizing chunk {i + 1}: {str(e)}")
                continue

        # Step 2: Combine all chunk summaries into a single text
        combined_summary = " ".join(chunk_summaries)
        print("Combined chunk summaries into a single text.")

        # Step 3: Deduplicate the combined summary
        deduplicated_summary = self.deduplicate_summary(combined_summary)
        print("Deduplicated the combined summary.")

        # Step 4: Perform a final summarization on the combined summary
        print("Performing a final summarization on the combined summary...")
        try:
            # Calculate the target length for the summary (40% of the deduplicated summary length)
            deduplicated_length = len(deduplicated_summary.split())  # Word count of deduplicated summary
            target_length = max(50, int(deduplicated_length * 0.4))  # Ensure a minimum target length of 50 words

            # Set max_length and min_length dynamically
            max_length = min(900, target_length + 50)  # Allow some flexibility above the target length
            min_length = max(30, target_length - 50)  # Ensure a minimum length of 30 words

            print(f"Target length: {target_length} words, max_length: {max_length}, min_length: {min_length}")

            # Perform the final summarization
            final_summary = self.summarizer(
                deduplicated_summary,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )[0]['summary_text']
        except Exception as e:
            print(f"Error during final summarization: {str(e)}")
            final_summary = deduplicated_summary  # Fallback to the deduplicated summary

        # Step 5: Clean and return the final summary
        return self.clean_summary(final_summary)
        
    def chunk_by_sentences(self, text, max_chars=1024):
        """
        Split the text into chunks based on sentences, ensuring each chunk is within the character limit.

        Args:
            text (str): The text to split into chunks.
            max_chars (int): Maximum number of characters per chunk.

        Returns:
            list: A list of text chunks.
        """
        # Ensure the 'punkt' resource is available
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')

        # Tokenize the text into sentences
        sentences = sent_tokenize(text)
        chunks, current_chunk = [], ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_chars:
                current_chunk += " " + sentence
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

    def clean_summary(self, summary):
        return summary.replace("\n", " ").replace("  ", " ")

    def deduplicate_summary(self, summary):
        """
        Remove repeated sentences from the summary.

        Args:
            summary (str): The generated summary.f

        Returns:
            str: A deduplicated version of the summary.
        """
        sentences = sent_tokenize(summary)
        seen = set()
        deduplicated_sentences = []
        for sentence in sentences:
            normalized_sentence = sentence.strip().lower()
            if normalized_sentence not in seen:
                deduplicated_sentences.append(sentence)
                seen.add(normalized_sentence)
        return " ".join(deduplicated_sentences)

    def preprocess_transcription(self, transcript):
        """
        Preprocess the transcription to remove redundant speaker labels and clean up the text.

        Args:
            transcript (str): The raw transcription text.

        Returns:
            str: The cleaned transcription text.
        """
        # Remove speaker labels like "Speaker A:" or "Host:"
        cleaned_transcript = transcript.replace("Speaker A:", "").replace("Host:", "").strip()

        # Remove excessive whitespace
        cleaned_transcript = " ".join(cleaned_transcript.split())

        return cleaned_transcript


if __name__ == "__main__":
    summarizer = ConversationSummarizer()
    transcription_file = r"D:\\Python Projects\\NLP_Customer_Audit_Project\\transcripts\\long_conversation.txt"
    output_dir = r"D:\\Python Projects\\NLP_Customer_Audit_Project\\transcripts"
    summary = summarizer.summarize_conversation(transcription_file, output_dir, input_type="transcription")
    print("----------------------------------")
    print("End Summary:")
    print(summary)
