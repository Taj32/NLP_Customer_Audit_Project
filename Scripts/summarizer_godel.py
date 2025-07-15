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
from nltk import sent_tokenize


class ConversationSummarizer:
    def __init__(self):
        self.transcriber = Transcriber(model_name="base")
        print("CUDA Availability:", torch.cuda.is_available())
        if torch.cuda.is_available():
            print("CUDA Device Name:", torch.cuda.get_device_name(0))

        # Initialize GODEL summarization pipeline
        model_name = "microsoft/GODEL-v1_1-large-seq2seq"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        self.summarizer = pipeline(
            "text2text-generation",
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
            summary = self.generate_summary_independent(transcript)
        else:
            summary = self.generate_summary(transcript, sentiment_score, emotion_results)

        print("\n\n[[Summary]]:")
        print(summary)
        return summary

    def summarize_day(self, day, summaries_dir="summaries"):
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
        overall_summary = self.summarizer(
            f"Summarize the following conversations:\n\n{combined_summaries}",
            max_length=500,
            min_length=200,
            do_sample=False
        )[0]['generated_text']

        return self.clean_summary(overall_summary)

    def generate_summary(self, text, sentiment, emotion):
        chunks = self.chunk_by_sentences(text)
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            print(f"Summarizing chunk {i + 1}/{len(chunks)}...")
            prompt = f"Summarize the following conversation:\n\n{chunk}"
            try:
                output = self.summarizer(prompt, max_length=300, min_length=100, do_sample=False)[0]['generated_text']
                chunk_summaries.append(output)
            except Exception as e:
                print(f"Error summarizing chunk {i + 1}: {str(e)}")
                continue

        combined_summary = " ".join(chunk_summaries)
        sentiment_summary = f"\n\nSentiment Analysis:\n{sentiment}"
        emotion_summary = f"\n\nEmotion Analysis:\n{', '.join([f'{e['label']} ({e['score']:.2f})' for e in emotion])}"
        return self.clean_summary(combined_summary + sentiment_summary + emotion_summary)

    def generate_summary_independent(self, text):
        chunks = self.chunk_by_sentences(text)
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            print(f"Summarizing chunk {i + 1}/{len(chunks)}...")
            prompt = f"Summarize the following conversation:\n\n{chunk}"
            try:
                output = self.summarizer(prompt, max_length=300, min_length=100, do_sample=False)[0]['generated_text']
                chunk_summaries.append(output)
            except Exception as e:
                print(f"Error summarizing chunk {i + 1}: {str(e)}")
                continue

        return self.clean_summary(" ".join(chunk_summaries))

    def chunk_by_sentences(self, text, max_chars=1024):
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


if __name__ == "__main__":
    summarizer = ConversationSummarizer()
    transcription_file = r"D:\\Python Projects\\NLP_Customer_Audit_Project\\transcripts\\long_conversation.txt"
    output_dir = r"D:\\Python Projects\\NLP_Customer_Audit_Project\\transcripts"
    summary = summarizer.summarize_conversation(transcription_file, output_dir, input_type="transcription")
    print("----------------------------------")
    print("End Summary:")
    print(summary)
