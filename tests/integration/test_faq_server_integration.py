import asyncio
import os
import pytest
import shutil
import tempfile
from datetime import datetime
from typing import Generator

# Import real components
from shared.core_functions.config import Config
from shared.core_functions.logger import get_logger, TrivyaLogger
from shared.core_functions.security import TrivyaSecurity
from shared.knowledge_base.kb_manager import KnowledgeBaseManager as KBManager
from shared.knowledge_base.vector_store import VectorStore
from shared.knowledge_base.rag_pipeline import RAGPipeline
from mcp_servers.knowledge.faq_server import FAQServer
from mcp_servers.base_server import MCPMessage, MCPMessageHeader, MessageType

from cryptography.fernet import Fernet

# --- integration setup ---

@pytest.fixture(scope="session")
def test_env():
    """Setup test environment variables"""
    # Backup original env
    old_env = os.environ.copy()
    
    # Set test env
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["LOG_OUTPUT"] = "file"
    # Create temp dir for logs
    temp_log_dir = tempfile.mkdtemp()
    os.environ["LOG_FILE_PATH"] = f"{temp_log_dir}/integration_test.log"
    os.environ["JWT_SECRET_KEY"] = "test_secret_key"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
    
    # Mock OpenAI API Key if not present (KBManager might need it for embeddings)
    if "OPENAI_API_KEY" not in os.environ:
         os.environ["OPENAI_API_KEY"] = "sk-test-key-mock"
    
    yield
    
    # Cleanup
    shutil.rmtree(temp_log_dir, ignore_errors=True)
    os.environ.clear()
    os.environ.update(old_env)

@pytest.fixture
def real_config(test_env):
    """Return a real Config object"""
    return Config()

@pytest.fixture
def integration_faq_server(real_config):
    """Fixture to create and manage an FAQServer instance"""
    server = FAQServer("integration_faq_server", real_config)
    # Ensure cache is clear
    server.cache.clear()
    yield server
    # Cleanup runs automatically via cleanup method if we called it, 
    # but we can also manually clear resources
    server.cache.clear()

@pytest.mark.asyncio
async def test_end_to_end_async_flow(integration_faq_server):
    """Test full async request handling"""
    # Note: With a mock OpenAI Key, the real Embedding generation will likely fail 
    # unless we mock the underlying call in VectorStore or RAGPipeline.
    # For *Integration* tests, ideally we have a real environment or a robust mock of the external service.
    # Since we can't guarantee a real API key in this environment, we should Mock the 'search' method 
    # of the internal kb_manager to return a result, BUT verify the rest of the flow (caching, logging, messaging)
    # uses the REAL server logic.
         
    # Mocking the internal KBManager search specifically to avoid external API calls
    # while testing the Server's async dispatching and caching.
    async def mock_search(query):
        await asyncio.sleep(0.1) # Simulate network delay
        return {
            "answer": "Integration Answer", 
            "confidence": 0.8, 
            "context": [{"metadata": {"source": "int_test"}}]
        }
    
    # Monkey patch the instance method
    # Since _search_faq calls loop.run_in_executor(None, self.kb_manager.search, query)
    # We need to mock self.kb_manager.search to be a valid callable.
    
    integration_faq_server.kb_manager.search = lambda q: {
        "answer": "Integration Answer", 
        "confidence": 0.8, 
        "context": [{"metadata": {"source": "int_test"}}]
    }
    
    query = "Integration Test Query"
    request = MCPMessage(
        header=MCPMessageHeader(message_type=MessageType.REQUEST, message_id="int1", source="tester"),
        body={"action": "search_faq", "query": query}
    )
    
    response = await integration_faq_server.handle_request(request)
    
    assert response["answer"] == "Integration Answer"
    assert response["confidence"] == 0.8
    assert response["source"] == ["int_test"]
    
    # Verify Stats
    stats = await integration_faq_server.handle_request(
        MCPMessage(header=MCPMessageHeader(message_type=MessageType.REQUEST, message_id="2", source="tester"),
        body={"action": "get_stats"})
    )
    assert stats["total_requests"] >= 1
    assert stats["cache_misses"] == 1

@pytest.mark.asyncio
async def test_cache_persistence_behavior(integration_faq_server):
    """Test that cache effectively prevents re-execution of search logic"""
    
    call_count = 0
    def side_effect(q):
        nonlocal call_count
        call_count += 1
        return {"answer": f"Answer {call_count}"}
        
    integration_faq_server.kb_manager.search = side_effect
    
    query = "Persistent Query"
    req = MCPMessage(
        header=MCPMessageHeader(message_type=MessageType.REQUEST, message_id="id", source="test"),
        body={"action": "search_faq", "query": query}
    )
    
    # 1st call
    await integration_faq_server.handle_request(req)
    assert call_count == 1
    
    # 2nd call
    await integration_faq_server.handle_request(req)
    assert call_count == 1 # Should rely on cache
    
    stats = integration_faq_server.get_cache_stats()
    assert stats["cache_hits"] == 1
    assert stats["cache_misses"] == 1

@pytest.mark.asyncio
async def test_performance_under_load(integration_faq_server):
    """Test concurrent request handling"""
    integration_faq_server.kb_manager.search = lambda q: {"answer": "Fast Answer"}
    
    queries = [f"Query {i}" for i in range(50)]
    tasks = []
    
    for q in queries:
        req = MCPMessage(
            header=MCPMessageHeader(message_type=MessageType.REQUEST, message_id="load", source="load_test"),
            body={"action": "search_faq", "query": q}
        )
        tasks.append(integration_faq_server.handle_request(req))
        
    start = datetime.now()
    results = await asyncio.gather(*tasks)
    duration = (datetime.now() - start).total_seconds()
    
    assert len(results) == 50
    # 50 requests should be very fast with mocked backend
    # Just asserting it didn't crash or take mostly long
    assert duration < 2.0 

if __name__ == "__main__":
    # Manually run if executed as script
    pass
