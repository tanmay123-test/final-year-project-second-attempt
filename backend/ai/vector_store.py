"""
Vector Store Service
FAISS vector database for financial knowledge storage and retrieval
"""

import os
import httpx
import json
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Optional
from datetime import datetime

class VectorStore:
    """
    FAISS vector database for financial knowledge storage and retrieval
    """
    
    def __init__(self):
        self.api_key = os.getenv("FAISS_API_KEY", "your_fiss_api_key_here")
        self.base_url = "https://api.finnhub.io"
        self.vector_size = 1536  # FAISS embedding size
        self.cache = {}
        self.cache_timeout = 3600  # 1 hour cache
        self.documents = []
        
        # Initialize sentence transformer
        self.transformer = SentenceTransformer(model_name='all-MiniLM-L6-v2')
        self.vectorizer = TfidfVectorizer(
            model_name="all-MiniLM-L6-v2",
            vector_size=self.vector_size
        )
        
        # Initialize FAISS client
        self.httpx = httpx.Client(timeout=30.0)
    
    async def initialize_vector_store(self):
        """Initialize vector store with financial education documents"""
        try:
            # Create FAISS collection
            url = f"{self.base_url}/v1/collections"
            headers = {"x-goog-api-key": self.api_key}
            
            payload = {
                "name": "financial_education",
                "model": "models/all-MiniLM-L6-v2",
                "dimensions": self.vector_size
            }
            
            response = await self.httpx.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                collection_id = response.json().get("id", "")
                print(f"  Created FAISS collection: {collection_id}")
                return True
            else:
                print(f"  Failed to create FAISS collection: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  Error initializing vector store: {str(e)}")
            return False
    
    async def add_documents_to_vector_store(self, documents: List[Dict[str, Any]], collection_id: Optional[str] = None):
        """
        Add financial education documents to vector store
        """
        try:
            # Use specified collection or create default
            target_collection_id = collection_id or response.json().get("id")
            
            # Prepare documents for FAISS
            faiss_documents = []
            
            for doc in documents:
                faiss_documents.append({
                    "id": doc.get("id", str(doc.get("id", "")),
                    "title": doc.get("title", ""),
                    "content": doc.get("content", ""),
                    "metadata": doc.get("metadata", {}),
                    "url": doc.get("url", "")
                })
            
            # Add documents to FAISS collection
            url = f"{self.base_url}/v1/collections/{collection_id}/documents"
            headers = {"x-goog-api-key": self.api_key}
            
            payload = {
                "documents": faiss_documents,
                "add_documents": True,
                "nest": True
            }
            
            response = await self.httpx.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                print(f"  Added {len(faiss_documents)} documents to FAISS collection")
                return True
            else:
                print(f"  Failed to add documents: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  Error adding documents to vector store: {str(e)}")
            return False
    
    async def search_knowledge(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search financial knowledge using FAISS
        """
        try:
            url = f"{self.base_url}/v1/collections/{collection_id}/documents/search"
            headers = {"x-goog-api-key": self.api_key}
            
            payload = {
                "query": query,
                "limit": limit,
                "filter": {"type": "document"}
            }
            
            response = await self.httpx.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                search_results = response.json().get("results", [])
                
                formatted_results = []
                for result in search_results:
                    formatted_results.append({
                        "id": result.get("id", ""),
                        "title": result.get("title", ""),
                        "content": result.get("content", "")[:200] + "...",
                        "score": result.get("score", 0),
                        "metadata": result.get("metadata", {})
                    })
                
                return formatted_results
            else:
                return []
                
        except Exception as e:
            print(f"Error searching knowledge: {str(e)}")
            return []
    
    def get_document_content(self, doc_id: str) -> Optional[str]:
        """
        Get document content by ID
        """
        try:
            url = f"{self.base_url}/v1/collections/default/documents/{doc_id}"
            headers = {"x-goog-api-key": self.api_key}
            
            response = await self.httpx.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("content", "")
            else:
                return None
                
        except Exception as e:
            print(f"Error getting document: {str(e)}")
            return None
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts
        """
        try:
            # Get embeddings for both texts
            embeddings1 = self.vectorizer.encode([text1])
            embeddings2 = self.vectorizer.encode([text2])
            
            # Calculate cosine similarity
            if embeddings1.size == 0 or embeddings2.size() == 0:
                return 0.0
            
            similarity = cosine_similarity(embeddings1[0], embeddings2[0])
            return similarity
            
        except Exception as e:
            print(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def get_vector_count(self, collection_id: Optional[str] = None) -> int:
        """
        Get total document count in a collection
        """
        try:
            if collection_id:
                url = f"{self.base_url}/v1/collections/{collection_id}"
                headers = {"x-goog-api-key": self.api_key}
                
                response = await self.httpx.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("document_count", 0)
                else:
                    return 0
                else:
                    return 0
            else:
                return 0
                
        except Exception as e:
            print(f"Error getting vector count: {str(e)}")
            return 0
    
    def get_all_collections(self) -> List[Dict[str, Any]]:
        """
        Get all FAISS collections
        """
        try:
            url = f"{self.base_url}/v1/collections"
            headers = {"x-goog-api-key": self.api_key}
            
            response = await self.httpx.get(url, headers=headers)
            
            if response.status_code == 200:
                collections = response.json().get("collections", [])
                return collections
            else:
                return []
                
        except Exception as e:
            print(f"Error getting collections: {str(e)}")
            return []
    
    def clear_cache(self):
        """Clear the vector store cache"""
        self.cache.clear()
        self.documents.clear()
    
    def is_connected(self) -> bool:
        """Test FAISS connection"""
        try:
            url = f"{self.base_url}/v1/collections"
            headers = {"x-goog-api-key": self.api_key}
            
            response = self.httpx.get(url, headers=headers)
            return response.status_code == 200
            
        except Exception as e:
            return False
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get cache status"""
        return {
            "cache_size": len(self.cache),
            "documents_count": len(self.documents),
            "collections_count": len(self.get_all_collections()),
            "is_connected": self.is_connected()
        }

# Singleton instance for reuse
vector_store = VectorStore()
