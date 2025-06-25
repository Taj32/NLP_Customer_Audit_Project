# import AudioRecorder
# import Transcriber
# import EmotionClassifier
# import SentimentAnalyzer
import os

from audio_recorder import AudioRecorder
from emotion_classifier import EmotionClassifier
from sentiment_analyzer import SentimentAnalyzer
from transcriber import Transcriber

class CustomerAuditPipeline:
    def __init__(self):
        """
        Initialize the pipeline components.
        """
        self.audio_recorder = AudioRecorder(output_folder="recordings")
        self.transcriber = Transcriber(model_name="base")
        self.output_dir = "transcripts"

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

        # Final Output
        print("\nPipeline completed successfully!")
        print("\nEmotion Results:")
        for result_list in emotion_results:
            for result in result_list:
                print(f"Label: {result['label']}, Score: {result['score']}")

        print("\nSentiment Scores:")
        print(sentiment_scores)

# Run the pipeline
if __name__ == "__main__":
    pipeline = CustomerAuditPipeline()
    pipeline.run_pipeline()