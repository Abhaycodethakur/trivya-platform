"""
Unit Tests for KB Server

Comprehensive tests covering initialization, document operations,
caching, security, and error handling.
"""

import pytest
import os
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

# Set env vars before imports
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/test_db"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

from mcp_servers.knowledge.kb_server import (
    KBServer, DocumentNotFoundError, DocumentValidationError
)
from mcp_servers.base_server import (
    MCPMessage, MCPMessageHeader, MessageType, 
    MCPServerError, MCPValidationError
)


class MockConfig:
    """Mock configuration for testing"""
    def __init__(self):
        self.env = {
            "VECTOR_DB_TYPE": "chromadb",
            "VECTOR_DB_PATH": "./data/test_kb",
            "COLLECTION_NAME": "test_kb_collection",
            "LOG_LEVEL": "DEBUG"
        }
        self.vector_db_config = MagicMock()
        self.vector_db_config.VECTOR_DB_TYPE = "chromadb"
        self.vector_db_config.VECTOR_DB_PATH = "./data/test_kb"
        self.vector_db_config.COLLECTION_NAME = "test_kb_collection"


@pytest.fixture
def mock_config():
    return MockConfig()


@pytest.fixture
def mock_kb_manager():
    manager = MagicMock()
    manager.ingest_documents.return_value = {
        "success": True,
        "successful": 1,
        "failed": 0,
        "document_ids": ["doc_123"]
    }
    manager.update_document.return_value = True
    manager.get_stats.return_value = {
        "total_documents": 10,
        "total_queries": 5
    }
    manager.health_check.return_value = {
        "status": "healthy",
        "checks": {"vector_store": True, "rag_pipeline": True}
    }
    return manager


@pytest.fixture
def mock_vector_store():
    store = MagicMock()
    store.list_documents.return_value = [
        {"id": "doc_1", "content": "Test content 1", "metadata": {"source": "test"}},
        {"id": "doc_2", "content": "Test content 2", "metadata": {"source": "test"}}
    ]
    store.search.return_value = [
        {"id": "doc_1", "content": "Relevant content", "metadata": {"source": "search"}}
    ]
    return store


@pytest.fixture
def kb_server(mock_config, mock_kb_manager, mock_vector_store):
    """Create KB Server with mocked dependencies"""
    with patch('mcp_servers.knowledge.kb_server.VectorStore') as MockVS, \
         patch('mcp_servers.knowledge.kb_server.RAGPipeline') as MockRAG, \
         patch('mcp_servers.knowledge.kb_server.KnowledgeBaseManager') as MockKBM, \
         patch('mcp_servers.base_server.SecurityManager'):
        
        MockVS.return_value = mock_vector_store
        MockRAG.return_value = MagicMock()
        MockKBM.return_value = mock_kb_manager
        
        server = KBServer(config=mock_config)
        server.vector_store = mock_vector_store
        server.kb_manager = mock_kb_manager
        return server


def create_request(action: str, **kwargs) -> MCPMessage:
    """Helper to create MCP request messages"""
    return MCPMessage(
        header=MCPMessageHeader(
            message_type=MessageType.REQUEST,
            source="test"
        ),
        body={"action": action, **kwargs}
    )


# ============ Initialization Tests ============

class TestKBServerInitialization:
    """Test server initialization"""
    
    def test_initialization_with_defaults(self, kb_server):
        """Test server initializes with default config"""
        assert kb_server.name == "kb_server"
        assert kb_server.kb_config["max_document_size"] == 10485760
        assert kb_server.kb_config["cache_size_limit"] == 100
    
    def test_valid_actions_defined(self, kb_server):
        """Test valid actions are properly defined"""
        expected_actions = [
            "add_document", "get_document", "update_document",
            "delete_document", "list_documents", "search_documents",
            "get_stats", "health_check"
        ]
        assert all(action in kb_server.VALID_ACTIONS for action in expected_actions)


# ============ Document Operation Tests ============

class TestAddDocument:
    """Test add_document operation"""
    
    @pytest.mark.asyncio
    async def test_add_document_success(self, kb_server):
        """Test adding a valid document"""
        request = create_request(
            "add_document",
            content="This is test content",
            metadata={"title": "Test Doc", "tags": ["test"]}
        )
        
        result = await kb_server.handle_request(request)
        
        assert result["success"] is True
        assert "document_id" in result
        assert result["document_id"] == "doc_123"
    
    @pytest.mark.asyncio
    async def test_add_document_missing_content(self, kb_server):
        """Test adding document without content fails"""
        request = create_request("add_document", metadata={"title": "No Content"})
        
        with pytest.raises(MCPValidationError) as exc:
            await kb_server.handle_request(request)
        
        assert "content is required" in str(exc.value).lower()
    
    @pytest.mark.asyncio
    async def test_add_document_exceeds_size_limit(self, kb_server):
        """Test adding document that exceeds size limit"""
        # Create content larger than 10MB
        large_content = "x" * (11 * 1024 * 1024)  # 11MB
        request = create_request("add_document", content=large_content)
        
        with pytest.raises(MCPValidationError) as exc:
            await kb_server.handle_request(request)
        
        assert "exceeds maximum size" in str(exc.value).lower()


class TestGetDocument:
    """Test get_document operation"""
    
    @pytest.mark.asyncio
    async def test_get_document_success(self, kb_server, mock_vector_store):
        """Test retrieving an existing document"""
        mock_vector_store.list_documents.return_value = [
            {"id": "doc_1", "content": "Test content", "metadata": {"source": "test"}}
        ]
        
        request = create_request("get_document", document_id="doc_1")
        result = await kb_server.handle_request(request)
        
        assert result["success"] is True
        assert result["document_id"] == "doc_1"
        assert "content" in result
    
    @pytest.mark.asyncio
    async def test_get_document_not_found(self, kb_server, mock_vector_store):
        """Test retrieving non-existent document"""
        mock_vector_store.list_documents.return_value = []
        
        request = create_request("get_document", document_id="nonexistent")
        
        with pytest.raises(MCPValidationError) as exc:
            await kb_server.handle_request(request)
        
        assert "not found" in str(exc.value).lower()
    
    @pytest.mark.asyncio
    async def test_get_document_missing_id(self, kb_server):
        """Test get document without ID fails"""
        request = create_request("get_document")
        
        with pytest.raises(MCPValidationError) as exc:
            await kb_server.handle_request(request)
        
        assert "document_id is required" in str(exc.value).lower()


class TestUpdateDocument:
    """Test update_document operation"""
    
    @pytest.mark.asyncio
    async def test_update_document_success(self, kb_server):
        """Test updating an existing document"""
        request = create_request(
            "update_document",
            document_id="doc_1",
            content="Updated content",
            metadata={"updated": True}
        )
        
        result = await kb_server.handle_request(request)
        
        assert result["success"] is True
        assert result["document_id"] == "doc_1"
    
    @pytest.mark.asyncio
    async def test_update_document_missing_content(self, kb_server):
        """Test update without content fails"""
        request = create_request("update_document", document_id="doc_1")
        
        with pytest.raises(MCPValidationError) as exc:
            await kb_server.handle_request(request)
        
        assert "content is required" in str(exc.value).lower()


class TestDeleteDocument:
    """Test delete_document operation"""
    
    @pytest.mark.asyncio
    async def test_delete_document_success(self, kb_server):
        """Test deleting a document"""
        request = create_request("delete_document", document_id="doc_1")
        
        result = await kb_server.handle_request(request)
        
        assert result["success"] is True
        assert result["document_id"] == "doc_1"


class TestSearchDocuments:
    """Test search_documents operation"""
    
    @pytest.mark.asyncio
    async def test_search_documents_success(self, kb_server):
        """Test searching documents"""
        request = create_request(
            "search_documents",
            query="test query",
            limit=5
        )
        
        result = await kb_server.handle_request(request)
        
        assert result["success"] is True
        assert "results" in result
        assert result["query"] == "test query"
    
    @pytest.mark.asyncio
    async def test_search_documents_missing_query(self, kb_server):
        """Test search without query fails"""
        request = create_request("search_documents")
        
        with pytest.raises(MCPValidationError) as exc:
            await kb_server.handle_request(request)
        
        assert "query is required" in str(exc.value).lower()


class TestListDocuments:
    """Test list_documents operation"""
    
    @pytest.mark.asyncio
    async def test_list_documents_success(self, kb_server):
        """Test listing documents"""
        request = create_request("list_documents", limit=10, offset=0)
        
        result = await kb_server.handle_request(request)
        
        assert result["success"] is True
        assert "documents" in result
        assert result["limit"] == 10
        assert result["offset"] == 0


# ============ Caching Tests ============

class TestCaching:
    """Test document caching functionality"""
    
    @pytest.mark.asyncio
    async def test_document_cached_after_add(self, kb_server):
        """Test document is cached after adding"""
        request = create_request(
            "add_document",
            content="Cached content"
        )
        
        result = await kb_server.handle_request(request)
        doc_id = result["document_id"]
        
        # Check cache
        assert doc_id in kb_server.cache
        assert kb_server.cache[doc_id]["content"] == "Cached content"
    
    @pytest.mark.asyncio
    async def test_cache_hit_on_get(self, kb_server):
        """Test cache hit when retrieving document"""
        # Pre-populate cache
        kb_server.cache["cached_doc"] = {
            "content": "Cached content",
            "metadata": {"cached": True}
        }
        
        request = create_request("get_document", document_id="cached_doc")
        result = await kb_server.handle_request(request)
        
        assert result["cached"] is True
        assert result["content"] == "Cached content"
    
    @pytest.mark.asyncio
    async def test_cache_invalidated_on_update(self, kb_server):
        """Test cache is cleared when document is updated"""
        # Pre-populate cache
        kb_server.cache["doc_1"] = {"content": "Old", "metadata": {}}
        
        request = create_request(
            "update_document",
            document_id="doc_1",
            content="New content"
        )
        
        await kb_server.handle_request(request)
        
        assert "doc_1" not in kb_server.cache


# ============ Error Handling Tests ============

class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.mark.asyncio
    async def test_invalid_action(self, kb_server):
        """Test handling of invalid action"""
        request = create_request("invalid_action")
        
        with pytest.raises(MCPValidationError) as exc:
            await kb_server.handle_request(request)
        
        assert "invalid action" in str(exc.value).lower()
    
    @pytest.mark.asyncio
    async def test_missing_action(self, kb_server):
        """Test handling of missing action - empty body triggers body validation first"""
        request = MCPMessage(
            header=MCPMessageHeader(message_type=MessageType.REQUEST, source="test"),
            body={}
        )
        
        with pytest.raises(MCPValidationError) as exc:
            await kb_server.handle_request(request)
        
        # Empty body {} triggers "action is required" validation
        assert "action" in str(exc.value).lower() or "required" in str(exc.value).lower()
    
    @pytest.mark.asyncio
    async def test_empty_body(self, kb_server):
        """Test handling of empty request body - triggers action validation"""
        request = MCPMessage(
            header=MCPMessageHeader(message_type=MessageType.REQUEST, source="test"),
            body={}
        )
        
        with pytest.raises(MCPValidationError) as exc:
            await kb_server.handle_request(request)
        
        # Empty body {} can trigger either "action" or "body" validation
        error_msg = str(exc.value).lower()
        assert "action" in error_msg or "body" in error_msg or "required" in error_msg


# ============ Stats and Health Tests ============

class TestStatsAndHealth:
    """Test statistics and health check operations"""
    
    @pytest.mark.asyncio
    async def test_get_stats(self, kb_server):
        """Test getting KB statistics"""
        request = create_request("get_stats")
        
        result = await kb_server.handle_request(request)
        
        assert result["success"] is True
        assert "stats" in result
        assert "cache_size" in result["stats"]
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, kb_server):
        """Test health check returns healthy status"""
        request = create_request("health_check")
        
        result = await kb_server.handle_request(request)
        
        assert result["status"] == "healthy"
        assert "components" in result
        assert "timestamp" in result
