import asyncio
import json
import unittest
import time
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

from mcp_servers.base_server import MCPMessage, MCPMessageHeader, MessageType, MCPServerError, MCPValidationError
from mcp_servers.knowledge.faq_server import FAQServer

class TestFAQServer(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.mock_config = MagicMock()
        self.mock_config.env = {} # Mock env dict
        self.mock_config.env.get = MagicMock(side_effect=lambda key, default=None: {
            "FAQ_CACHE_SIZE": 2,
            "FAQ_CACHE_TTL": 1
        }.get(key, default))
        
        # Patch KBManager components to prevent real instantation
        self.vector_store_patcher = patch('mcp_servers.knowledge.faq_server.VectorStore')
        self.rag_pipeline_patcher = patch('mcp_servers.knowledge.faq_server.RAGPipeline')
        self.kb_manager_patcher = patch('mcp_servers.knowledge.faq_server.KBManager')
        self.get_logger_patcher = patch('mcp_servers.base_server.get_logger')
        
        self.MockVectorStore = self.vector_store_patcher.start()
        self.MockRAGPipeline = self.rag_pipeline_patcher.start()
        self.MockKBManager = self.kb_manager_patcher.start()
        self.MockGetLogger = self.get_logger_patcher.start()
        
        # Setup mock logger
        self.mock_logger_instance = MagicMock()
        self.MockGetLogger.return_value = self.mock_logger_instance
        
        # Setup mock KBManager instance
        self.mock_kb_instance = self.MockKBManager.return_value
        
        self.server = FAQServer(name="test_faq", config=self.mock_config)
        self.server._log = MagicMock()

    def tearDown(self):
        self.vector_store_patcher.stop()
        self.rag_pipeline_patcher.stop()
        self.kb_manager_patcher.stop()
        self.get_logger_patcher.stop()

    async def test_search_faq_success(self):
        """Test successful FAQ search with simulated IO bound KB search"""
        query = "How do I return items?"
        
        # Mock KBManager.search side effect to be synchronous as per implementation assumption
        self.mock_kb_instance.search.return_value = {
            "answer": "You can return items within 30 days.",
            "confidence": 0.95,
            "context": [{"metadata": {"source": "returns.md"}}],
            "related_questions": ["What is the refund policy?"]
        }
        
        request = MCPMessage(
            header=MCPMessageHeader(
                message_type=MessageType.REQUEST, 
                message_id="1", 
                source="test"
            ),
            body={"action": "search_faq", "query": query}
        )
        
        response = await self.server.handle_request(request)
        
        self.assertEqual(response["answer"], "You can return items within 30 days.")
        self.assertEqual(response["confidence"], 0.95)
        self.assertEqual(response["source"], ["returns.md"])
        
        # Verify cache interaction
        self.assertIn(query, self.server.cache)
        self.assertEqual(self.server.stats["cache_misses"], 1)

    async def test_caching_mechanism(self):
        """Test cache hit and eviction"""
        query = "Cached Query"
        self.mock_kb_instance.search.return_value = {"answer": "Cached Answer"}
        
        request = MCPMessage(
            header=MCPMessageHeader(message_type=MessageType.REQUEST, message_id="1", source="test"),
            body={"action": "search_faq", "query": query}
        )
        
        # First call - Miss
        await self.server.handle_request(request)
        self.assertEqual(self.server.stats["cache_misses"], 1)
        self.assertEqual(self.server.stats["cache_hits"], 0)
        
        # Second call - Hit
        await self.server.handle_request(request)
        self.assertEqual(self.server.stats["cache_misses"], 1)
        self.assertEqual(self.server.stats["cache_hits"], 1)
        
        # Verify KB was only called once
        self.assertEqual(self.mock_kb_instance.search.call_count, 1)

    async def test_cache_expiration(self):
        """Test that cache expires after TTL"""
        query = "Short lived query"
        self.mock_kb_instance.search.return_value = {"answer": "A"}
        
        self.server._cache_response(query, {"answer": "A"})
        self.server.cache[query]["expires_at"] = time.time() - 1 # Expire immediately
        
        # Should be a miss
        cached = self.server._get_cached_response(query)
        self.assertIsNone(cached)
        self.assertNotIn(query, self.server.cache)

    async def test_lru_eviction(self):
        """Test that oldest items are evicted when cache is full"""
        # Cache size is 2
        self.server._cache_response("Q1", "A1")
        self.server._cache_response("Q2", "A2")
        
        # Access Q1 to make it recent
        self.server._get_cached_response("Q1")
        
        # Add Q3, should evict Q2 (since Q1 was just used)
        self.server._cache_response("Q3", "A3")
        
        self.assertIn("Q1", self.server.cache)
        self.assertIn("Q3", self.server.cache)
        self.assertNotIn("Q2", self.server.cache)

    async def test_error_handling(self):
        """Test internal server error propagation"""
        query = "Error Query"
        self.mock_kb_instance.search.side_effect = Exception("KB is down")
        
        request = MCPMessage(
            header=MCPMessageHeader(message_type=MessageType.REQUEST, message_id="1", source="test"),
            body={"action": "search_faq", "query": query}
        )
        
        with self.assertRaises(MCPServerError) as cm:
            await self.server.handle_request(request)
        
        self.assertIn("Internal error during FAQ search", str(cm.exception))

    async def test_response_structure_validation(self):
        """Ensure response matches expected schema even with partial KB data"""
        query = "Partial Data"
        self.mock_kb_instance.search.return_value = {} # Empty result
        
        request = MCPMessage(
            header=MCPMessageHeader(message_type=MessageType.REQUEST, message_id="1", source="test"),
            body={"action": "search_faq", "query": query}
        )
        
        response = await self.server.handle_request(request)
        self.assertEqual(response["answer"], "No answer found.")
        self.assertEqual(response["confidence"], 0.0)
        self.assertEqual(response["related_questions"], [])
        
    async def test_logging_integration(self):
        """Test that requests are logged"""
        query = "Log me"
        self.mock_kb_instance.search.return_value = {"answer": "Logged"}
        
        request = MCPMessage(
            header=MCPMessageHeader(message_type=MessageType.REQUEST, message_id="log123", source="tester"),
            body={"action": "search_faq", "query": query}
        )
        
        await self.server.handle_request(request)
        
        # Verify log called
        self.server._log.assert_called()
        call_args = self.server._log.call_args
        self.assertEqual(call_args[0][0], "info") # level
        self.assertIn(query, call_args[0][1]) # message contains query

if __name__ == "__main__":
    unittest.main()
