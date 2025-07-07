"""
Sentiment Analyzer Module

This module provides functionality to analyze the sentiment of a transcript file using the VADER
SentimentIntensityAnalyzer. It includes the `SentimentAnalyzer` class and an example usage for testing.
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os


class SentimentAnalyzer:
    """
    A class to analyze the sentiment of a transcript file using the VADER SentimentIntensityAnalyzer.

    Attributes:
        transcript_path (str): Path to the transcript file.
        analyzer (SentimentIntensityAnalyzer): Instance of the VADER sentiment analyzer.
    """

    def __init__(self, transcript_path):
        """
        Initialize the SentimentAnalyzer with the path to the transcript file.

        Args:
            transcript_path (str): Path to the transcript file.
        """
        self.transcript_path = transcript_path
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze_sentiment(self):
        """
        Analyze the sentiment of the transcript file.

        Returns:
            dict: A dictionary containing sentiment scores (positive, neutral, negative, and compound).
                  Returns None if the transcript file is not found.
        """
        # Check if the transcript file exists
        if not os.path.exists(self.transcript_path):
            print(f"File not found: {self.transcript_path}")
            return None

        # Load the transcript content
        with open(self.transcript_path, "r", encoding="utf-8") as f:
            transcript = f.read()

        # Get sentiment scores using VADER
        scores = self.analyzer.polarity_scores(transcript)

        # Print the sentiment scores
        print("Sentiment Scores:", scores)

        # Return the sentiment scores
        return scores


# Example usage
if __name__ == "__main__":
    """
    Example usage of the SentimentAnalyzer class.

    This script demonstrates how to analyze the sentiment of a transcript file.
    """
    # Specify the path to the transcript file
    transcript_file = r"D:\Python Projects\NLP_Customer_Audit_Project\transcripts\transcription2.txt"

    # Create an instance of the SentimentAnalyzer class
    sentiment_analyzer = SentimentAnalyzer(transcript_file)

    # Analyze the sentiment of the transcript
    sentiment_scores = sentiment_analyzer.analyze_sentiment()