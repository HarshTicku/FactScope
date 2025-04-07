import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def extract_facts_from_text(text, num_facts=3):
    """Extract meaningful facts using NER and sentence context."""
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    entity_set = set(ent[0] for ent in entities)
    
    facts = []
    for sent in doc.sents:
        if any(entity in sent.text for entity in entity_set):
            facts.append(sent.text.strip())
        if len(facts) >= num_facts:
            break
    
    if len(facts) < num_facts:
        for sent in doc.sents:
            if sent.text.strip() not in facts:
                facts.append(sent.text.strip())
                if len(facts) >= num_facts:
                    break
    
    return facts

def extract_text_from_url(url):
    """Extract text from a given URL using newspaper3k."""
    from newspaper import Article, Config  # Import here to keep dependencies minimal
    try:
        config = Config()
        config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        article = Article(url, config=config)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"❌ Failed to extract text from {url}: {e}")
        return None