from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

class NeuralSearcher:
    """
    A class for performing neural search operations on embedded documents using Qdrant.

    This class enables semantic search over documents by converting text queries into
    vectors and finding similar vectors in a Qdrant collection.

    Args:
        collection_name (str): Name of the Qdrant collection to search in
        client (QdrantClient): Initialized Qdrant client for database operations
        model (SentenceTransformer): Model for encoding text into vectors
    """

    def __init__(self, collection_name: str, client: QdrantClient, model: SentenceTransformer):
        self.collection_name = collection_name
        # Initialize encoder model
        self.model = model
        # initialize Qdrant client
        self.qdrant_client = client

    def search(self, text: str, limit: int = 1):
        """
        Perform a neural search for the given text query.

        Args:
            text (str): Search query text
            limit (int, optional): Maximum number of results to return. Defaults to 1

        Returns:
            list: List of payload objects from the most similar documents found in the collection,
                 where each payload contains the document text and metadata
        """
        # Convert text query into vector
        vector = self.model.encode(text).tolist()

        # Use `vector` for search for closest vectors in the collection
        search_result = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            query_filter=None,  # If you don't want any filters for now
            limit=limit,
        )
        payloads = [hit.payload for hit in search_result]
        return payloads
