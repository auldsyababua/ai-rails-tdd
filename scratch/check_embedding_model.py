#!/usr/bin/env python3
"""
Check if Upstash Vector index has native embedding model configured.
"""
import os
from dotenv import load_dotenv
from upstash_vector import Index

load_dotenv()

def check_embedding_model():
    """Check Vector index configuration."""
    url = os.getenv("UPSTASH_VECTOR_URL")
    token = os.getenv("UPSTASH_VECTOR_TOKEN")
    
    if not url or not token:
        print("❌ Vector credentials not found")
        return
    
    try:
        # Create index connection
        index = Index(url=url, token=token)
        
        # Try to use native embedding (this will only work if configured)
        print("Testing native embedding support...")
        
        # Try upserting with raw text (only works with native embedding)
        try:
            result = index.upsert(
                vectors=[{
                    "id": "embedding-test",
                    "data": "This is a test of native embeddings",
                    "metadata": {"test": True}
                }]
            )
            print("✅ Native embedding model is configured!")
            print("   You can upsert raw text directly without creating embeddings.")
            
            # Query with text
            results = index.query(
                data="test query",
                top_k=1,
                include_metadata=True
            )
            print("✅ Text-based query also works!")
            
            # Cleanup
            index.delete(["embedding-test"])
            
        except Exception as e:
            print("❌ No native embedding model configured")
            print("   Your index requires pre-computed vectors (1536 dimensions)")
            print(f"   Error: {str(e)}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")


if __name__ == "__main__":
    check_embedding_model()