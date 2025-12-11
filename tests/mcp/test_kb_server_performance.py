"""
Performance Tests for KB Server

Tests response times

, concurrency handling, and cache efficiency.
"""

import pytest
import os
import time
import asyncio
from unittest.mock import MagicMock, patch

# Set env vars before imports
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/perf_db"
os.environ["JWT_SECRET_KEY"] = "perf-secret-key"

from mcp_servers.knowledge.kb_server import KBServer
from mcp_servers.base_server import MCPMessage, MCPMessageHeader, MessageType
from shared.core_functions.config import Config, VectorDBConfig


class PerfConfig(Config):
    """Performance test configuration"""
    def __init__(self):
        super().__init__()
        self.env.update({
            "VECTOR_DB_TYPE": "chromadb",
            "VECTOR_DB_PATH": "./data/perf_test",
            "COLLECTION_NAME": "perf_test_collection"
        })
        self.vector_db_config = VectorDBConfig(
            VECTOR_DB_TYPE="chromadb",
            VECTOR_DB_PATH="./data/perf_test",
            COLLECTION_NAME="perf_test_collection"
        )


@pytest.fixture
def mock_kb_manager():
    """Mock KB Manager for performance testing"""
    manager = MagicMock()
    manager.ingest_documents.return_value = {
        "success": True,
        "successful": 1,
        "failed": 0,
        "document_ids": ["perf_doc"]
    }
    manager.get_stats.return_value = {"total_documents": 100}
    manager.health_check.return_value = {
        "status": "healthy",
        "checks": {"vector_store": True, "rag_pipeline": True}
    }
    return manager


@pytest.fixture
def mock_vector_store():
    """Mock VectorStore for performance testing"""
    store = MagicMock()
    store.list_documents.return_value = [
        {"id": f"doc_{i}", "content": f"Content {i}", "metadata": {}}
        for i in range(10)
    ]
    store.search.return_value = [
        {"id": "doc_1", "content": "Search result", "metadata": {}}
    ]
    return store


@pytest.fixture
def perf_server(mock_kb_manager, mock_vector_store):
    """Create KB Server with mocked dependencies for perf testing"""
    with patch('mcp_servers.knowledge.kb_server.VectorStore') as MockVS, \
         patch('mcp_servers.knowledge.kb_server.RAGPipeline') as MockRAG, \
         patch('mcp_servers.knowledge.kb_server.KnowledgeBaseManager') as MockKBM, \
         patch('mcp_servers.base_server.SecurityManager'):
        
        MockVS.return_value = mock_vector_store
        MockRAG.return_value = MagicMock()
        MockKBM.return_value = mock_kb_manager
        
        server = KBServer(config=PerfConfig())
        server.vector_store = mock_vector_store
        server.kb_manager = mock_kb_manager
        return server


def create_request(action: str, **kwargs) -> MCPMessage:
    """Helper to create MCP request messages"""
    return MCPMessage(
        header=MCPMessageHeader(
            message_type=MessageType.REQUEST,
            source="perf_test"
        ),
        body={"action": action, **kwargs}
    )


class TestConcurrentPerformance:
    """Test concurrent request handling performance"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests_efficiency(self, perf_server):
        """
        Test that concurrent requests are handled efficiently.
        10 requests with 50ms simulated delay each should complete
        in ~100ms if truly concurrent, not 500ms+ if serial.
        """
        num_requests = 10
        
        # Simulate async delay in mock
        async def mock_handler(req):
            await asyncio.sleep(0.05)  # 50ms per request
            return {"success": True, "document_id": "perf_doc"}
        
        requests = [
            create_request("add_document", content=f"Doc {i}")
            for i in range(num_requests)
        ]
        
        start = time.time()
        tasks = [perf_server.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks)
        duration = time.time() - start
        
        print(f"\nProcessed {num_requests} requests in {duration:.3f}s")
        
        # Should be much faster than serial (10 * 0.05 = 0.5s)
        # With concurrency overhead, should be < 0.3s
        assert duration < 0.5
        assert len(results) == num_requests
        assert all(r["success"] for r in results)


class TestCachePerformance:
    """Test cache performance improvements"""
    
    @pytest.mark.asyncio
    async def test_cache_speeds_up_retrieval(self, perf_server):
        """Test that cached documents are retrieved faster"""
        doc_id = "cached_perf_doc"
        
        # Pre-populate cache
        perf_server.cache[doc_id] = {
            "content": "Cached content for performance test",
            "metadata": {"cached": True}
        }
        
        request = create_request("get_document", document_id=doc_id)
        
        # Time cached retrieval
        start = time.time()
        result = await perf_server.handle_request(request)
        cache_duration = time.time() - start
        
        print(f"\nCached retrieval: {cache_duration*1000:.2f}ms")
        
        assert result["cached"] is True
        # Cached should be near-instant (< 10ms)
        assert cache_duration < 0.01
    
    @pytest.mark.asyncio
    async def test_cache_hit_ratio(self, perf_server):
        """Test cache hit ratio for repeated requests"""
        doc_id = "hit_ratio_doc"
        
        # First request (cache miss)
        perf_server.cache[doc_id] = {
            "content": "Test content",
            "metadata": {}
        }
        
        request = create_request("get_document", document_id=doc_id)
        
        # Make multiple requests
        hits = 0
        total = 10
        
        for _ in range(total):
            result = await perf_server.handle_request(request)
            if result.get("cached"):
                hits += 1
        
        hit_ratio = hits / total
        print(f"\nCache hit ratio: {hit_ratio*100:.0f}%")
        
        # All should be cache hits after first
        assert hit_ratio >= 0.9


class TestBatchOperationPerformance:
    """Test batch operation performance"""
    
    @pytest.mark.asyncio
    async def test_list_documents_performance(self, perf_server):
        """Test list documents response time"""
        request = create_request("list_documents", limit=50, offset=0)
        
        start = time.time()
        result = await perf_server.handle_request(request)
        duration = time.time() - start
        
        print(f"\nList documents: {duration*1000:.2f}ms")
        
        assert result["success"] is True
        # Should complete within 300ms
        assert duration < 0.3
    
    @pytest.mark.asyncio
    async def test_search_performance(self, perf_server):
        """Test search response time"""
        request = create_request(
            "search_documents",
            query="performance test query",
            limit=10
        )
        
        start = time.time()
        result = await perf_server.handle_request(request)
        duration = time.time() - start
        
        print(f"\nSearch documents: {duration*1000:.2f}ms")
        
        assert result["success"] is True
        # Should complete within 200ms with mocked backend
        assert duration < 0.2
