import pytest
import asyncio
from unittest.mock import MagicMock, patch
from mcp_servers.knowledge.rag_server import RAGServer, VectorStoreError, LLMGenerationError
from mcp_servers.base_server import MCPMessage, MCPMessageHeader, MessageType, MCPValidationError, MCPServerError

class MockConfig:
    def __init__(self):
        self.env = {
            "LOG_LEVEL": "INFO",
            "LOG_FORMAT": "json",
            "LOG_OUTPUT": "console",
            "LOG_FILE_PATH": "logs/test.log",
            "OPENROUTER_API_KEY": "test-key",
            "RAG_CACHE_SIZE": 10,
            "RAG_CACHE_TTL": 60,
            "RAG_MAX_DOCS": 2
        }

@pytest.fixture
def mock_config():
    return MockConfig()

@pytest.fixture
def rag_server(mock_config):
    with patch("mcp_servers.knowledge.rag_server.VectorStore") as MockVectorStore, \
         patch("mcp_servers.base_server.SecurityManager"):
        server = RAGServer(config=mock_config)
        server.vector_store = MockVectorStore.return_value
        return server

@pytest.mark.asyncio
async def test_initialization(rag_server):
    assert rag_server.name == "rag_server"
    assert rag_server.vector_store is not None
    assert rag_server.openrouter_api_key == "test-key"

@pytest.mark.asyncio
async def test_handle_request_success(rag_server):
    # Mock Vector Store search
    rag_server.vector_store.search.return_value = [
        {"id": "doc1", "content": "The sky is blue.", "metadata": {"source": "nature_doc"}},
        {"id": "doc2", "content": "Grass is green.", "metadata": {"source": "nature_doc"}}
    ]
    
    # Mock LLM Call
    with patch.object(rag_server, "_call_llm", return_value="The sky is blue."):
        request = MCPMessage(
            header=MCPMessageHeader(message_type=MessageType.REQUEST, source="client"),
            body={"query": "What color is the sky?"}
        )
        
        response = await rag_server.handle_request(request)
        
        assert response["answer"] == "The sky is blue."
        assert len(response["sources"]) == 2
        assert response["confidence"] > 0.8
        assert response["sources"][0]["id"] == "doc1"

@pytest.mark.asyncio
async def test_handle_request_validation_error(rag_server):
    request = MCPMessage(
        header=MCPMessageHeader(message_type=MessageType.REQUEST, source="client"),
        body={} # Missing query
    )
    
    with pytest.raises(MCPValidationError):
        await rag_server.handle_request(request)

@pytest.mark.asyncio
async def test_handle_request_vector_store_error(rag_server):
    rag_server.vector_store.search.side_effect = VectorStoreError("DB Connection Failed")
    
    request = MCPMessage(
        header=MCPMessageHeader(message_type=MessageType.REQUEST, source="client"),
        body={"query": "test"}
    )
    
    with pytest.raises(MCPServerError) as excinfo:
        await rag_server.handle_request(request)
    assert "Knowledge retrieval failed" in str(excinfo.value)

@pytest.mark.asyncio
async def test_handle_request_llm_error(rag_server):
    rag_server.vector_store.search.return_value = []
    
    with patch.object(rag_server, "_call_llm", side_effect=LLMGenerationError("API Error")):
        request = MCPMessage(
            header=MCPMessageHeader(message_type=MessageType.REQUEST, source="client"),
            body={"query": "test"}
        )
        
        with pytest.raises(MCPServerError) as excinfo:
            await rag_server.handle_request(request)
        assert "Answer generation failed" in str(excinfo.value)

@pytest.mark.asyncio
async def test_caching(rag_server):
    rag_server.vector_store.search.return_value = [{"content": "A", "metadata": {}}]
    
    with patch.object(rag_server, "_call_llm", return_value="Answer A") as mock_llm:
        request = MCPMessage(
            header=MCPMessageHeader(message_type=MessageType.REQUEST, source="client"),
            body={"query": "same query"}
        )
        
        # First call
        await rag_server.handle_request(request)
        assert mock_llm.call_count == 1
        
        # Second call (should hit cache)
        await rag_server.handle_request(request)
        assert mock_llm.call_count == 1 # Still 1

def test_build_prompt(rag_server):
    prompt = rag_server._build_prompt("Question?", "Context...")
    assert "Question?" in prompt
    assert "Context..." in prompt
    assert "ONLY on the provided context" in prompt

