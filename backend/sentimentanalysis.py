# -*- coding: utf-8 -*-
"""sentiment_analysis.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1aG0iF5ssmAYD4zGe6LQGYmWC4R5D2Lgd
"""

from transformers import pipeline

# Load the sentiment analysis model
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def analyze_sentiment(text: str) -> dict:
    try:
        result = sentiment_analyzer(text[:512])[0]  # Limit input to 512 tokens

        label = result['label'].lower()
        score = round(result['score'], 2)

        # Convert to polarity-style contribution:
        # Neutral (0.5), Positive (0.7), Negative (0.3)
        if label == "positive":
            contribution_score = 0.7
        elif label == "negative":
            contribution_score = 0.3
        else:
            contribution_score = 0.5

        return {
            "label": label,
            "score": contribution_score,
            "reason": f"The model classified the tone as '{label}' with confidence {round(score * 100, 2)}%"
        }

    except Exception as e:
        return {
            "label": "error",
            "score": 0.0,
            "reason": str(e)
        }

