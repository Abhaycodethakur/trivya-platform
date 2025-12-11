import pytest
import asyncio
import time
from unittest.mock import MagicMock, AsyncMock
from mcp_servers.knowledge.rag_server import RAGServer
from mcp_servers.base_server import MCPMessage, MCPMessageHeader, MessageType
from shared.core_functions.config import Config

class PerformanceConfig(Config):
    def __init__(self):
        super().__init__()
        self.env.update({
             "RAG_MODEL": "test-model",
             "OPENROUTER_API_KEY": "test-key"
        })
        # Mock vector config
        from shared.core_functions.config import VectorDBConfig
        self.vector_db_config = VectorDBConfig(
            VECTOR_DB_TYPE="chromadb",
            VECTOR_DB_PATH="./data/test_perf",
            COLLECTION_NAME="perf_test"
        )

@pytest.fixture
def mock_dependencies():
    import os
    os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/perf_db"
    os.environ["JWT_SECRET_KEY"] = "perf-secret"
    
    vector_store = MagicMock()
    # Simulate some delay in DB search to test async non-blocking
    vector_store.search.side_effect = lambda q, top_k: [{"content": "Result", "metadata": {"source": "test"}}]
    return vector_store

@pytest.fixture
def rag_server_perf(mock_dependencies):
    config = PerformanceConfig()
    server = RAGServer(config=config)
    server.vector_store = mock_dependencies
    
    # Mock LLM call to simulate network delay
    async def mock_call_llm(prompt):
        await asyncio.sleep(0.1) # 100ms simulated delay
        return "This is a generated answer."
    
    server._call_llm = mock_call_llm
    return server

@pytest.mark.asyncio
async def test_concurrent_request_performance(rag_server_perf):
    """
    Test that the server handles multiple requests concurrently.
    If it was serial, 10 requests * 0.1s would take > 1.0s.
    With concurrency, it should be much faster (close to 0.1s + overhead).
    """
    num_requests = 10
    requests = [
        MCPMessage(
            header=MCPMessageHeader(message_type=MessageType.REQUEST, source="perf_test"),
            body={"query": f"Query {i}"}
        )
        for i in range(num_requests)
    ]
    
    start_time = time.time()
    tasks = [rag_server_perf.handle_request(req) for req in requests]
    responses = await asyncio.gather(*tasks)
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"\nProcessed {num_requests} requests in {duration:.4f}s")
    
    # Assert it was faster than serial execution
    # 10 * 0.1s = 1.0s. Allowing some overhead, it should be < 0.5s if effectively concurrent
    assert duration < 0.5
    assert len(responses) == num_requests

@pytest.mark.asyncio
async def test_cache_performance(rag_server_perf):
    """Test response time improvement with caching"""
    request = MCPMessage(
        header=MCPMessageHeader(message_type=MessageType.REQUEST, source="perf_test"),
        body={"query": "Repeated Query"}
    )
    
    # First call (uncached)
    start = time.time()
    await rag_server_perf.handle_request(request)
    first_duration = time.time() - start
    
    # Second call (cached)
    start = time.time()
    await rag_server_perf.handle_request(request)
    second_duration = time.time() - start
    
    print(f"\nUncached: {first_duration:.4f}s, Cached: {second_duration:.4f}s")
    
    # Cached should be significantly faster (near instant)
    assert second_duration < first_duration
    assert second_duration < 0.01 # Should be sub-millisecond essentially
