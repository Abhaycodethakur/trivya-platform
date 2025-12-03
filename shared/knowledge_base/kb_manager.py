"""
Knowledge Base Manager for Trivya Platform

This module provides high-level orchestration for document ingestion,
updates, and retrieval across the knowledge base system.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.core_functions.config import Config
from shared.core_functions.logger import get_logger
from shared.knowledge_base.vector_store import VectorStore
from shared.knowledge_base.rag_pipeline import RAGPipeline


class KnowledgeBaseError(Exception):
    """Custom exception for Knowledge Base errors"""
    pass


class KnowledgeBaseManager:
    """
    Knowledge Base Manager for orchestrating document operations.
    
    This class provides high-level management of the knowledge base,
    including document ingestion, updates, search, and statistics.
    """
    
    def __init__(
        self,
        config: Config,
        vector_store: VectorStore,
        rag_pipeline: RAGPipeline,
        logger: Optional[Any] = None
    ):
        """
        Initialize the Knowledge Base Manager.
        
        Args:
            config: Config object
            vector_store: VectorStore instance
            rag_pipeline: RAGPipeline instance
            logger: Optional Logger instance
            
        Raises:
            KnowledgeBaseError: If initialization fails
        """
        self.config = config
        self.vector_store = vector_store
        self.rag_pipeline = rag_pipeline
        self.logger = logger or get_logger(config).get_logger("KnowledgeBaseManager")
        
        # Track statistics
        self.stats = {
            "total_documents": 0,
            "last_update": None,
            "total_queries": 0,
            "successful_ingestions": 0,
            "failed_ingestions": 0
        }
        
        self.logger.info("Knowledge Base Manager initialized")
    
    def validate_document(self, document: Dict[str, Any]) -> bool:
        """
        Validate a document before ingestion.
        
        Args:
            document: Document dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        if 'content' not in document:
            self.logger.warning("Document missing 'content' field")
            return False
        
        if not isinstance(document['content'], str):
            self.logger.warning("Document 'content' must be a string")
            return False
        
        if not document['content'].strip():
            self.logger.warning("Document 'content' cannot be empty")
            return False
        
        # Check metadata
        if 'metadata' in document and not isinstance(document['metadata'], dict):
            self.logger.warning("Document 'metadata' must be a dictionary")
            return False
        
        return True
    
    def ingest_documents(
        self,
        documents: List[Dict[str, Any]],
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Ingest multiple documents into the knowledge base.
        
        Args:
            documents: List of document dictionaries
            validate: Whether to validate documents before ingestion
            
        Returns:
            Ingestion summary with success/failure counts
            
        Raises:
            KnowledgeBaseError: If ingestion fails completely
        """
        try:
            if not documents:
                self.logger.warning("No documents provided for ingestion")
                return {
                    "success": True,
                    "total": 0,
                    "successful": 0,
                    "failed": 0,
                    "document_ids": []
                }
            
            # Validate documents if requested
            valid_documents = []
            invalid_count = 0
            
            if validate:
                for doc in documents:
                    if self.validate_document(doc):
                        valid_documents.append(doc)
                    else:
                        invalid_count += 1
            else:
                valid_documents = documents
            
            # Ingest valid documents
            document_ids = []
            if valid_documents:
                try:
                    document_ids = self.vector_store.add_documents(valid_documents)
                    self.stats["successful_ingestions"] += len(document_ids)
                    self.stats["total_documents"] += len(document_ids)
                except Exception as e:
                    self.logger.error(f"Failed to add documents to vector store: {str(e)}")
                    self.stats["failed_ingestions"] += len(valid_documents)
                    raise
            
            # Update statistics
            self.stats["last_update"] = datetime.now().isoformat()
            self.stats["failed_ingestions"] += invalid_count
            
            summary = {
                "success": True,
                "total": len(documents),
                "successful": len(document_ids),
                "failed": invalid_count,
                "document_ids": document_ids,
                "timestamp": self.stats["last_update"]
            }
            
            self.logger.info(
                f"Document ingestion completed",
                extra={
                    "total": len(documents),
                    "successful": len(document_ids),
                    "failed": invalid_count
                }
            )
            
            return summary
            
        except Exception as e:
            error_msg = f"Document ingestion failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise KnowledgeBaseError(error_msg) from e

    def add_document(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a document to the knowledge base from a file path."""
        path = Path(file_path)
        if not path.exists():
            raise KnowledgeBaseError(f"Document not found: {file_path}")

        document = {
            "content": path.read_text(encoding="utf-8"),
            "metadata": metadata or {"source": path.name}
        }

        result = self.ingest_documents([document])
        return result["document_ids"][0] if result["document_ids"] else ""
    
    def update_document(
        self,
        doc_id: str,
        new_content: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Update an existing document in the knowledge base.
        
        Note: Current implementation adds a new version rather than
        updating in place, as vector stores typically don't support updates.
        
        Args:
            doc_id: Document ID to update
            new_content: New content for the document
            metadata: Optional new metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare updated document
            updated_doc = {
                "content": new_content,
                "metadata": metadata or {}
            }
            
            # Add version information to metadata
            updated_doc["metadata"]["previous_id"] = doc_id
            updated_doc["metadata"]["updated_at"] = datetime.now().isoformat()
            
            # Validate and ingest
            if not self.validate_document(updated_doc):
                return False
            
            result = self.ingest_documents([updated_doc], validate=False)
            
            self.logger.info(
                f"Document updated",
                extra={
                    "original_id": doc_id,
                    "new_id": result["document_ids"][0] if result["document_ids"] else None
                }
            )
            
            return result["successful"] > 0
            
        except Exception as e:
            self.logger.error(f"Failed to update document: {str(e)}")
            return False
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        system_instruction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search the knowledge base and get RAG-formatted results.
        
        Args:
            query: Search query
            top_k: Number of results to return
            system_instruction: Optional system instruction for prompt
            
        Returns:
            RAG query results with prompt and context
            
        Raises:
            KnowledgeBaseError: If search fails
        """
        try:
            # Update query statistics
            self.stats["total_queries"] += 1
            
            # Perform RAG query
            result = self.rag_pipeline.query(
                user_query=query,
                top_k=top_k,
                system_instruction=system_instruction
            )
            
            self.logger.info(
                f"Knowledge base search completed",
                extra={
                    "query_length": len(query),
                    "results_count": result["context_count"]
                }
            )
            
            return result
            
        except Exception as e:
            error_msg = f"Knowledge base search failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise KnowledgeBaseError(error_msg) from e

    def query(
        self,
        query: str,
        top_k: int = 5,
        system_instruction: Optional[str] = None
    ) -> str:
        """High-level helper that returns a textual response for the query."""
        result = self.search(query, top_k=top_k, system_instruction=system_instruction)
        context_docs = result.get("context", [])

        if not context_docs:
            return "No relevant information found in the knowledge base."

        snippets = []
        for idx, doc in enumerate(context_docs, 1):
            content = doc.get("content", "").strip()
            if not content:
                continue
            source = doc.get("metadata", {}).get("source", f"Document {idx}")
            snippets.append(f"[{source}] {content}")

        combined = "\n".join(snippets)
        return f"Based on the knowledge base, here's what we found:\n{combined}"
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base.
        
        Returns:
            Dictionary with knowledge base statistics
        """
        try:
            # Get vector store info
            vector_store_info = self.vector_store.get_collection_info()
            
            # Combine with internal stats
            stats = {
                **self.stats,
                "vector_store": vector_store_info,
                "rag_pipeline": self.rag_pipeline.get_pipeline_stats()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get stats: {str(e)}")
            return {
                "error": str(e),
                **self.stats
            }

    def list_documents(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """List documents currently stored in the vector store."""
        try:
            return self.vector_store.list_documents(limit=limit)
        except Exception as e:
            self.logger.error(f"Failed to list documents: {str(e)}")
            return []
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the knowledge base system.
        
        Returns:
            Health check results
        """
        health = {
            "status": "healthy",
            "checks": {
                "vector_store": False,
                "rag_pipeline": False,
                "document_count": 0
            }
        }
        
        try:
            # Check vector store
            info = self.vector_store.get_collection_info()
            health["checks"]["vector_store"] = True
            health["checks"]["document_count"] = info.get("document_count", 0)
            
            # Check RAG pipeline
            pipeline_stats = self.rag_pipeline.get_pipeline_stats()
            health["checks"]["rag_pipeline"] = "error" not in pipeline_stats
            
            # Overall status
            if all([
                health["checks"]["vector_store"],
                health["checks"]["rag_pipeline"]
            ]):
                health["status"] = "healthy"
            else:
                health["status"] = "degraded"
                
        except Exception as e:
            health["status"] = "unhealthy"
            health["error"] = str(e)
            self.logger.error(f"Health check failed: {str(e)}")
        
        return health
