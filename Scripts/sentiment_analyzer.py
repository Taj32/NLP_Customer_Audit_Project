from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# Load analyzer
analyzer = SentimentIntensityAnalyzer()

# Example input (could be loaded from file)
with open(r"D:\Python Projects\NLP_Customer_Audit_Project\transcripts\transcription2.txt", "r") as f:
    transcript = f.read()

# Get sentiment scores
scores = analyzer.polarity_scores(transcript)
analyzer.polarity_scores(transcript)

print(scores)