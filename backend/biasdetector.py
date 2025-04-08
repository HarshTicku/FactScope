# -*- coding: utf-8 -*-
"""bias_detector.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1gJ2Jf0B69Uv5KzDhHHzJugf9ZIYrG-Ih
"""

from transformers import pipeline

# Load zero-shot classifier (offline load for better performance)
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Pre-defined labels
labels = ["biased", "neutral"]

def detect_bias(text: str) -> dict:
    try:
        result = classifier(text, candidate_labels=labels)
        label = result["labels"][0]
        score = result["scores"][0]

        # Convert to contribution-style score (neutral → higher)
        if label == "neutral":
            final_score = round(score, 2)
        else:  # biased
            final_score = round(1 - score, 2)

        return {
            "label": label,
            "score": final_score,
            "reason": f"Model classified the content as '{label}' with confidence {round(score * 100, 2)}%"
        }

    except Exception as e:
        return {
            "label": "error",
            "score": 0.0,
            "reason": str(e)
        }