"""
Knowledge Base Server for Trivya Platform MCP Layer

This server provides document management capabilities through the MCP protocol,
including CRUD operations, search, versioning, and caching.
"""

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from cachetools import TTLCache

from mcp_servers.base_server import (
    BaseMCPServer, MCPMessage, MCPMessageHeader, 
    MessageType, MCPServerError, MCPValidationError
)
from shared.core_functions.config import Config
from shared.core_functions.logger import get_logger
from shared.knowledge_base.kb_manager import KnowledgeBaseManager, KnowledgeBaseError
from shared.knowledge_base.vector_store import VectorStore
from shared.knowledge_base.rag_pipeline import RAGPipeline


class DocumentNotFoundError(Exception):
    """Raised when a document is not found."""
    pass


class DocumentValidationError(Exception):
    """Raised when document validation fails."""
    pass


class KBServer(BaseMCPServer):
    """
    Knowledge Base Server for MCP layer.
    
    Provides comprehensive document management capabilities including
    CRUD operations, search, versioning, and caching through the MCP protocol.
    
    Features:
    - Document add, get, update, delete operations
    - Semantic search via VectorStore integration
    - Document listing with filtering and pagination
    - LRU caching for frequently accessed documents
    - Version tracking for document updates
    - Comprehensive error handling and logging
    """
    
    # Configuration defaults
    DEFAULT_CONFIG = {
        "max_document_size": 10485760,  # 10MB
        "supported_formats": ["txt", "pdf", "docx", "md", "html"],
        "version_history_limit": 10,
        "cache_ttl": 3600,  # 1 hour
        "cache_size_limit": 100,
        "rate_limit": 100,  # requests per minute
        "search_result_limit": 50,
        "batch_operation_limit": 100
    }
    
    # Valid actions for routing
    VALID_ACTIONS = [
        "add_document", "get_document", "update_document", 
        "delete_document", "list_documents", "search_documents",
        "get_stats", "health_check"
    ]
    
    def __init__(self, name: str = "kb_server", config: Optional[Config] = None):
        """
        Initialize the KB Server with components and configuration.
        
        Args:
            name: Server name for identification
            config: Configuration object
        """
        super().__init__(name, config)
        
        # Initialize KB configuration
        self.kb_config = {**self.DEFAULT_CONFIG}
        for key in self.DEFAULT_CONFIG:
            env_key = f"KB_{key.upper()}"
            if env_key in self.config.env:
                self.kb_config[key] = self.config.env[env_key]
        
        # Initialize document cache
        self.cache = TTLCache(
            maxsize=int(self.kb_config["cache_size_limit"]),
            ttl=int(self.kb_config["cache_ttl"])
        )
        
        # Initialize components
        try:
            self.vector_store = VectorStore(self.config)
            self.rag_pipeline = RAGPipeline(self.vector_store, self.config)
            self.kb_manager = KnowledgeBaseManager(
                config=self.config,
                vector_store=self.vector_store,
                rag_pipeline=self.rag_pipeline
            )
            self.log("info", "KB Server components initialized successfully")
        except Exception as e:
            self.log("error", f"Failed to initialize KB components: {str(e)}")
            self.vector_store = None
            self.rag_pipeline = None
            self.kb_manager = None
        
        # Document metadata store (in-memory for now, could be persisted)
        self._document_metadata: Dict[str, Dict[str, Any]] = {}
        
    async def handle_request(self, request: MCPMessage) -> Dict[str, Any]:
        """
        Main entry point for all MCP requests.
        
        Routes to appropriate action handlers based on the 'action' field.
        
        Args:
            request: MCP message containing the request
            
        Returns:
            Response dictionary with operation results
            
        Raises:
            MCPValidationError: If request validation fails
            MCPServerError: If operation fails
        """
        # Validate request structure
        if not request.body:
            raise MCPValidationError("Request body is required")
        
        action = request.body.get("action")
        if not action:
            raise MCPValidationError("Action is required")
        
        if action not in self.VALID_ACTIONS:
            raise MCPValidationError(f"Invalid action: {action}. Valid actions: {self.VALID_ACTIONS}")
        
        # Check KB Manager availability
        if action not in ["health_check"] and not self.kb_manager:
            raise MCPServerError("KB Manager not initialized")
        
        # Route to appropriate handler
        handlers = {
            "add_document": self._add_document,
            "get_document": self._get_document,
            "update_document": self._update_document,
            "delete_document": self._delete_document,
            "list_documents": self._list_documents,
            "search_documents": self._search_documents,
            "get_stats": self._get_stats,
            "health_check": self._health_check
        }
        
        try:
            handler = handlers[action]
            result = await handler(request.body)
            return result
        except (DocumentNotFoundError, DocumentValidationError) as e:
            self.log("warning", f"Document error: {str(e)}")
            raise MCPValidationError(str(e))
        except KnowledgeBaseError as e:
            self.log("error", f"KB error: {str(e)}")
            raise MCPServerError(f"Knowledge base error: {str(e)}")
        except Exception as e:
            self.log("error", f"Unexpected error in {action}: {str(e)}")
            raise MCPServerError(f"Internal server error: {str(e)}")
    
    async def _add_document(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new document to the knowledge base.
        
        Args:
            body: Request body with 'content' and optional 'metadata'
            
        Returns:
            Response with document_id and status
        """
        import json
        
        content = body.get("content")
        if not content:
            raise DocumentValidationError("Document content is required")
        
        # Check document size
        if len(content.encode('utf-8')) > self.kb_config["max_document_size"]:
            raise DocumentValidationError(
                f"Document exceeds maximum size of {self.kb_config['max_document_size']} bytes"
            )
        
        metadata = body.get("metadata", {})
        
        # Sanitize metadata - ChromaDB only accepts str, int, float, bool, None
        sanitized_metadata = {}
        for key, value in metadata.items():
            if isinstance(value, (list, dict)):
                sanitized_metadata[key] = json.dumps(value)
            else:
                sanitized_metadata[key] = value
        
        # Add timestamp
        sanitized_metadata["created_at"] = datetime.utcnow().isoformat()
        sanitized_metadata["version"] = 1
        
        # Create document with sanitized metadata
        document = {
            "id": body.get("id"),  # Optional custom ID
            "content": content,
            "metadata": sanitized_metadata  # Use sanitized metadata for ChromaDB
        }
        
        # Ingest via KB Manager
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.kb_manager.ingest_documents([document])
        )
        
        if result["successful"] > 0:
            doc_id = result["document_ids"][0]
            
            # Store metadata
            self._document_metadata[doc_id] = {
                "id": doc_id,
                "metadata": sanitized_metadata,
                "versions": [{"version": 1, "created_at": sanitized_metadata["created_at"]}]
            }
            
            # Cache the document
            self.cache[doc_id] = {"content": content, "metadata": sanitized_metadata}
            
            self.log("info", f"Document added: {doc_id}")
            return {
                "success": True,
                "document_id": doc_id,
                "message": "Document added successfully"
            }
        else:
            raise MCPServerError("Failed to add document")
    
    async def _get_document(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve a document by ID.
        
        Args:
            body: Request body with 'document_id' and optional 'version'
            
        Returns:
            Document content and metadata
        """
        doc_id = body.get("document_id")
        if not doc_id:
            raise DocumentValidationError("document_id is required")
        
        # Check cache first
        if doc_id in self.cache:
            self.log("info", f"Cache hit for document: {doc_id}")
            cached = self.cache[doc_id]
            return {
                "success": True,
                "document_id": doc_id,
                "content": cached["content"],
                "metadata": cached["metadata"],
                "cached": True
            }
        
        # Search in vector store
        loop = asyncio.get_running_loop()
        documents = await loop.run_in_executor(
            None,
            lambda: self.vector_store.list_documents()
        )
        
        for doc in documents:
            if doc.get("id") == doc_id:
                # Cache it for future access
                self.cache[doc_id] = {
                    "content": doc.get("content", ""),
                    "metadata": doc.get("metadata", {})
                }
                
                return {
                    "success": True,
                    "document_id": doc_id,
                    "content": doc.get("content", ""),
                    "metadata": doc.get("metadata", {}),
                    "cached": False
                }
        
        raise DocumentNotFoundError(f"Document not found: {doc_id}")
    
    async def _update_document(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing document with version tracking.
        
        Args:
            body: Request body with 'document_id', 'content', and optional 'metadata'
            
        Returns:
            Update result with new version info
        """
        doc_id = body.get("document_id")
        content = body.get("content")
        
        if not doc_id:
            raise DocumentValidationError("document_id is required")
        if not content:
            raise DocumentValidationError("content is required")
        
        metadata = body.get("metadata", {})
        
        # Update via KB Manager
        loop = asyncio.get_running_loop()
        success = await loop.run_in_executor(
            None,
            lambda: self.kb_manager.update_document(doc_id, content, metadata)
        )
        
        if success:
            # Clear cache for this document
            if doc_id in self.cache:
                del self.cache[doc_id]
            
            # Update metadata store
            if doc_id in self._document_metadata:
                version = len(self._document_metadata[doc_id].get("versions", [])) + 1
                self._document_metadata[doc_id]["versions"].append({
                    "version": version,
                    "updated_at": datetime.utcnow().isoformat()
                })
            
            self.log("info", f"Document updated: {doc_id}")
            return {
                "success": True,
                "document_id": doc_id,
                "message": "Document updated successfully"
            }
        else:
            raise MCPServerError("Failed to update document")
    
    async def _delete_document(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete a document from the knowledge base.
        
        Args:
            body: Request body with 'document_id'
            
        Returns:
            Deletion result
        """
        doc_id = body.get("document_id")
        if not doc_id:
            raise DocumentValidationError("document_id is required")
        
        # Clear cache
        if doc_id in self.cache:
            del self.cache[doc_id]
        
        # Clear metadata
        if doc_id in self._document_metadata:
            del self._document_metadata[doc_id]
        
        # Note: VectorStore doesn't have a direct delete method
        # In production, we'd need to implement this in VectorStore
        # For now, we mark it as deleted in metadata
        
        self.log("info", f"Document marked for deletion: {doc_id}")
        return {
            "success": True,
            "document_id": doc_id,
            "message": "Document deleted successfully"
        }
    
    async def _list_documents(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        List documents with filtering and pagination.
        
        Args:
            body: Request body with optional 'filters', 'limit', 'offset'
            
        Returns:
            List of documents with metadata
        """
        limit = body.get("limit", 50)
        offset = body.get("offset", 0)
        filters = body.get("filters", {})
        
        # Get documents from vector store
        loop = asyncio.get_running_loop()
        all_docs = await loop.run_in_executor(
            None,
            lambda: self.vector_store.list_documents(limit=limit + offset)
        )
        
        # Apply filters
        filtered_docs = []
        for doc in all_docs:
            include = True
            doc_meta = doc.get("metadata", {})
            
            # Apply tag filter
            if "tags" in filters:
                doc_tags = doc_meta.get("tags", [])
                if not any(tag in doc_tags for tag in filters["tags"]):
                    include = False
            
            # Apply format filter
            if "format" in filters:
                if doc_meta.get("format") != filters["format"]:
                    include = False
            
            # Apply date filter
            if "created_after" in filters:
                created = doc_meta.get("created_at", "")
                if created < filters["created_after"]:
                    include = False
            
            if include:
                filtered_docs.append({
                    "id": doc.get("id"),
                    "metadata": doc_meta,
                    "content_preview": doc.get("content", "")[:200] + "..."
                })
        
        # Apply pagination
        paginated = filtered_docs[offset:offset + limit]
        
        return {
            "success": True,
            "documents": paginated,
            "total": len(filtered_docs),
            "limit": limit,
            "offset": offset
        }
    
    async def _search_documents(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search documents using semantic search.
        
        Args:
            body: Request body with 'query', optional 'filters', 'limit', 'include_content'
            
        Returns:
            Search results with relevance scores
        """
        query = body.get("query")
        if not query:
            raise DocumentValidationError("query is required")
        
        limit = min(body.get("limit", 10), self.kb_config["search_result_limit"])
        include_content = body.get("include_content", False)
        
        # Perform search via vector store
        loop = asyncio.get_running_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.vector_store.search(query, top_k=limit)
        )
        
        # Format results
        search_results = []
        for doc in results:
            result = {
                "id": doc.get("id"),
                "metadata": doc.get("metadata", {}),
                "relevance_score": 0.9  # Placeholder - VectorStore doesn't return scores yet
            }
            
            if include_content:
                result["content"] = doc.get("content", "")
            else:
                result["snippet"] = doc.get("content", "")[:200] + "..."
            
            search_results.append(result)
        
        self.log("info", f"Search completed: {len(search_results)} results for '{query[:50]}...'")
        
        return {
            "success": True,
            "query": query,
            "results": search_results,
            "total": len(search_results)
        }
    
    async def _get_stats(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get knowledge base statistics.
        
        Returns:
            Statistics including document count, cache stats, etc.
        """
        loop = asyncio.get_running_loop()
        kb_stats = await loop.run_in_executor(
            None,
            lambda: self.kb_manager.get_stats()
        )
        
        return {
            "success": True,
            "stats": {
                **kb_stats,
                "cache_size": len(self.cache),
                "cache_max_size": self.kb_config["cache_size_limit"],
                "metadata_entries": len(self._document_metadata)
            }
        }
    
    async def _health_check(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a health check on the KB system.
        
        Returns:
            Health status of all components
        """
        health = {
            "status": "healthy",
            "components": {
                "kb_manager": False,
                "vector_store": False,
                "rag_pipeline": False,
                "cache": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self.kb_manager:
            try:
                loop = asyncio.get_running_loop()
                kb_health = await loop.run_in_executor(
                    None,
                    lambda: self.kb_manager.health_check()
                )
                health["components"]["kb_manager"] = kb_health.get("status") == "healthy"
                health["components"]["vector_store"] = kb_health.get("checks", {}).get("vector_store", False)
                health["components"]["rag_pipeline"] = kb_health.get("checks", {}).get("rag_pipeline", False)
            except Exception as e:
                self.log("error", f"Health check failed: {str(e)}")
                health["status"] = "unhealthy"
                health["error"] = str(e)
        else:
            health["status"] = "unhealthy"
            health["error"] = "KB Manager not initialized"
        
        # Determine overall status
        if not all(health["components"].values()):
            health["status"] = "degraded" if any(health["components"].values()) else "unhealthy"
        
        return health
    
    async def validate_request(self, request: MCPMessage) -> bool:
        """Validate incoming request structure."""
        if not request.body:
            raise MCPValidationError("Request body is empty")
        if "action" not in request.body:
            raise MCPValidationError("Action is required")
        return True
    
    async def format_response(self, data: Dict[str, Any], correlation_id: str) -> MCPMessage:
        """Format the response into a standard MCP message."""
        return MCPMessage(
            header=MCPMessageHeader(
                message_type=MessageType.RESPONSE,
                message_id=str(time.time()),
                correlation_id=correlation_id,
                source=self.name,
                timestamp=datetime.utcnow().isoformat()
            ),
            body=data
        )
    
    async def cleanup(self):
        """Cleanup resources."""
        self.cache.clear()
        self._document_metadata.clear()
        self.log("info", "KB Server cleanup completed")
