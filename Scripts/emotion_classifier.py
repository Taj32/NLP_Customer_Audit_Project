"""
Emotion Classifier Module

This module provides functionality to classify emotions in a transcript file using a pre-trained
transformer model. It includes the `EmotionClassifier` class and an example usage for testing.
"""

from transformers import pipeline
import os


class EmotionClassifier:
    """
    A class to classify emotions in a transcript file using a pre-trained transformer model.

    Attributes:
        transcript_path (str): Path to the transcript file.
        classifier (transformers.pipeline): Pre-trained emotion classification pipeline.
    """

    def __init__(self, transcript_path):
        """
        Initialize the EmotionClassifier with the path to the transcript file.

        Args:
            transcript_path (str): Path to the transcript file.
        """
        self.transcript_path = transcript_path
        self.classifier = pipeline(
            task="text-classification",
            model="SamLowe/roberta-base-go_emotions",
            top_k=None  # Return all emotion labels and their scores
        )

    def classify_emotions(self):
        """
        Classify emotions in the transcript file.

        Returns:
            list: A list of dictionaries containing emotion labels and their scores,
                  or None if the transcript file is not found.
        """
        # Check if the transcript file exists
        if not os.path.exists(self.transcript_path):
            print(f"File not found: {self.transcript_path}")
            return None

        # Load the transcript content
        with open(self.transcript_path, "r", encoding="utf-8") as f:
            transcript = f.read()

        # Truncate long text if needed (BERT models have a token limit of 512)
        chunk = transcript[:1000]

        # Run emotion classification using the pre-trained model
        results = self.classifier(chunk)

        # Print all emotions and their scores
        print("All emotions and their scores:")
        for result_list in results:  # Iterate through the outer list
            for result in result_list:  # Iterate through the inner list of dictionaries
                print(f"Label: {result['label']}, Score: {result['score']}")

        # Return the classification results
        return results


# Example usage
if __name__ == "__main__":
    """
    Example usage of the EmotionClassifier class.

    This script demonstrates how to classify emotions in a transcript file.
    """
    # Specify the path to the transcript file
    transcript_file = r"D:\Python Projects\NLP_Customer_Audit_Project\transcripts\transcription3.txt"

    # Create an instance of the EmotionClassifier class
    emotion_classifier = EmotionClassifier(transcript_file)

    # Classify emotions in the transcript
    emotion_results = emotion_classifier.classify_emotions()