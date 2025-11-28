import pytest
from unittest.mock import MagicMock
from shared.knowledge_base.kb_manager import KnowledgeBaseManager, KnowledgeBaseError
from shared.core_functions.config import Config

@pytest.fixture
def mock_config():
    config = MagicMock(spec=Config)
    config.env = {}
    return config

@pytest.fixture
def mock_vector_store():
    vector_store = MagicMock()
    vector_store.get_collection_info.return_value = {
        "name": "test_collection",
        "document_count": 5
    }
    return vector_store

@pytest.fixture
def mock_rag_pipeline():
    pipeline = MagicMock()
    pipeline.get_pipeline_stats.return_value = {
        "top_k": 5,
        "similarity_threshold": 0.7
    }
    return pipeline

@pytest.fixture
def kb_manager(mock_config, mock_vector_store, mock_rag_pipeline):
    return KnowledgeBaseManager(
        config=mock_config,
        vector_store=mock_vector_store,
        rag_pipeline=mock_rag_pipeline
    )

def test_initialization(mock_config, mock_vector_store, mock_rag_pipeline):
    """Test that KnowledgeBaseManager initializes correctly."""
    manager = KnowledgeBaseManager(
        config=mock_config,
        vector_store=mock_vector_store,
        rag_pipeline=mock_rag_pipeline
    )
    
    assert manager.config == mock_config
    assert manager.vector_store == mock_vector_store
    assert manager.rag_pipeline == mock_rag_pipeline
    assert manager.stats["total_documents"] == 0

def test_validate_document_valid(kb_manager):
    """Test document validation with valid document."""
    doc = {
        "content": "Test content",
        "metadata": {"source": "test.txt"}
    }
    
    assert kb_manager.validate_document(doc) is True

def test_validate_document_missing_content(kb_manager):
    """Test validation fails for missing content."""
    doc = {"metadata": {"source": "test.txt"}}
    assert kb_manager.validate_document(doc) is False

def test_validate_document_empty_content(kb_manager):
    """Test validation fails for empty content."""
    doc = {"content": "   ", "metadata": {}}
    assert kb_manager.validate_document(doc) is False

def test_validate_document_invalid_metadata(kb_manager):
    """Test validation fails for invalid metadata type."""
    doc = {"content": "Test", "metadata": "invalid"}
    assert kb_manager.validate_document(doc) is False

def test_ingest_documents_success(kb_manager, mock_vector_store):
    """Test successful document ingestion."""
    documents = [
        {"content": "Doc 1", "metadata": {"source": "file1.txt"}},
        {"content": "Doc 2", "metadata": {"source": "file2.txt"}}
    ]
    
    mock_vector_store.add_documents.return_value = ["id1", "id2"]
    
    result = kb_manager.ingest_documents(documents)
    
    assert result["success"] is True
    assert result["total"] == 2
    assert result["successful"] == 2
    assert result["failed"] == 0
    assert len(result["document_ids"]) == 2
    assert kb_manager.stats["total_documents"] == 2

def test_ingest_documents_with_validation(kb_manager, mock_vector_store):
    """Test ingestion with validation filtering invalid documents."""
    documents = [
        {"content": "Valid doc", "metadata": {}},
        {"content": "", "metadata": {}},  # Invalid - empty
        {"metadata": {}}  # Invalid - no content
    ]
    
    mock_vector_store.add_documents.return_value = ["id1"]
    
    result = kb_manager.ingest_documents(documents, validate=True)
    
    assert result["successful"] == 1
    assert result["failed"] == 2

def test_ingest_documents_empty_list(kb_manager):
    """Test ingestion with empty document list."""
    result = kb_manager.ingest_documents([])
    
    assert result["success"] is True
    assert result["total"] == 0
    assert result["successful"] == 0

def test_update_document(kb_manager, mock_vector_store):
    """Test document update."""
    mock_vector_store.add_documents.return_value = ["new_id"]
    
    success = kb_manager.update_document(
        doc_id="old_id",
        new_content="Updated content",
        metadata={"version": 2}
    )
    
    assert success is True
    mock_vector_store.add_documents.assert_called_once()
    
    # Check that metadata includes previous_id
    call_args = mock_vector_store.add_documents.call_args[0][0]
    assert call_args[0]["metadata"]["previous_id"] == "old_id"

def test_search(kb_manager, mock_rag_pipeline):
    """Test knowledge base search."""
    mock_rag_pipeline.query.return_value = {
        "query": "test query",
        "prompt": "Generated prompt",
        "context": [{"content": "Result"}],
        "context_count": 1
    }
    
    result = kb_manager.search("test query", top_k=3)
    
    assert result["query"] == "test query"
    assert result["context_count"] == 1
    assert kb_manager.stats["total_queries"] == 1
    mock_rag_pipeline.query.assert_called_once_with(
        user_query="test query",
        top_k=3,
        system_instruction=None
    )

def test_search_with_system_instruction(kb_manager, mock_rag_pipeline):
    """Test search with system instruction."""
    mock_rag_pipeline.query.return_value = {
        "query": "test",
        "prompt": "prompt",
        "context": [],
        "context_count": 0
    }
    
    kb_manager.search("test", system_instruction="Be helpful")
    
    mock_rag_pipeline.query.assert_called_with(
        user_query="test",
        top_k=5,
        system_instruction="Be helpful"
    )

def test_get_stats(kb_manager, mock_vector_store, mock_rag_pipeline):
    """Test getting knowledge base statistics."""
    stats = kb_manager.get_stats()
    
    assert "total_documents" in stats
    assert "total_queries" in stats
    assert "vector_store" in stats
    assert "rag_pipeline" in stats
    assert stats["vector_store"]["document_count"] == 5

def test_health_check_healthy(kb_manager, mock_vector_store, mock_rag_pipeline):
    """Test health check when system is healthy."""
    health = kb_manager.health_check()
    
    assert health["status"] == "healthy"
    assert health["checks"]["vector_store"] is True
    assert health["checks"]["rag_pipeline"] is True
    assert health["checks"]["document_count"] == 5

def test_health_check_unhealthy(kb_manager, mock_vector_store):
    """Test health check when system has issues."""
    mock_vector_store.get_collection_info.side_effect = Exception("DB error")
    
    health = kb_manager.health_check()
    
    assert health["status"] == "unhealthy"
    assert "error" in health
