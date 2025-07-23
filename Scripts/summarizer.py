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

        # Initialize the LED summarization pipeline
        model_name = "pszemraj/led-large-book-summary"
        self.summarizer = pipeline(
            "summarization",
            model=model_name,
            device=0 if torch.cuda.is_available() else -1  # Use GPU if available
        )

    def summarize_conversation(self, transcription_path, output_dir, input_type="audio"):
        # Load and preprocess the transcription
        if not os.path.exists(transcription_path):
            print(f"Error: Transcription file not found at {transcription_path}")
            return None

        with open(transcription_path, "r", encoding="utf-8") as f:
            transcript = f.read().strip()

        if not transcript:
            print("Error: Transcription file is empty.")
            return None

        # Preprocess the text for the LED model
        transcript = self.preprocess_text(transcript)

        # Generate the summary
        print("---------------------")
        print(transcript)
        print("---------------------")
        print("Summarizing transcription...")
        summary = self.generate_summary_independent(transcript)

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
        Generate a summary without sentiment or emotion metrics, with a length approximately 40-45% of the transcription.

        Args:
            text (str): The text to summarize.

        Returns:
            str: A summarized version of the text.
        """
        print("Generating summary without sentiment or emotion metrics...")

        # Ensure the input text is not empty
        if not text.strip():
            print("Error: Input text is empty.")
            return "No content to summarize."

        # Calculate the target length for the summary
        word_count = len(text.split())  # Count the number of words in the transcription
        target_length = max(50, int(word_count * 0.3))  # Ensure a minimum target length of 50 words
        max_length = min(1024, target_length + 50)  # Allow some flexibility above the target length
        min_length = max(30, target_length - 50)  # Ensure a minimum length of 30 words

        print(f"Word count: {word_count}, Target length: {target_length} words")
        print(f"Summarization parameters -> min_length: {min_length}, max_length: {max_length}")

        # Perform summarization using the LED model
        try:
            print("Summarizing the transcription...")
            final_summary = self.summarizer(
                text,
                min_length=min_length,
                max_length=max_length,
                no_repeat_ngram_size=4,
                encoder_no_repeat_ngram_size=3,
                repetition_penalty=3.5,
                num_beams=4,
                early_stopping=True
            )[0]['summary_text']
        except Exception as e:
            print(f"Error during summarization: {str(e)}")
            final_summary = "Summarization failed due to an error."

        # Clean and return the final summary
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

    def preprocess_text(self, text, max_tokens=16384):
        """
        Preprocess the text to ensure it fits within the model's token limit.

        Args:
            text (str): The input text.
            max_tokens (int): Maximum number of tokens allowed by the model.

        Returns:
            str: The truncated text.
        """
        tokenized_input = self.summarizer.tokenizer(
            text,
            truncation=True,
            max_length=max_tokens,
            return_tensors="pt"
        )
        return self.summarizer.tokenizer.decode(tokenized_input["input_ids"][0], skip_special_tokens=True)


if __name__ == "__main__":
    summarizer = ConversationSummarizer()
    transcription_file = r"D:\\Python Projects\\NLP_Customer_Audit_Project\\transcripts\\long_conversation.txt"
    output_dir = r"D:\\Python Projects\\NLP_Customer_Audit_Project\\transcripts"
    summary = summarizer.summarize_conversation(transcription_file, output_dir, input_type="transcription")
    print("----------------------------------")
    print("End Summary:")
    print(summary)
