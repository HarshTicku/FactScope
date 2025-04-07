import sys
import time
from googlesearch import search
from newspaper import Article, Config
from factextractor import extract_facts_from_text, extract_text_from_url

def fetch_related_articles(query, num_results=5):
    """Fetch top 5 related articles from Google based on a query."""
    articles = []
    for i, url in enumerate(search(query, num_results=num_results)):
        try:
            config = Config()
            config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            article = Article(url, config=config)
            article.download()
            article.parse()
            articles.append((url, article.title))
        except Exception as e:
            print(f"❌ Failed to fetch article from {url}: {e}")
        time.sleep(1)
    return articles

def process_input(input_value):
    """Process the input based on its type (URL, text, or claim)."""
    # Check if it's a URL
    if input_value.startswith("http://") or input_value.startswith("https://"):
        print("Processing URL input...")
        text = extract_text_from_url(input_value)
        if not text:
            return None
        facts = extract_facts_from_text(text)
        print(f"\nExtracted Facts:")
        for idx, fact in enumerate(facts, 1):
            print(f"{idx}. {fact}")
        search_query = " ".join(facts)
    
    # Check if it's a claim (short input, < 50 characters)
    elif len(input_value) < 50:
        print("Processing claim input...")
        search_query = input_value
        print(f"\nClaim: {search_query}")
    
    # Otherwise, treat as pasted article text
    else:
        print("Processing text input...")
        facts = extract_facts_from_text(input_value)
        print(f"\nExtracted Facts:")
        for idx, fact in enumerate(facts, 1):
            print(f"{idx}. {fact}")
        search_query = " ".join(facts)

    # Fetch related articles
    print(f"\nSearch Query: {search_query}")
    related_articles = fetch_related_articles(search_query)
    return related_articles

def main():
    if len(sys.argv) != 2:
        print("Usage: python scraper.py <URL, text, or claim>")
        sys.exit(1)

    input_value = sys.argv[1]
    related_articles = process_input(input_value)

    if related_articles:
        print("\nTop 5 Related Articles:")
        for idx, (url, title) in enumerate(related_articles, 1):
            print(f"{idx}. {title}")
            print(f"   {url}\n")
    else:
        print("Failed to fetch articles.")

if __name__ == "__main__":
    main()