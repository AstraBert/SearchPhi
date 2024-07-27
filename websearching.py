from googlesearch import search
from rake_nltk import Rake
from boilerpy3 import extractors
import json

extractor = extractors.ArticleExtractor()
r = Rake()

# Function to perform web search
def web_search(query, num_results=5):
    search_results = []
    for url in search(query, num_results=num_results):
        search_results.append(url)
    urls = list(set(search_results))
    jsonlike = {}
    for url in urls:
        try:
            content = extractor.get_content_from_url(url)
            r.extract_keywords_from_text(content)
            keywords = r.get_ranked_phrases()[:20]
            jsonlike.update({url: {"keywords": keywords}})
        except Exception:
            continue
    jsonstr = json.dumps(jsonlike)
    return jsonstr





