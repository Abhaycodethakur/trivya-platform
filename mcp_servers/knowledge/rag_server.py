import asyncio
import json
import logging
import time
import os
import requests
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from cachetools import TTLCache
from shared.core_functions.config import Config
from shared.core_functions.logger import get_logger
from shared.knowledge_base.vector_store import VectorStore
from mcp_servers.base_server import BaseMCPServer, MCPMessage, MCPMessageHeader, MessageType, MCPServerError, MCPValidationError

class VectorStoreError(Exception):
    pass

class LLMGenerationError(Exception):
    pass

class InvalidRequestError(Exception):
    pass

class RAGServer(BaseMCPServer):
    """
    RAG Server for handling retrieval-augmented generation requests.
    
    Features:
    - Semantic search via VectorStore
    - LLM generation via OpenRouter (Gemini 2.0 Flash)
    - TTLCache for frequent queries
    - Async handling
    """
    
    def __init__(self, name: str = "rag_server", config: Optional[Config] = None):
        super().__init__(name, config)
        
        # Initialize Vector Store
        try:
            self.vector_store = VectorStore(self.config)
        except Exception as e:
            self.log("error", f"Failed to initialize VectorStore: {str(e)}")
            # We might want to raise this, but BaseMCPServer might handle it nicely
            # For now, let's allow it but subsequent calls will fail
            self.vector_store = None

        # Setup Cache
        # Use config or defaults from plan
        cache_size = int(self.config.env.get("RAG_CACHE_SIZE", 100))
        cache_ttl = int(self.config.env.get("RAG_CACHE_TTL", 3600))
        self.cache = TTLCache(maxsize=cache_size, ttl=cache_ttl)
        
        # LLM Config
        self.openrouter_api_key = self.config.env.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        self.model = self.config.env.get("RAG_MODEL", "google/gemini-2.0-flash-experimental")
        self.max_context_length = 1000000 
        
        # RAG Config
        self.max_retrieved_docs = int(self.config.env.get("RAG_MAX_DOCS", 5))
        self.similarity_threshold = float(self.config.env.get("RAG_SIMILARITY_THRESHOLD", 0.7))

    async def handle_request(self, request: MCPMessage) -> Dict[str, Any]:
        """
        Handle incoming RAG requests.
        
        Expected body: {"query": "..."}
        """
        if not request.body or "query" not in request.body:
             raise MCPValidationError("Query is required")
             
        query = request.body.get("query")
        
        # Check cache
        if query in self.cache:
            self.log("info", f"Cache hit for query: {query}")
            return self.cache[query]
            
        try:
            # 1. Retrieve Documents
            if not self.vector_store:
                 raise VectorStoreError("VectorStore not initialized")
                 
            # Run vector search in executor to avoid blocking
            loop = asyncio.get_running_loop()
            docs = await loop.run_in_executor(
                None, 
                lambda: self.vector_store.search(query, top_k=self.max_retrieved_docs)
            )
            
            # Filter by relevance if possible (Chroma returns distances usually, conversion needed)
            # Assuming VectorStore returns a standard format list of dicts with 'metadata' and 'content'
            
            context_text = "\n\n".join([d.get("content", "") for d in docs])
            
            # 2. Build Prompt
            prompt = self._build_prompt(query, context_text)
            
            # 3. Call LLM
            llm_response = await self._call_llm(prompt)
            
            # 4. Format Response
            response_data = {
                "answer": llm_response,
                "sources": [
                    {
                        "id": d.get("id", "unknown"),
                        "title": d.get("metadata", {}).get("source", "Unknown"), 
                        "snippet": d.get("content", "")[:200] + "...",
                        "relevance_score": 0.0 # Placeholder as VectorStore might not return normalized score yet
                    } for d in docs
                ],
                "confidence": self._calculate_confidence(llm_response, docs)
            }
            
            # 5. Cache
            self.cache[query] = response_data
            
            return response_data
            
        except VectorStoreError as e:
            self.log("error", f"Vector store error: {str(e)}")
            raise MCPServerError(f"Knowledge retrieval failed: {str(e)}")
        except LLMGenerationError as e:
            self.log("error", f"LLM error: {str(e)}")
            raise MCPServerError(f"Answer generation failed: {str(e)}")
        except Exception as e:
            self.log("error", f"Unexpected error: {str(e)}")
            raise MCPServerError(f"Internal server error: {str(e)}")

    def _build_prompt(self, query: str, context: str) -> str:
        """Construct the prompt for RAG"""
        return f"""You are a helpful assistant for the Trivya platform.
Answer the following question based ONLY on the provided context.
If the answer cannot be found in the context, say "I don't have enough information to answer that."

Context:
{context}

Question:
{query}

Answer:"""

    async def _call_llm(self, prompt: str) -> str:
        """Call OpenRouter API"""
        if not self.openrouter_api_key:
            raise LLMGenerationError("OpenRouter API key not configured")
            
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://trivya.com", # Required by OpenRouter
            "X-Title": "Trivya Platform"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            # Use run_in_executor for blocking requests call
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
            )
            
            if response.status_code != 200:
                raise LLMGenerationError(f"API Error: {response.text}")
                
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                raise LLMGenerationError("No choices in API response")
                
        except Exception as e:
            raise LLMGenerationError(str(e))

    def _calculate_confidence(self, answer: str, docs: List[Dict]) -> float:
        """
        Calculate a simple confidence score.
        Real implementation would be more complex.
        """
        if not docs:
            return 0.0
        if "I don't have enough information" in answer:
            return 0.1
        return 0.9 # High confidence if docs exist and answer generated

    async def validate_request(self, request: MCPMessage) -> bool:
        """Validate request structure"""
        if not request.body:
             raise MCPValidationError("Request body is empty")
        if "query" not in request.body:
             raise MCPValidationError("Query is required")
        return True

    async def format_response(self, data: Dict[str, Any], correlation_id: str) -> MCPMessage:
        """Format the response into a standard MCP message"""
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
        self.cache.clear()
