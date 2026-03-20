"""
Simple Vector Store Service
Mock implementation for financial knowledge storage and retrieval
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import sqlite3

class VectorStore:
    """
    Simple mock vector database for financial knowledge storage and retrieval
    """
    
    def __init__(self):
        self.documents = []
        self.cache = {}
        self.cache_timeout = 3600  # 1 hour cache
        self.db_path = 'expertease.db'
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize the database for vector storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create documents table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
    
    async def initialize_vector_store(self):
        """Initialize vector store with financial education documents"""
        try:
            print("✅ Mock vector store initialized successfully")
            return True
                
        except Exception as e:
            print(f"❌ Error initializing vector store: {str(e)}")
            return False
    
    async def add_documents_to_vector_store(self, documents: List[Dict[str, Any]], collection_id: Optional[str] = None):
        """
        Add financial education documents to vector store
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for doc in documents:
                doc_id = doc.get("id", str(len(self.documents)))
                title = doc.get("title", "")
                content = doc.get("content", "")
                metadata = json.dumps(doc.get("metadata", {}))
                category = doc.get("category", "general")
                
                cursor.execute("""
                INSERT OR REPLACE INTO knowledge_documents (id, title, content, metadata, category, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (doc_id, title, content, metadata, category, datetime.utcnow()))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Added {len(documents)} documents to vector store")
            return True
                
        except Exception as e:
            print(f"❌ Error adding documents to vector store: {str(e)}")
            return False
    
    async def search_knowledge(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search financial knowledge using simple keyword matching
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Simple keyword search
            keywords = query.lower().split()
            search_results = []
            
            for keyword in keywords:
                cursor.execute("""
                SELECT id, title, content, metadata, category 
                FROM knowledge_documents 
                WHERE LOWER(title) LIKE ? OR LOWER(content) LIKE ?
                LIMIT ?
                """, (f"%{keyword}%", f"%{keyword}%", limit))
                
                rows = cursor.fetchall()
                
                for row in rows:
                    doc_id, title, content, metadata, category = row
                    
                    # Calculate simple relevance score
                    score = self._calculate_relevance_score(query, title, content)
                    
                    if doc_id not in [r["id"] for r in search_results]:
                        search_results.append({
                            "id": doc_id,
                            "title": title,
                            "content": content[:200] + "...",
                            "score": score,
                            "metadata": json.loads(metadata) if metadata else {},
                            "category": category
                        })
            
            conn.close()
            
            # Sort by score and limit results
            search_results.sort(key=lambda x: x["score"], reverse=True)
            return search_results[:limit]
                
        except Exception as e:
            print(f"Error searching knowledge: {str(e)}")
            return []
    
    def _calculate_relevance_score(self, query: str, title: str, content: str) -> float:
        """
        Calculate simple relevance score based on keyword matching
        """
        query_lower = query.lower()
        title_lower = title.lower()
        content_lower = content.lower()
        
        score = 0.0
        
        # Check for exact phrase matches
        if query_lower in title_lower:
            score += 2.0
        if query_lower in content_lower:
            score += 1.0
        
        # Check for individual keyword matches
        keywords = query_lower.split()
        for keyword in keywords:
            if keyword in title_lower:
                score += 0.5
            if keyword in content_lower:
                score += 0.3
        
        return score
    
    def get_document_content(self, doc_id: str) -> Optional[str]:
        """
        Get document content by ID
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT content FROM knowledge_documents WHERE id = ?
            """, (doc_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return row[0]
            else:
                return None
                
        except Exception as e:
            print(f"Error getting document: {str(e)}")
            return None
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple similarity between two texts
        """
        try:
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union) if union else 0.0
            
        except Exception as e:
            print(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def get_vector_count(self, collection_id: Optional[str] = None) -> int:
        """
        Get total document count
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM knowledge_documents")
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
                
        except Exception as e:
            print(f"Error getting vector count: {str(e)}")
            return 0
    
    def get_all_collections(self) -> List[Dict[str, Any]]:
        """
        Get all categories as collections
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT DISTINCT category, COUNT(*) as count FROM knowledge_documents GROUP BY category")
            rows = cursor.fetchall()
            
            collections = []
            for row in rows:
                category, count = row
                collections.append({
                    "name": category,
                    "document_count": count
                })
            
            conn.close()
            return collections
                
        except Exception as e:
            print(f"Error getting collections: {str(e)}")
            return []
    
    def clear_cache(self):
        """Clear the vector store cache"""
        self.cache.clear()
        self.documents.clear()
    
    def is_connected(self) -> bool:
        """Test connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            return True
        except:
            return False
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get cache status"""
        return {
            "cache_size": len(self.cache),
            "documents_count": self.get_vector_count(),
            "collections_count": len(self.get_all_collections()),
            "is_connected": self.is_connected()
        }

# Singleton instance for reuse
vector_store = VectorStore()
