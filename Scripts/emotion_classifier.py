from transformers import pipeline
import os

class EmotionClassifier:
    def __init__(self, transcript_path):
        """
        Initialize the EmotionClassifier with the path to the transcript file.
        """
        self.transcript_path = transcript_path
        self.classifier = pipeline(task="text-classification",
                                   model="SamLowe/roberta-base-go_emotions",
                                   top_k=None)

    def classify_emotions(self):
        """
        Classify emotions in the transcript file.

        :return: A list of dictionaries containing emotion labels and their scores.
        """
        if not os.path.exists(self.transcript_path):
            print(f"File not found: {self.transcript_path}")
            return None

        # Load the transcript
        with open(self.transcript_path, "r", encoding="utf-8") as f:
            transcript = f.read()

        # Truncate long text if needed (BERT has a token limit of 512)
        chunk = transcript[:1000]

        # Run emotion classification
        results = self.classifier(chunk)

        # Print all emotions and their scores
        print("All emotions and their scores:")
        for result_list in results:  # Iterate through the outer list
            for result in result_list:  # Iterate through the inner list of dictionaries
                print(f"Label: {result['label']}, Score: {result['score']}")

        # Return the results
        return results

# Example usage
if __name__ == "__main__":
    # Specify the path to the transcript file
    transcript_file = r"D:\Python Projects\NLP_Customer_Audit_Project\transcripts\transcription3.txt"

    # Create an instance of the EmotionClassifier class
    emotion_classifier = EmotionClassifier(transcript_file)

    # Classify emotions
    emotion_results = emotion_classifier.classify_emotions()