from duckduckgo_search import DDGS
from typing import Dict
from crawl4ai import AsyncWebCrawler
from qdrantRag import upload_text_to_qdrant, sparse_encoder, dense_encoder, client, NeuralSearcher
from rake_nltk import Rake
from langchain_text_splitters import MarkdownTextSplitter
import time

searcher = DDGS()
splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=0)
neural_searcher = NeuralSearcher("browser_memory", client, dense_encoder, sparse_encoder)
rake_ext = Rake()

def web_search(prompt: str) -> Dict[str, str]:
    rake_ext.extract_keywords_from_text(prompt)
    keys = rake_ext.get_ranked_phrases()[:2]
    text = " ".join(keys)
    results = searcher.text(text, max_results=5)
    return results

async def web_crawling(url: str) -> str:
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url,
        )
    return result.markdown

async def results_to_db(search_results: Dict[str, str]) -> None:
    c = 0
    for res in search_results:
        url = res["href"]
        text = await web_crawling(url)
        a = time.time()
        split_texts = splitter.split_text(text)
        a = time.time()
        for t in split_texts:
            upload_text_to_qdrant(client, "browser_memory", t, c)
            c+=1
        b = time.time()

def search_db(query: str):
    context = neural_searcher.search_text(query, 5)
    return context

        




