"""
Vector embedding management system for AI Rails TDD workflow.
This module provides semantic search capabilities using Upstash Vector.
"""
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Try to import upstash-vector, provide fallback if not available
try:
    from upstash_vector import Index
    VECTOR_AVAILABLE = True
except ImportError:
    logger.warning("upstash-vector not installed. Vector search will be disabled.")
    VECTOR_AVAILABLE = False
    Index = None


class VectorManager:
    """
    Manages vector embeddings for semantic search using Upstash Vector.
    
    This class provides methods to store, search, and manage vector embeddings
    for various agent outputs, enabling semantic search across the workflow.
    """
    
    def __init__(self, url: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize the Vector manager with Upstash credentials.
        
        Args:
            url: Upstash Vector URL (defaults to env var UPSTASH_VECTOR_URL)
            token: Upstash Vector token (defaults to env var UPSTASH_VECTOR_TOKEN)
        """
        self.url = url or os.getenv("UPSTASH_VECTOR_URL")
        self.token = token or os.getenv("UPSTASH_VECTOR_TOKEN")
        self.index = None
        self._memory_store: Dict[str, Tuple[List[float], Dict[str, Any]]] = {}
        
        if not VECTOR_AVAILABLE:
            logger.warning("Vector search running in memory-only mode (upstash-vector not installed)")
        elif not self.url or not self.token:
            logger.warning("Upstash Vector credentials not found. Vector search running in memory-only mode.")
        else:
            try:
                self.index = Index(url=self.url, token=self.token)
                logger.info("Connected to Upstash Vector")
            except Exception as e:
                logger.error(f"Failed to connect to Upstash Vector: {e}")
                logger.info("Falling back to memory-only mode")
    
    async def upsert(self, id: str, vector: List[float], metadata: Dict[str, Any] = None) -> bool:
        """
        Insert or update a vector with metadata.
        
        Args:
            id: Unique identifier for the vector
            vector: The embedding vector
            metadata: Optional metadata to store with the vector
            
        Returns:
            bool: True if successful, False otherwise
        """
        metadata = metadata or {}
        
        # Add timestamp if not present
        if "timestamp" not in metadata:
            metadata["timestamp"] = datetime.now().isoformat()
        
        if self.index:
            try:
                await self.index.upsert(
                    vectors=[{
                        "id": id,
                        "vector": vector,
                        "metadata": metadata
                    }]
                )
                return True
            except Exception as e:
                logger.error(f"Failed to upsert vector to Upstash: {e}")
                # Fall through to memory storage
        
        # Memory fallback
        self._memory_store[id] = (vector, metadata)
        return True
    
    async def query(
        self, 
        vector: List[float], 
        top_k: int = 5, 
        filter: Optional[str] = None,
        include_vectors: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Query similar vectors.
        
        Args:
            vector: Query embedding vector
            top_k: Number of results to return
            filter: Optional filter expression (e.g., "type = 'plan'")
            include_vectors: Whether to include vectors in results
            
        Returns:
            List of results with id, score, metadata, and optionally vector
        """
        if self.index:
            try:
                results = await self.index.query(
                    vector=vector,
                    top_k=top_k,
                    include_metadata=True,
                    include_vectors=include_vectors,
                    filter=filter
                )
                return results
            except Exception as e:
                logger.error(f"Failed to query vectors from Upstash: {e}")
                # Fall through to memory search
        
        # Memory fallback - simple cosine similarity
        scores = []
        for id, (stored_vector, metadata) in self._memory_store.items():
            # Apply filter if provided (basic implementation)
            if filter and not self._matches_filter(metadata, filter):
                continue
                
            score = self._cosine_similarity(vector, stored_vector)
            scores.append({
                "id": id,
                "score": score,
                "metadata": metadata,
                "vector": stored_vector if include_vectors else None
            })
        
        # Sort by score and return top_k
        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores[:top_k]
    
    async def delete(self, ids: List[str]) -> bool:
        """
        Delete vectors by IDs.
        
        Args:
            ids: List of vector IDs to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        success = True
        
        if self.index:
            try:
                await self.index.delete(ids)
            except Exception as e:
                logger.error(f"Failed to delete vectors from Upstash: {e}")
                success = False
        
        # Also delete from memory store
        for id in ids:
            self._memory_store.pop(id, None)
        
        return success
    
    async def fetch(self, ids: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch vectors by IDs.
        
        Args:
            ids: List of vector IDs to fetch
            
        Returns:
            List of vectors with metadata
        """
        if self.index:
            try:
                results = await self.index.fetch(ids)
                return results
            except Exception as e:
                logger.error(f"Failed to fetch vectors from Upstash: {e}")
                # Fall through to memory fetch
        
        # Memory fallback
        results = []
        for id in ids:
            if id in self._memory_store:
                vector, metadata = self._memory_store[id]
                results.append({
                    "id": id,
                    "vector": vector,
                    "metadata": metadata
                })
        return results
    
    async def update_metadata(self, id: str, metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for a vector.
        
        Args:
            id: Vector ID
            metadata: New metadata (will be merged with existing)
            
        Returns:
            bool: True if successful
        """
        # Fetch existing vector
        existing = await self.fetch([id])
        if not existing:
            return False
        
        # Merge metadata
        current = existing[0]
        updated_metadata = {**current.get("metadata", {}), **metadata}
        
        # Re-upsert with updated metadata
        return await self.upsert(
            id=id,
            vector=current["vector"],
            metadata=updated_metadata
        )
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import math
        
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _matches_filter(self, metadata: Dict[str, Any], filter: str) -> bool:
        """
        Simple filter matching for memory fallback.
        Only supports basic equality checks like "type = 'plan'"
        """
        # Very basic implementation - just handles "key = 'value'"
        parts = filter.split("=")
        if len(parts) != 2:
            return True
        
        key = parts[0].strip()
        value = parts[1].strip().strip("'\"")
        
        return metadata.get(key) == value


class EmbeddingManager:
    """
    Manages the creation of embeddings using OpenAI API.
    """
    
    def __init__(self, model: str = "text-embedding-3-small"):
        """
        Initialize the embedding manager.
        
        Args:
            model: The embedding model to use (default: text-embedding-3-small)
                  Options: text-embedding-3-small, text-embedding-3-large, text-embedding-ada-002
        """
        self.model = model
        self.dimension = 1536  # All current OpenAI models use 1536 dimensions
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client if API key is available."""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and not api_key.startswith("sk-..."):  # Check it's not placeholder
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=api_key)
                logger.info(f"Initialized OpenAI client with model: {self.model}")
            except ImportError:
                logger.warning("OpenAI package not installed. Run: pip install openai")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        else:
            logger.warning("OpenAI API key not found or invalid. Using placeholder embeddings.")
    
    async def create_embedding(self, text: str) -> List[float]:
        """
        Create an embedding for the given text using OpenAI API.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector (1536 dimensions)
        """
        if self._client:
            try:
                response = await self._client.embeddings.create(
                    input=text,
                    model=self.model
                )
                return response.data[0].embedding
            except Exception as e:
                logger.error(f"OpenAI embedding error: {e}")
                # Fall through to placeholder
        
        # Placeholder fallback
        import random
        logger.debug("Using placeholder embeddings")
        return [random.random() for _ in range(self.dimension)]
    
    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts efficiently."""
        if self._client and len(texts) > 0:
            try:
                # OpenAI supports batch embedding
                response = await self._client.embeddings.create(
                    input=texts,
                    model=self.model
                )
                return [item.embedding for item in response.data]
            except Exception as e:
                logger.error(f"OpenAI batch embedding error: {e}")
        
        # Fallback to individual embeddings
        return [await self.create_embedding(text) for text in texts]