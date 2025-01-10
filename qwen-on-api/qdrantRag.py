from qdrant_client import QdrantClient, models
from fastembed import SparseTextEmbedding
from sentence_transformers import SentenceTransformer
import torch
import uuid
from typing import List, Dict

## GLOBALS

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
dense_encoder = SentenceTransformer("sentence-transformers/LaBSE").to(device)
sparse_encoder = SparseTextEmbedding(model_name="prithivida/Splade_PP_en_v1")

client = QdrantClient("http://localhost:6333")

client.recreate_collection(
    collection_name="browser_memory",
    vectors_config={},
    sparse_vectors_config={"sparse-text": models.SparseVectorParams(
        index=models.SparseIndexParams(
            on_disk=False
        )
    )}
)

client.recreate_collection(
    collection_name="semantic_cache",
    vectors_config=models.VectorParams(
        size=768,  # Vector size is defined by used model
        distance=models.Distance.COSINE,
    ),
)

## FUNCTIONS

def reranking(docs: List[str], query: str, dense_encoder: SentenceTransformer):
    query_vector = dense_encoder.encode(query)
    docs_vector = dense_encoder.encode(docs)
    similarities = dense_encoder.similarity(docs_vector, query_vector)
    sims = [float(sim[0]) for sim in similarities]
    text2sims = {docs[i]: sims[i] for i in range(len(sims))}
    sorted_items = sorted(text2sims.items(), key=lambda x: x[1], reverse=True)
    return sorted_items[0][0]

def get_sparse_embedding(text: str, model: SparseTextEmbedding):
    embeddings = list(model.embed(text))
    vector = {f"sparse-text": models.SparseVector(indices=embeddings[0].indices, values=embeddings[0].values)}
    return vector

def get_query_sparse_embedding(text: str, model: SparseTextEmbedding):
    embeddings = list(model.embed(text))
    query_vector = models.NamedSparseVector(
        name="sparse-text",
        vector=models.SparseVector(
            indices=embeddings[0].indices,
            values=embeddings[0].values,
        ),
    )
    return query_vector

def upload_text_to_qdrant(client: QdrantClient, collection_name: str, text: str, point_id_sparse: int):
    try:
        docs = {"text": text}
        client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=point_id_sparse,
                    vector=get_sparse_embedding(docs["text"], sparse_encoder),
                    payload=docs,
                )
            ],
        )
        return True
    except Exception as e:
        return False
    


## CLASSES

class SemanticCache:
    def __init__(self, client: QdrantClient, text_encoder: SentenceTransformer, collection_name: str, threshold: float = 0.75):
        self.client = client
        self.text_encoder = text_encoder
        self.collection_name = collection_name
        self.threshold = threshold
    def upload_to_cache(self, question: str, answer: str):
        docs = {"question": question, "answer": answer}
        point_id = str(uuid.uuid4())
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=self.text_encoder.encode(docs["question"]).tolist(),
                    payload=docs,
                )
            ],
        )
    def search_cache(self, question: str, limit: int = 5):
        vector = self.text_encoder.encode(question).tolist()
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            query_filter=None,
            limit=limit,
        )
        payloads = [hit.payload["answer"] for hit in search_result if hit.score > self.threshold]
        if len(payloads) > 0:
            return payloads[0]
        else:
            return ""


class NeuralSearcher:
    def __init__(self, text_collection_name: str, client: QdrantClient, dense_encoder: SentenceTransformer , sparse_encoder: SparseTextEmbedding):
        self.text_collection_name = text_collection_name
        self.dense_encoder = dense_encoder
        self.qdrant_client = client
        self.sparse_encoder = sparse_encoder

    def search_text(self, text: str, limit: int = 5):
        search_result_sparse = self.qdrant_client.search(
            collection_name=self.text_collection_name,
            query_vector=get_query_sparse_embedding(text, self.sparse_encoder),
            query_filter=None,
            limit=limit,
        )
        payloads = [hit.payload["text"] for hit in search_result_sparse]
        context = reranking(payloads, text, self.dense_encoder)
        return context
    
    
    