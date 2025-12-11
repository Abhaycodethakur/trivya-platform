import pytest
import os
import shutil
import asyncio
from mcp_servers.knowledge.rag_server import RAGServer
from mcp_servers.base_server import MCPMessage, MCPMessageHeader, MessageType
from shared.core_functions.config import Config

# Use the user-provided key for integration testing if env var not set
# In a real CI this would be a secret, but user explicitly provided it in chat
TEST_API_KEY = "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"

class IntegrationConfig(Config):
    def __init__(self, db_path):
        super().__init__() # Initialize base defaults
        
        # Override env
        self.env.update({
            "VECTOR_DB_TYPE": "chromadb",
            "VECTOR_DB_PATH": db_path,
            "COLLECTION_NAME": "integration_test_rag",
            "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY", TEST_API_KEY),
            "RAG_MODEL": "google/gemma-3-27b-it:free",
            "RAG_CACHE_SIZE": 100,
            "RAG_CACHE_TTL": 3600
        })
        
        # Override vector config
        from shared.core_functions.config import VectorDBConfig
        self.vector_db_config = VectorDBConfig(
            VECTOR_DB_TYPE="chromadb",
            VECTOR_DB_PATH=db_path,
            COLLECTION_NAME="integration_test_rag"
        )

@pytest.fixture(scope="module")
def vector_db_path():
    # Set required env vars for SecurityManager and Config
    os.environ["JWT_SECRET_KEY"] = "test-secret-integration"
    os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/test_db"
    
    path = "./data/chromadb_integration_rag"
    os.makedirs(path, exist_ok=True)
    yield path
    # Cleanup
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
        except PermissionError:
            print(f"Warning: Could not delete test directory {path} due to file locks.")

@pytest.fixture(scope="module")
def rag_server_integration(vector_db_path):
    config = IntegrationConfig(vector_db_path)
    server = RAGServer(config=config)
    
    # Populate Vector DB with some test data
    # Note: RAGServer doesn't have ingest methods, we access vector_store directly
    if server.vector_store:
        # Reset collection to ensure clean state from previous runs
        try:
            server.vector_store.delete_collection()
        except:
            pass # Ignore if collection doesn't exist or other error
            
        server.vector_store.add_documents([
            {"id": "test_1", "content": "The capital of France is Paris. It is known for the Eiffel Tower.", "metadata": {"source": "geo"}},
            {"id": "test_2", "content": "Python is a programming language created by Guido van Rossum.", "metadata": {"source": "tech"}},
            {"id": "test_3", "content": "The speed of light is approximately 299,792 kilometers per second.", "metadata": {"source": "physics"}}
        ])
    
    return server

@pytest.mark.asyncio
async def test_full_rag_flow(rag_server_integration):
    """Test end-to-end RAG flow: Retrieval + Generation"""
    
    # Verify vector store works first
    results = rag_server_integration.vector_store.search("France capital")
    assert len(results) > 0
    assert "Paris" in results[0]["content"]

    request = MCPMessage(
        header=MCPMessageHeader(message_type=MessageType.REQUEST, source="integration_test"),
        body={"query": "What is the capital of France and what is it known for?"}
    )
    
    response = await rag_server_integration.handle_request(request)
    
    assert response["answer"] is not None
    assert isinstance(response["answer"], str)
    assert len(response["answer"]) > 10
    assert "Paris" in response["answer"] or "Eiffel" in response["answer"]
    
    # Check sources
    assert len(response["sources"]) > 0
    assert response["sources"][0]["id"] == "test_1"

@pytest.mark.asyncio
async def test_rag_flow_no_knowledge(rag_server_integration):
    """Test query where no knowledge exists"""
    
    request = MCPMessage(
        header=MCPMessageHeader(message_type=MessageType.REQUEST, source="integration_test"),
        body={"query": "What is the recipe for Glup Shitto's famous stew?"} 
        # Hopefully not in the vector DB
    )
    
    response = await rag_server_integration.handle_request(request)
    
    # LLM should say it doesn't know or hallucinate conservatively based on prompt instructions
    # Prompt says: If the answer cannot be found in the context, say "I don't have enough information to answer that."
    assert "I don't have enough information" in response["answer"] or "context" in response["answer"]

@pytest.mark.asyncio
async def test_concurrent_requests(rag_server_integration):
    """Test multiple concurrent requests"""
    import asyncio
    
    queries = [
        "Who created Python?",
        "How fast is light?",
        "Capital of France?"
    ]
    
    tasks = []
    for q in queries:
        req = MCPMessage(
            header=MCPMessageHeader(message_type=MessageType.REQUEST, source="integration_test"),
            body={"query": q}
        )
        tasks.append(rag_server_integration.handle_request(req))
        
    responses = await asyncio.gather(*tasks)
    
    assert len(responses) == 3
    assert "Guido" in responses[0]["answer"]
    assert "299,792" in responses[1]["answer"] or "light" in responses[1]["answer"]
    assert "Paris" in responses[2]["answer"]

