from transformers import pipeline
import matplotlib.pyplot as plt
import warnings
import re

warnings.filterwarnings("ignore")

# Initialize classifiers outside functions for efficiency
bias_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", framework="pt")
sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment", framework="pt")

# 1. Bias Detection
def detect_bias(text, threshold=0.7):
    """
    Detects if text is biased or neutral using zero-shot classification.
    Args:
        text (str): Input text to analyze.
        threshold (float): Confidence threshold for labeling (default: 0.7).
    Returns:
        dict: Bias label, confidence, and raw scores.
    """
    labels = ["biased", "neutral"]
    result = bias_classifier(text, labels, multi_label=False)
    top_label = result["labels"][0]
    top_score = result["scores"][0]
    final_label = top_label if top_score >= threshold else "uncertain"
    return {
        "text": text,
        "label": final_label,
        "confidence": top_score,
        "raw_scores": dict(zip(result["labels"], result["scores"]))
    }

# 2. Sentiment & Polarity (Updated with Star Ratings)
def analyze_article_sentiment(text):
    """
    Analyze blog/article-style content using star-based sentiment model.
    Maps star ratings to POSITIVE / NEUTRAL / NEGATIVE.
    Args:
        text (str): Input text to analyze.
    Returns:
        dict: Sentiment label, average stars, and label counts.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    star_to_label = {
        1: "NEGATIVE", 2: "NEGATIVE",
        3: "NEUTRAL",
        4: "POSITIVE", 5: "POSITIVE"
    }

    total_stars = 0
    label_count = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
    count = 0

    for sentence in sentences:
        if not sentence.strip():
            continue

        result = sentiment_analyzer(sentence)[0]
        stars = int(result['label'][0])  # e.g., '4 stars' → 4
        label = star_to_label[stars]

        total_stars += stars
        label_count[label] += 1
        count += 1

    avg_stars = round(total_stars / count, 2) if count > 0 else 0
    final_label = max(label_count, key=label_count.get) if count > 0 else "NEUTRAL"

    return {
        "text": text,
        "sentiment": final_label.lower(),  # "positive", "neutral", "negative"
        "avg_stars": avg_stars,
        "counts": label_count
    }

# 3. Combined Analysis with Visualization
def analyze_text(text):
    """
    Combines bias and sentiment analysis, then visualizes results.
    Args:
        text (str 
   
): Input text to analyze.
    """
    # Run bias and sentiment detection
    bias_result = detect_bias(text)
    sentiment_result = analyze_article_sentiment(text)

    # Combine results
    combined_result = {
        "text": text,
        "bias": bias_result["label"],
        "bias_confidence": bias_result["confidence"],
        "sentiment": sentiment_result["sentiment"],
        "avg_stars": sentiment_result["avg_stars"],
        "sentiment_counts": sentiment_result["counts"]
    }

    # Print results
    print(f"Text: {combined_result['text']}")
    print(f"Bias: {combined_result['bias']} (Confidence: {combined_result['bias_confidence']:.2f})")
    print(f"Sentiment: {combined_result['sentiment']} (Avg Stars: {combined_result['avg_stars']}/5)")
    print(f"Sentiment Breakdown: {combined_result['sentiment_counts']}")

    # Visualization: Bar chart for bias confidence and average stars
    labels = ["Bias Confidence", "Avg Stars"]
    values = [combined_result["bias_confidence"], combined_result["avg_stars"] / 5]  # Normalize stars to 0–1 for comparison
    colors = ["blue", "green" if combined_result["avg_stars"] >= 3 else "red"]

    plt.bar(labels, values, color=colors)
    plt.ylim(0, 1)  # Normalize to 0–1 scale for consistency
    plt.title(f"Analysis of: '{text}'")
    plt.ylabel("Score (Normalized)")
    plt.show()

    return combined_result

# Test the full pipeline
if __name__ == "__main__":
    test_texts = [
        "The moon landing was staged by NASA. It was a hoax!",
        "The Earth revolves around the Sun. This is a fact.",
        "Vaccines are a government conspiracy! They harm us all."
    ]

    for text in test_texts:
        analyze_text(text)
        print("-" * 50)