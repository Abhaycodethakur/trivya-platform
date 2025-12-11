"""
Integration Tests for KB Server

Tests end-to-end workflows with real VectorStore and KB Manager.
"""

import pytest
import os
import shutil
import asyncio

# Set env vars before imports
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/test_db"
os.environ["JWT_SECRET_KEY"] = "test-secret-integration"

from mcp_servers.knowledge.kb_server import KBServer
from mcp_servers.base_server import MCPMessage, MCPMessageHeader, MessageType
from shared.core_functions.config import Config, VectorDBConfig


class IntegrationConfig(Config):
    """Test configuration for integration testing"""
    def __init__(self, db_path):
        super().__init__()
        self.env.update({
            "VECTOR_DB_TYPE": "chromadb",
            "VECTOR_DB_PATH": db_path,
            "COLLECTION_NAME": "integration_test_kb"
        })
        self.vector_db_config = VectorDBConfig(
            VECTOR_DB_TYPE="chromadb",
            VECTOR_DB_PATH=db_path,
            COLLECTION_NAME="integration_test_kb"
        )


@pytest.fixture(scope="module")
def vector_db_path():
    """Create and cleanup test database path"""
    path = "./data/kb_integration_test"
    os.makedirs(path, exist_ok=True)
    yield path
    # Cleanup
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
        except PermissionError:
            print(f"Warning: Could not delete {path} due to file locks")


@pytest.fixture(scope="module")
def kb_server_integration(vector_db_path):
    """Create KB Server with real components"""
    config = IntegrationConfig(vector_db_path)
    server = KBServer(config=config)
    
    # Reset collection for clean state
    if server.vector_store:
        try:
            server.vector_store.delete_collection()
        except:
            pass
    
    return server


def create_request(action: str, **kwargs) -> MCPMessage:
    """Helper to create MCP request messages"""
    return MCPMessage(
        header=MCPMessageHeader(
            message_type=MessageType.REQUEST,
            source="integration_test"
        ),
        body={"action": action, **kwargs}
    )


# ============ Document Lifecycle Tests ============

class TestDocumentLifecycle:
    """Test complete document lifecycle: add -> get -> update -> delete"""
    
    @pytest.mark.asyncio
    async def test_full_document_lifecycle(self, kb_server_integration):
        """Test complete document lifecycle"""
        server = kb_server_integration
        
        # 1. Add document (use string for tags, not list - ChromaDB limitation)
        add_request = create_request(
            "add_document",
            content="Integration test document content about Python programming.",
            metadata={"title": "Python Guide", "tags": "python,programming"}
        )
        add_result = await server.handle_request(add_request)
        
        assert add_result["success"] is True
        doc_id = add_result["document_id"]
        assert doc_id is not None
        
        # 2. Get document
        get_request = create_request("get_document", document_id=doc_id)
        get_result = await server.handle_request(get_request)
        
        assert get_result["success"] is True
        assert get_result["content"] == "Integration test document content about Python programming."
        
        # 3. Search for document
        search_request = create_request(
            "search_documents",
            query="Python programming",
            limit=5
        )
        search_result = await server.handle_request(search_request)
        
        assert search_result["success"] is True
        assert len(search_result["results"]) > 0
        
        # 4. Update document
        update_request = create_request(
            "update_document",
            document_id=doc_id,
            content="Updated: Python is a versatile programming language.",
            metadata={"title": "Updated Python Guide"}
        )
        update_result = await server.handle_request(update_request)
        
        assert update_result["success"] is True
        
        # 5. Delete document
        delete_request = create_request("delete_document", document_id=doc_id)
        delete_result = await server.handle_request(delete_request)
        
        assert delete_result["success"] is True


class TestSearchIntegration:
    """Test search functionality with real VectorStore"""
    
    @pytest.mark.asyncio
    async def test_semantic_search(self, kb_server_integration):
        """Test semantic search returns relevant results"""
        server = kb_server_integration
        
        # Add test documents
        docs = [
            {
                "content": "Machine learning is a subset of artificial intelligence.",
                "metadata": {"topic": "AI"}
            },
            {
                "content": "Python is great for data science and ML applications.",
                "metadata": {"topic": "Programming"}
            },
            {
                "content": "Cooking recipes for Italian pasta dishes.",
                "metadata": {"topic": "Cooking"}
            }
        ]
        
        for doc in docs:
            add_request = create_request("add_document", **doc)
            await server.handle_request(add_request)
        
        # Search for AI-related documents
        search_request = create_request(
            "search_documents",
            query="artificial intelligence and machine learning",
            limit=3
        )
        search_result = await server.handle_request(search_request)
        
        assert search_result["success"] is True
        results = search_result["results"]
        assert len(results) > 0
        
        # Check that AI content is in top results
        top_content = results[0].get("snippet", "") + results[0].get("content", "")
        assert "intelligence" in top_content.lower() or "machine" in top_content.lower()


class TestListAndFilter:
    """Test list documents with filtering"""
    
    @pytest.mark.asyncio
    async def test_list_documents_pagination(self, kb_server_integration):
        """Test document listing with pagination"""
        server = kb_server_integration
        
        # List first page
        list_request = create_request("list_documents", limit=5, offset=0)
        list_result = await server.handle_request(list_request)
        
        assert list_result["success"] is True
        assert "documents" in list_result
        assert list_result["limit"] == 5
        assert list_result["offset"] == 0


class TestHealthAndStats:
    """Test health check and statistics"""
    
    @pytest.mark.asyncio
    async def test_health_check_with_components(self, kb_server_integration):
        """Test health check reports component status"""
        server = kb_server_integration
        
        health_request = create_request("health_check")
        health_result = await server.handle_request(health_request)
        
        assert "status" in health_result
        assert "components" in health_result
        # Components should exist, status can vary based on config
        assert "kb_manager" in health_result["components"]
        assert "vector_store" in health_result["components"]
    
    @pytest.mark.asyncio
    async def test_stats_include_cache_info(self, kb_server_integration):
        """Test stats include cache information"""
        server = kb_server_integration
        
        stats_request = create_request("get_stats")
        stats_result = await server.handle_request(stats_request)
        
        assert stats_result["success"] is True
        assert "stats" in stats_result
        assert "cache_size" in stats_result["stats"]
        assert "cache_max_size" in stats_result["stats"]


class TestConcurrentRequests:
    """Test handling of concurrent requests"""
    
    @pytest.mark.asyncio
    async def test_concurrent_add_documents(self, kb_server_integration):
        """Test adding multiple documents concurrently"""
        server = kb_server_integration
        
        # Create multiple add requests
        requests = [
            create_request(
                "add_document",
                content=f"Concurrent document {i} about topic {i}",
                metadata={"index": i}
            )
            for i in range(5)
        ]
        
        # Execute concurrently
        tasks = [server.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert len(results) == 5
        assert all(r["success"] for r in results)
        assert len(set(r["document_id"] for r in results)) == 5  # All unique IDs
    
    @pytest.mark.asyncio
    async def test_concurrent_search_requests(self, kb_server_integration):
        """Test searching concurrently"""
        server = kb_server_integration
        
        queries = ["Python", "Machine learning", "Data science", "AI", "Programming"]
        
        requests = [
            create_request("search_documents", query=q, limit=3)
            for q in queries
        ]
        
        tasks = [server.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        assert all(r["success"] for r in results)
