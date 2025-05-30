# -*- coding: utf-8 -*-
"""summarizer.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1V1XUJp2cw9wUpDrwNNH_DtURt111zrFK
"""

from transformers import pipeline

# Load summarizer
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text: str, max_length: int = 200, chunk_size: int = 1000, overlap: int = 100) -> dict:
    try:
        summaries = []
        start = 0
        total_len = len(text)

        # Split long text into overlapping chunks
        while start < total_len:
            end = start + chunk_size
            chunk = text[start:end]
            summary = summarizer(chunk, max_length=max_length, min_length=30, do_sample=False)[0]["summary_text"]
            summaries.append(summary.strip())
            start = end - overlap  # move with overlap

        # Combine summaries into one
        final_summary = " ".join(summaries)

        return {
            "summary": final_summary,
            "length": len(final_summary.split()),
            "reason": f"Summarized in {len(summaries)} chunks. Final summary has {len(final_summary.split())} words."
        }

    except Exception as e:
        return {
            "summary": "",
            "length": 0,
            "reason": str(e)
        }