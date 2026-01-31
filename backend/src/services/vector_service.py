"""
vector_service.py
-----------------
Manages interactions with the Qdrant Vector Database.
Responsible for initializing collections, embedding text (using OpenAI),
and performing similarity search to retrieve relevant technical manuals.
"""

import uuid
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from src.core.config import get_settings
from src.core.schema import ManualChunk

settings = get_settings()

class VectorService:
    def __init__(self):
        """
        Initialize Qdrant client and OpenAI Embeddings.
        We connect to the 'qdrant' host defined in docker-compose.
        """
        self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        self.collection_name = "kone_manuals"
        
        # Initialize Embeddings
        # Uses OPENAI_API_KEY from settings automatically
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    def ensure_collection_exists(self):
        """
        Checks if the vector collection exists; if not, creates it.
        The vector size for 'text-embedding-3-small' is 1536.
        """
        collections = self.client.get_collections()
        exists = any(c.name == self.collection_name for c in collections.collections)

        if not exists:
            print(f"Creating collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=1536,  # Dimension for text-embedding-3-small
                    distance=models.Distance.COSINE
                )
            )
        else:
            print(f"Collection {self.collection_name} already exists.")

    def upsert_manuals(self, manuals: List[ManualChunk]):
        """
        Ingests parsed manual chunks into Qdrant.
        1. Converts text to vectors.
        2. Uploads to Qdrant with metadata (page number, source).
        """
        self.ensure_collection_exists()
        
        points = []
        for chunk in manuals:
            # Generate embedding
            vector = self.embeddings.embed_query(chunk.content)
            
            # Create payload for retrieval later
            payload = {
                "content": chunk.content,
                "source_doc": chunk.source_doc,
                "page_number": chunk.page_number,
                "related_error_codes": chunk.related_error_codes
            }
            
            # Create Qdrant Point
            points.append(models.PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=payload
            ))

        # Batch upload
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print(f"Successfully upserted {len(points)} manual chunks.")

    def search_similar(self, query: str, limit: int = 3) -> List[ManualChunk]:
        """
        Performs a semantic search for the query (e.g., an error code or description).
        Returns a list of ManualChunk objects.
        """
        # 1. Embed the query
        query_vector = self.embeddings.embed_query(query)

        # 2. Search Qdrant
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )

        # 3. Map back to Pydantic models
        results = []
        for hit in search_result:
            results.append(ManualChunk(
                chunk_id=str(hit.id),
                content=hit.payload["content"],
                source_doc=hit.payload["source_doc"],
                page_number=hit.payload["page_number"],
                related_error_codes=hit.payload.get("related_error_codes", [])
            ))
            
        return results

# Singleton instance for import
vector_service = VectorService()