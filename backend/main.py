import os
from scraper import get_articles_from_keyword
from summarizer import summarize_text
from factchecker import fact_check_claim_with_articles
from sentimentanalysis import analyze_sentiment
from biasdetector import detect_bias
from similaritycheck import check_similarity
from credeblityscore import calculate_credibility
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import Optional
import time

app = FastAPI(title="Content Credibility API")

# Add CORS middleware to allow requests from the Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (you might want to restrict this in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ContentRequest(BaseModel):
    text: str
    api_key: Optional[str] = None

def process_url_or_text(input_text: str, is_url: bool = False) -> dict:
    """
    Process either a URL, article text, or a claim.
    Returns a comprehensive analysis.
    """
    try:
        # If URL is provided, we need to fetch content first
        if is_url and input_text.startswith(('http://', 'https://')):
            # Extract content from URL
            from newspaper import Article
            article = Article(input_text)
            article.download()
            article.parse()
            content = article.text
            title = article.title
        else:
            content = input_text
            title = "User provided content"
            
        # Create a search query from the content
        query = content[:200] if len(content) > 200 else content
            
        # Step 1: Summarize the input content
        summary_result = summarize_text(content)
        summary = summary_result["summary"]
        
        # Step 2: Fetch related articles
        print("Searching for and scraping related articles...")
        scraped_articles = get_articles_from_keyword(query, max_articles=5)
        
        # Get related article URLs and titles for the frontend
        related_articles = []
        # In a real implementation, you would store and return URLs and titles from your scraper
        
        # Step 3: Check similarity with other sources
        print("Analyzing similarity with other sources...")
        similarity_result = check_similarity(content, scraped_articles)
        
        # Step 4: Fact check with retrieved articles
        print("Fact checking content...")
        fact_check_result = fact_check_claim_with_articles(content, scraped_articles)
        
        # Step 5: Analyze sentiment
        print("Analyzing sentiment...")
        sentiment_result = analyze_sentiment(content)
        
        # Step 6: Analyze bias
        print("Detecting bias...")
        bias_result = detect_bias(content)
        
        # Step 7: Calculate credibility score
        print("Calculating overall credibility score...")
        modules = {
            "fact_checker": {"score": fact_check_result["score"]},
            "similarity_checker": {"score": similarity_result["score"]},
            "bias_detector": {"score": bias_result["score"]}, 
            "sentiment_analysis": {"score": sentiment_result["score"]}
        }
        credibility_result = calculate_credibility(modules)
        credibility_score = credibility_result["final_score"]
                
        # Format response for the frontend
        return {
            "title": title,
            "summary": summary,
            "final_credibility_score": credibility_score,  # Named to match frontend expectations
            "credibility_breakdown": credibility_result["breakdown"],
            "fact_check": {
                "verdict": fact_check_result["verdict"],
                "score": fact_check_result["score"],
                "explanation": fact_check_result["reason"]
            },
            "similarity": {
                "label": similarity_result["label"],
                "score": similarity_result["score"],
                "explanation": similarity_result["reason"]
            },
            "sentiment": {
                "label": sentiment_result["label"],
                "score": sentiment_result["score"],
                "explanation": sentiment_result["reason"]
            },
            "bias": {
                "label": bias_result["label"],
                "score": bias_result["score"],
                "explanation": bias_result["reason"]
            },
            "related_articles": related_articles
        }
        
    except Exception as e:
        print(f"Error processing content: {str(e)}")
        return {
            "error": str(e),
            "final_credibility_score": 0.0
        }

@app.post("/evaluate")
async def evaluate_content(request: ContentRequest):
    """
    API endpoint for the Chrome extension to evaluate content
    """
    # Determine if input is URL or text
    is_url = request.text.startswith(('http://', 'https://'))
    
    # Process the content
    result = process_url_or_text(request.text, is_url)
    
    return result

@app.post("/summarize")
async def summarize_content(request: ContentRequest):
    """
    API endpoint for quick summarization
    """
    try:
        result = summarize_text(request.text)
        return {
            "summary": result["summary"],
            "success": True
        }
    except Exception as e:
        return {
            "summary": str(e),
            "success": False
        }

@app.get("/")
async def root():
    """
    Root endpoint to check if API is running
    """
    return {
        "message": "Content Credibility API is running",
        "version": "1.0.0",
        "endpoints": ["/evaluate", "/summarize"]
    }

def run_command_line():
    """
    Original command line interface
    """
    print("=" * 60)
    print("CONTENT CREDIBILITY ANALYZER")
    print("=" * 60)
    print("This tool analyzes the credibility of content based on")
    print("fact-checking, similarity to other sources, sentiment, and bias.")
    print("=" * 60)
    
    print("Select input type:")
    print("1. URL")
    print("2. Article text")
    print("3. Claim/statement")
    
    choice = input("Enter your choice (1-3): ")
    
    if choice == "1":
        input_data = input("Enter URL: ")
        is_url = True
    else:
        print("Enter your text (press Enter twice when done):")
        lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            lines.append(line)
        input_data = "\n".join(lines)
        is_url = False
    
    print("\nAnalyzing content... This may take a few moments.\n")
    
    result = process_url_or_text(input_data, is_url)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    # Display results
    print("\n" + "=" * 60)
    print(f"ANALYSIS RESULTS")
    print("=" * 60)
    
    print(f"TITLE: {result['title']}")
    print("\nSUMMARY:")
    print(result['summary'])
    
    print("\nCREDIBILITY SCORE:")
    score = result['final_credibility_score']
    print(f"{score:.2f}/1.00")

    # Display breakdown if available
    if "credibility_breakdown" in result:
        print("\nCREDIBILITY BREAKDOWN:")
        for module, details in result['credibility_breakdown'].items():
            print(f"- {module.replace('_', ' ').title()}: {details['score']:.2f} (weight: {details['weight']:.2f})")
    
    print("\nFACT CHECK RESULTS:")
    print(f"Verdict: {result['fact_check']['verdict'].upper()}")
    print(f"Confidence: {result['fact_check']['score']:.2f}")
    print(f"Reason: {result['fact_check']['explanation']}")
    
    print("\nSIMILARITY ANALYSIS:")
    print(f"Finding: {result['similarity']['label'].replace('_', ' ').upper()}")
    print(f"Score: {result['similarity']['score']:.2f}")
    print(f"Reason: {result['similarity']['explanation']}")
    
    print("\nSENTIMENT ANALYSIS:")
    print(f"Tone: {result['sentiment']['label'].upper()}")
    print(f"Reason: {result['sentiment']['explanation']}")
    
    print("\nBIAS ANALYSIS:")
    print(f"Finding: {result['bias']['label'].upper()}")
    print(f"Score: {result['bias']['score']:.2f}")
    print(f"Reason: {result['bias']['explanation']}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    import sys
    
    # Check if run with --server flag
    if len(sys.argv) > 1 and sys.argv[1] == '--server':
        # Run as API server
        print("Starting Content Credibility API server at http://localhost:8000")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        # Run as command line tool
        run_command_line()