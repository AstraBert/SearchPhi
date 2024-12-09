from googlesearch import search
from rake_nltk import Rake
from boilerpy3 import extractors
import json
from langchain.text_splitter import CharacterTextSplitter
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from rag import NeuralSearcher
import random as r


encoder = SentenceTransformer("sentence-transformers/LaBSE")
splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
extractor = extractors.ArticleExtractor()
collection_name = f"cute_kitty_{r.randint(1,10000)}"
qdrant_client = QdrantClient("http://localhost:6333")
searcher = NeuralSearcher(collection_name, qdrant_client, encoder)
r = Rake()

qdrant_client.recreate_collection(
    collection_name=collection_name,
    vectors_config=models.VectorParams(
        size=encoder.get_sentence_embedding_dimension(),  # Vector size is defined by used model
        distance=models.Distance.COSINE,
    ),
)

def upload_to_qdrant(client: QdrantClient, collection_name: str, encoder: SentenceTransformer, text: str):
    try:
        chunks = splitter.split_text(text)
        docs = []
        for chunk in chunks:
            docs.append({"text": chunk})
        client.upload_points(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=idx,
                    vector=encoder.encode(doc["text"]).tolist(),
                    payload=doc,
                )
                for idx, doc in enumerate(docs)
            ],
        )
        return True
    except Exception as e:
        return False
    

# Function to perform web search
def web_search(query, num_results=5, enable_rag=False):
    global qdrant_client, encoder, collection_name
    search_results = []
    for url in search(query, num_results=num_results):
        search_results.append(url)
    urls = list(set(search_results))
    print(urls)
    jsonlike = {}
    finalcont = ""
    for url in urls:
        try:
            content = extractor.get_content_from_url(url)
            r.extract_keywords_from_text(content)
            keywords = r.get_ranked_phrases()[:20]
            jsonlike.update({url: {"keywords": keywords}})
            finalcont+=content+"\n\n"
        except Exception as e:
            print(f"ERROR! {e}")
            continue
    context = ""
    if enable_rag:
        res = searcher.search(finalcont, 3)
        for i in range(len(res)):
            context += res[i]["text"]+"\n\n"+"---------------"+"\n\n"
    truth = upload_to_qdrant(qdrant_client, collection_name, encoder, finalcont)
    jsonstr = json.dumps(jsonlike)
    if truth:
        if context:
            return "KEYWORDS:\n\n"+jsonstr+"\n\nCONTEXT:\n\n"+context, "Semantic memory successfully updated!"
        else:
            return "KEYWORDS:\n\n"+jsonstr, "Semantic memory successfully updated!"
    if context:
        return "KEYWORDS:\n\n"+jsonstr+"\n\nCONTEXT:\n\n"+context, "Something went wrong while updating semantic memory"
    return jsonstr, "Something went wrong while updating semantic memory"




