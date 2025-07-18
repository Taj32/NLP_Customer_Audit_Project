"""
Customer Audit Pipeline

This script defines the `CustomerAuditPipeline` class, which provides functionality to record audio,
transcribe it, classify emotions, analyze sentiment, and summarize conversations. The pipeline integrates
multiple components to process customer interactions and generate insights.
"""

from datetime import datetime
import os
from dotenv import load_dotenv


# Import pipeline components
from audio_recorder import AudioRecorder
from emotion_classifier import EmotionClassifier
from sentiment_analyzer import SentimentAnalyzer
from transcriber import Transcriber
from summarizer import ConversationSummarizer
from api_uploader import get_token, post_conversation

import wave
import threading

load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")


class CustomerAuditPipeline:
    """
    A class to define the customer audit pipeline.

    Attributes:
        audio_recorder (AudioRecorder): Component for recording audio.
        transcriber (Transcriber): Component for transcribing audio.
        output_dir (str): Directory to save transcription files.
        summary_dir (str): Directory to save summary files.
    """

    def __init__(self):
        """
        Initialize the pipeline components and directories.
        """
        self.audio_recorder = AudioRecorder(output_folder="recordings")
        self.transcriber = Transcriber(model_name="base")
        self.output_dir = "transcripts"  # Directory to save transcriptions
        self.summary_dir = "summaries"  # Directory to save summaries
        self.processing_threads = []  # List to track active processing threads


    def save_summary(self, summary):
        """
        Save the generated summary to a text file in the summaries folder.

        Args:
            summary (str): The summary text to save.
        """
        # Ensure the summaries directory exists
        os.makedirs(self.summary_dir, exist_ok=True)

        # Generate a unique filename based on the current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = os.path.join(self.summary_dir, f"summary_{timestamp}.txt")

        # Save the summary to the file
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary)

        print(f"Summary saved to {summary_file}")

    def run_pipeline(self):
        """
        Run the full pipeline: Record audio, transcribe it, classify emotions, analyze sentiment, and summarize.
        """
        # Step 1: Record audio
        print("Step 1: Recording audio...")
        audio_file = self.audio_recorder.record_until_silence()
        if not audio_file:
            print("No audio recorded. Exiting pipeline.")
            return

        # Step 2: Transcribe audio
        print("\nStep 2: Transcribing audio...")
        audio_file = r"D:\Python Projects\NLP_Customer_Audit_Project\recordings\lean_interview.wav" # For testing purposes, remove later
        os.makedirs(self.output_dir, exist_ok=True)
        transcription_file = self.transcriber.transcribe_audio(audio_file, self.output_dir)
        if not transcription_file:
            print("Transcription failed. Exiting pipeline.")
            return

        # Check if the transcription is empty (ignoring separator and timestamp)
        with open(transcription_file, "r", encoding="utf-8") as f:
            transcription_lines = f.readlines()
        transcription_content = "".join(transcription_lines[:-2]).strip()  # Ignore the last two lines (separator and timestamp)
        if not transcription_content:
            print("Transcription is empty. Discarding this conversation.")
            os.remove(transcription_file)  # Delete the empty transcription file
            return

        # Step 3: Classify emotions
        print("\nStep 3: Classifying emotions...")
        emotion_classifier = EmotionClassifier(transcription_file)
        emotion_results = emotion_classifier.classify_emotions()
        if not emotion_results:
            print("Emotion classification failed. Exiting pipeline.")
            return

        # Step 4: Analyze sentiment
        print("\nStep 4: Analyzing sentiment...")
        sentiment_analyzer = SentimentAnalyzer(transcription_file)
        sentiment_scores = sentiment_analyzer.analyze_sentiment()
        if not sentiment_scores:
            print("Sentiment analysis failed. Exiting pipeline.")
            return
        
        # Extract the highest sentiment (ignoring compound)
        sentiment_label = max(
            {key: value for key, value in sentiment_scores.items() if key in ["neg", "neu", "pos"]},
            key=sentiment_scores.get
        )

        # Step 5: Summarize conversation
        print("\nStep 5: Summarizing conversation...")
        summarizer = ConversationSummarizer()
        summary = summarizer.summarize_conversation(transcription_file, None, input_type="transcription")
        if not summary:
            print("Summarization failed. Exiting pipeline.")
            return

        # Save the summary to a text file
        self.save_summary(summary)

        # Final Output
        print("\nPipeline completed successfully!")
        print("\nEmotion Results:")
        for result_list in emotion_results:
            for result in result_list:
                print(f"Label: {result['label']}, Score: {result['score']}")

        print("\nSentiment Scores:")
        print(sentiment_scores)

        print("\nSummary:")
        print(summary)

        print("\nStep 6: Pushing Conversation to Database (TESTING)")
        # Step 6: Pushing Conversation to Database (TESTING)
        token = get_token(EMAIL, PASSWORD)
        with open(transcription_file, "r", encoding="utf-8") as f:
            transcript_text = f.read()

        # Extract top 5 emotion scores
        emotion_scores = {
            e['label']: e['score']
            for e in sorted(
                [emotion for result_list in emotion_results for emotion in result_list],
                key=lambda x: x['score'],
                reverse=True
            )[:5]  # Take the top 5 emotions
        }
        
        # Extract the highest sentiment (ignoring compound) and reword it
        sentiment_mapping = {"neg": "negative", "neu": "neutral", "pos": "positive"}
        sentiment_label = max(
            {key: value for key, value in sentiment_scores.items() if key in sentiment_mapping},
            key=sentiment_scores.get
        )
        sentiment_label = sentiment_mapping[sentiment_label]  # Map to full name


        # Post to API
        print("Uploading to backend...")
        try:
            convo = post_conversation(token, transcript_text, sentiment_label, emotion_scores, summary)
            print("Uploaded conversation ID:", convo["id"])
        except Exception as e:
            print("Upload failed:", str(e))
        

     
    def process_conversation(self, audio_frames):
        """
        Process a single conversation: Transcribe, classify emotions, analyze sentiment, and summarize.

        Args:
            audio_frames (list): List of audio frames for the conversation.
        """
        def process_task():
            # Save the audio frames to a temporary file
            temp_audio_file = os.path.join(self.audio_recorder.output_folder, "temp_conversation.wav")
            with wave.open(temp_audio_file, 'wb') as wf:
                wf.setnchannels(self.audio_recorder.channels)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(self.audio_recorder.rate)
                wf.writeframes(b''.join(audio_frames))

            # Transcribe the audio
            print("\nTranscribing conversation...")
            transcription_file = self.transcriber.transcribe_audio(temp_audio_file, self.output_dir)
            if not transcription_file:
                print("Transcription failed.")
                return
            
            # Check if the transcription is empty (ignoring separator and timestamp)
            with open(transcription_file, "r", encoding="utf-8") as f:
                transcription_lines = f.readlines()
            transcription_content = "".join(transcription_lines[:-2]).strip()  # Ignore the last two lines (separator and timestamp)
            if not transcription_content:
                print("Transcription is empty. Discarding this conversation.")
                os.remove(transcription_file)  # Delete the empty transcription file
                return


            # Classify emotions
            print("\nClassifying emotions...")
            emotion_classifier = EmotionClassifier(transcription_file)
            emotion_results = emotion_classifier.classify_emotions()

            # Analyze sentiment
            print("\nAnalyzing sentiment...")
            sentiment_analyzer = SentimentAnalyzer(transcription_file)
            sentiment_scores = sentiment_analyzer.analyze_sentiment()

            # Summarize conversation
            print("\nSummarizing conversation...")
            summarizer = ConversationSummarizer()
            summary = summarizer.summarize_conversation(transcription_file, None, input_type="transcription")

            # Save the summary
            self.save_summary(summary)

            # Print results
            print("\nEmotion Results:")
            for result_list in emotion_results:
                for result in result_list:
                    print(f"Label: {result['label']}, Score: {result['score']}")

            print("\nSentiment Scores:")
            print(sentiment_scores)

            print("\nSummary:")
            print(summary)

        # Start a new thread for processing the conversation
        processing_thread = threading.Thread(target=process_task)
        processing_thread.start()
        self.processing_threads.append(processing_thread)
        
    def run_continuous_pipeline(self):
        """
        Run the pipeline continuously, processing conversations on the fly.
        """
        print("Starting continuous pipeline...")
        self.audio_recorder.listen_continuously(self.process_conversation)


# Run the pipeline
if __name__ == "__main__":
    pipeline = CustomerAuditPipeline()
    pipeline.run_pipeline() # For purpose of single run, of the pipeline
    # pipeline.run_continuous_pipeline() # For continuous processing of conversations