from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os

class SentimentAnalyzer:
    def __init__(self, transcript_path):
        """
        Initialize the SentimentAnalyzer with the path to the transcript file.
        """
        self.transcript_path = transcript_path
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze_sentiment(self):
        """
        Analyze the sentiment of the transcript file.

        :return: A dictionary containing sentiment scores.
        """
        if not os.path.exists(self.transcript_path):
            print(f"File not found: {self.transcript_path}")
            return None

        # Load the transcript
        with open(self.transcript_path, "r", encoding="utf-8") as f:
            transcript = f.read()

        # Get sentiment scores
        scores = self.analyzer.polarity_scores(transcript)

        # Print the scores
        print("Sentiment Scores:", scores)

        # Return the scores
        return scores

# Example usage
if __name__ == "__main__":
    # Specify the path to the transcript file
    transcript_file = r"D:\Python Projects\NLP_Customer_Audit_Project\transcripts\transcription2.txt"

    # Create an instance of the SentimentAnalyzer class
    sentiment_analyzer = SentimentAnalyzer(transcript_file)

    # Analyze the sentiment
    sentiment_scores = sentiment_analyzer.analyze_sentiment()