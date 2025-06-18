from transformers import pipeline

# Load emotion classification model
classifier = pipeline(task="text-classification",
                        model="SamLowe/roberta-base-go_emotions",
                        top_k=None)


# Load your transcript
with open("transcripts/transcription.txt", "r") as f:
    transcript = f.read()

# Truncate long text if needed (BERT has a token limit of 512)
chunk = transcript[:1000]

# Run emotion classification
results = classifier(chunk)

# Show the top emotion (highest score)
print("All emotions and their scores:")
for result_list in results:  # Iterate through the outer list
    for result in result_list:  # Iterate through the inner list of dictionaries
        print(f"Label: {result['label']}, Score: {result['score']}")