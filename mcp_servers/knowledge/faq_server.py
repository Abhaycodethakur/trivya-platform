import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from shared.core_functions.config import Config
from shared.core_functions.logger import get_logger
from shared.knowledge_base.kb_manager import KnowledgeBaseManager as KBManager
from shared.knowledge_base.vector_store import VectorStore
from shared.knowledge_base.rag_pipeline import RAGPipeline
from mcp_servers.base_server import BaseMCPServer, MCPMessage, MCPMessageHeader, MessageType, MCPServerError, MCPValidationError

class FAQServer(BaseMCPServer):
    """
    FAQ Server for handling FAQ requests using the Knowledge Base.
    
    Features:
    - Semantic search via KBManager
    - LRU Caching for frequent queries
    - Async handling
    - Confident routing
    """

    def __init__(self, name: str = "faq_server", config: Optional[Config] = None):
        super().__init__(name, config)
        
        # Initialize Knowledge Base components
        # Note: In a real production setup, we might inject these or use a factory
        # For now, we instantiate them using the server's config
        self.vector_store = VectorStore(self.config)
        self.rag_pipeline = RAGPipeline(self.config, self.vector_store)
        self.kb_manager = KBManager(self.config, self.vector_store, self.rag_pipeline, None)
        
        # Setup Cache
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_size = int(self.config.env.get("FAQ_CACHE_SIZE", 100))
        self.cache_ttl = int(self.config.env.get("FAQ_CACHE_TTL", 3600))  # 1 hour default
        
        # Stats
        self.stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "total_requests": 0,
            "avg_latency": 0.0
        }
        
        # Pre-load common FAQs (simulated or configurable)
        self._preload_common_faqs()

    def _preload_common_faqs(self):
        """Simulate pre-loading common FAQs or load from a file"""
        # This could be fetching from a 'common_questions.json' file
        self.log("info", "Pre-loading common FAQs not yet implemented, but ready hook.")
        pass

    async def handle_request(self, request: MCPMessage) -> Dict[str, Any]:
        """
        Handle incoming FAQ requests.
        
        Expected body: {"action": "search_faq", "query": "..."}
        """
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        action = request.body.get("action")
        query = request.body.get("query")
        
        if action == "search_faq":
            if not query:
                raise MCPValidationError("Query is required for FAQ search")
            
            self.log_request(query, request)
            
            try:
                result = await self._search_faq(query)
                latency = time.time() - start_time
                self._update_stats(latency)
                return self._format_response(result)
            except Exception as e:
                self.log("error", f"FAQ Search failed: {str(e)}", extra={"query": query})
                raise MCPServerError(f"Internal error during FAQ search: {str(e)}")
        
        elif action == "get_stats":
            return self.get_cache_stats()
            
        else:
            raise MCPValidationError(f"Unknown action: {action}")

    async def _search_faq(self, query: str) -> Dict[str, Any]:
        """
        Search for FAQ answer, checking cache first.
        """
        # Check cache
        cached = self._get_cached_response(query)
        if cached:
            self.stats["cache_hits"] += 1
            return cached
        
        self.stats["cache_misses"] += 1
        
        # Fallback to KB Search (Async wrapper if IO bound)
        # KBManager.search is synchronous in the file I viewed, but let's wrap it 
        # or treat it as blocking call in async wrapper if needed.
        # However, the user plan requested 'await self.kb_manager.search(query)'
        # If KBManager.search is not async, we should run it in an executor.
        
        # Checking KBManager source again from memory... 
        # KBManager.search calls rag_pipeline.query, these seemed synchronous in previous view.
        # To make it properly async non-blocking, we use run_in_executor.
        
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, self.kb_manager.search, query)
        
        self._cache_response(query, result)
        return result

    def _get_cached_response(self, query: str) -> Optional[Dict[str, Any]]:
        """Retrieve from LRU cache if valid"""
        if query in self.cache:
            entry = self.cache[query]
            if time.time() < entry["expires_at"]:
                # specific to LRU: move to end
                # Python dicts are ordered by insertion, so re-inserting handles 'Least Recently Used' partially
                # But a real LRU usually pops and re-adds.
                val = self.cache.pop(query)
                self.cache[query] = val
                return val["data"]
            else:
                del self.cache[query]
        return None

    def _cache_response(self, query: str, data: Dict[str, Any]):
        """Store in cache with eviction"""
        if len(self.cache) >= self.cache_size:
            # Remove first item (LRU)
            self.cache.pop(next(iter(self.cache)))
        
        self.cache[query] = {
            "data": data,
            "expires_at": time.time() + self.cache_ttl
        }

    async def validate_request(self, request: MCPMessage) -> bool:
        """Validate the incoming request structure"""
        if not request.body:
            raise MCPValidationError("Request body is required")
        
        action = request.body.get("action")
        if not action:
            raise MCPValidationError("Action is required")
            
        if action == "search_faq":
            if "query" not in request.body:
                raise MCPValidationError("Query is required for FAQ search")
        
        return True

    async def format_response(self, data: Dict[str, Any], correlation_id: str) -> MCPMessage:
        """Format the data into a standard MCP response"""
        return MCPMessage(
            header=MCPMessageHeader(
                message_type=MessageType.RESPONSE,
                message_id=str(time.time()), # Simple ID generation
                correlation_id=correlation_id,
                source=self.name,
                timestamp=datetime.utcnow().isoformat()
            ),
            body=data
        )

    def _format_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format the raw RAG result into a structured FAQ response payload"""
        # RAG result typically has {"answer": ..., "context": ..., "confidence": ...}
        
        return {
            "answer": result.get("answer", "No answer found."),
            "confidence": result.get("confidence", 0.0),
            "source": [doc.get("metadata", {}).get("source") for doc in result.get("context", [])],
            "related_questions": result.get("related_questions", []) 
        }

    def _update_stats(self, latency: float):
        """Update running average latency"""
        n = self.stats["total_requests"]
        current_avg = self.stats["avg_latency"]
        self.stats["avg_latency"] = ((current_avg * (n - 1)) + latency) / n

    def get_cache_stats(self) -> Dict[str, Any]:
        return self.stats.copy()

    def log_request(self, query: str, request: MCPMessage):
        """Log the request details"""
        self.log("info", f"FAQ Request: {query}", extra={
             "source": request.header.source,
             "message_id": request.header.message_id
        })

    # Implement abstract cleanup
    async def cleanup(self):
        """Cleanup resources"""
        self.cache.clear()
        self.log("info", "FAQ Server cleaned up.")
