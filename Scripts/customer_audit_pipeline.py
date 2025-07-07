# import AudioRecorder
# import Transcriber
# import EmotionClassifier
# import SentimentAnalyzer
from datetime import datetime
import os

from audio_recorder import AudioRecorder
from emotion_classifier import EmotionClassifier
from sentiment_analyzer import SentimentAnalyzer
from transcriber import Transcriber
from summarizer import ConversationSummarizer

class CustomerAuditPipeline:
    def __init__(self):
        """
        Initialize the pipeline components.
        """
        self.audio_recorder = AudioRecorder(output_folder="recordings")
        self.transcriber = Transcriber(model_name="base")
        self.output_dir = "transcripts"
        self.summary_dir = "summaries"  # Directory to save summaries
        
    def save_summary(self, summary):
        """
        Save the generated summary to a text file in the summaries folder.

        :param summary: The summary text to save.
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
        Run the full pipeline: Record audio, transcribe it, classify emotions, and analyze sentiment.
        """
        # Step 1: Record audio
        print("Step 1: Recording audio...")
        audio_file = self.audio_recorder.record_until_silence()
        if not audio_file:
            print("No audio recorded. Exiting pipeline.")
            return

        # Step 2: Transcribe audio
        audio_file = r"D:\Python Projects\NLP_Customer_Audit_Project\recordings\lean_interview.wav"
        print("\nStep 2: Transcribing audio...")
        os.makedirs(self.output_dir, exist_ok=True)
        transcription_file = self.transcriber.transcribe_audio(audio_file, self.output_dir)
        if not transcription_file:
            print("Transcription failed. Exiting pipeline.")
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

        # Step 5: Summarize conversation
        print("\nStep 5: Summarizing conversation...")
        summarizer = ConversationSummarizer()
        #output_dir = r"D:\Python Projects\NLP_Customer_Audit_Project\transcripts"
        summary = summarizer.summarize_conversation(transcription_file, None, input_type="transcription")
        #summary = self.summarizer.generate_summary(transcription_file, self.output_dir, input_type="transcription")
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

# Run the pipeline
if __name__ == "__main__":
    pipeline = CustomerAuditPipeline()
    pipeline.run_pipeline()