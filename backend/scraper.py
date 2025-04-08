# -*- coding: utf-8 -*-
"""scraper.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1GQwZFRwFG0i4VNwi6QA3yYV9eBRWnouD
"""

from newspaper import Article
from googlesearch import search
import random
import socket

# 🔍 Search and scrape articles from web based on keyword or claim
def get_articles_from_keyword(query: str, max_articles: int = 5) -> list:
    results = []
    socket.setdefaulttimeout(5)  # Set timeout for article downloads
    try:
        urls = list(search(query, num_results=max_articles * 2))
        random.shuffle(urls)
        count = 0
        for url in urls:
            if count >= max_articles:
                break
            try:
                article = Article(url)
                article.download()
                article.parse()
                content = article.text.strip()
                if len(content) > 300:
                    results.append(content)
                    count += 1
                    print(f"✅ Article {count} added from: {url}")
            except Exception as e:
                print(f"❌ Skipped URL: {url} due to error: {e}")
                continue
    except Exception as e:
        print("❌ Search failed:", e)

    return results

