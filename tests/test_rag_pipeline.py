import pytest
from unittest.mock import MagicMock, patch
from shared.knowledge_base.rag_pipeline import RAGPipeline, RAGPipelineError
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
        "document_count": 10
    }
    return vector_store

@pytest.fixture
def rag_pipeline(mock_config, mock_vector_store):
    return RAGPipeline(
        config=mock_config,
        vector_store=mock_vector_store,
        top_k=5,
        similarity_threshold=0.7
    )

def test_initialization(mock_config, mock_vector_store):
    """Test that RAGPipeline initializes correctly."""
    pipeline = RAGPipeline(
        config=mock_config,
        vector_store=mock_vector_store,
        top_k=3,
        similarity_threshold=0.5
    )
    
    assert pipeline.top_k == 3
    assert pipeline.similarity_threshold == 0.5
    assert pipeline.vector_store == mock_vector_store

def test_retrieve_context(rag_pipeline, mock_vector_store):
    """Test context retrieval from vector store."""
    # Mock vector store response
    mock_vector_store.similarity_search.return_value = [
        {
            "content": "Document 1 content",
            "metadata": {"source": "doc1.txt"},
            "distance": 0.2,
            "id": "id1"
        },
        {
            "content": "Document 2 content",
            "metadata": {"source": "doc2.txt"},
            "distance": 0.3,
            "id": "id2"
        }
    ]
    
    results = rag_pipeline.retrieve_context("test query", top_k=2)
    
    assert len(results) == 2
    assert results[0]["content"] == "Document 1 content"
    assert "similarity_score" in results[0]
    mock_vector_store.similarity_search.assert_called_once_with("test query", n_results=2)

def test_retrieve_context_empty_query(rag_pipeline):
    """Test that empty query returns empty results."""
    results = rag_pipeline.retrieve_context("")
    assert results == []
    
    results = rag_pipeline.retrieve_context("   ")
    assert results == []

def test_retrieve_context_with_threshold_filtering(rag_pipeline, mock_vector_store):
    """Test that similarity threshold filters results."""
    # Mock results with varying distances
    mock_vector_store.similarity_search.return_value = [
        {"content": "Good match", "distance": 0.1, "metadata": {}},  # similarity = 0.9
        {"content": "Poor match", "distance": 0.5, "metadata": {}},  # similarity = 0.5
    ]
    
    # With threshold of 0.7, only first result should pass
    results = rag_pipeline.retrieve_context("test", filter_threshold=True)
    
    assert len(results) == 1
    assert results[0]["content"] == "Good match"

def test_generate_prompt(rag_pipeline):
    """Test prompt generation with context."""
    context = [
        {
            "content": "The sky is blue.",
            "metadata": {"source": "science.txt"},
            "similarity_score": 0.95
        },
        {
            "content": "Water is wet.",
            "metadata": {"source": "facts.txt"},
            "similarity_score": 0.85
        }
    ]
    
    prompt = rag_pipeline.generate_prompt("What color is the sky?", context)
    
    assert "What color is the sky?" in prompt
    assert "The sky is blue." in prompt
    assert "Water is wet." in prompt
    assert "science.txt" in prompt
    assert "95.00%" in prompt

def test_generate_prompt_no_context(rag_pipeline):
    """Test prompt generation with no context."""
    prompt = rag_pipeline.generate_prompt("test query", [])
    
    assert "test query" in prompt
    assert "No relevant context found" in prompt

def test_generate_prompt_with_system_instruction(rag_pipeline):
    """Test prompt generation with system instruction."""
    context = [{"content": "Test content", "metadata": {}}]
    system_instruction = "You are a helpful assistant."
    
    prompt = rag_pipeline.generate_prompt(
        "test query",
        context,
        system_instruction=system_instruction
    )
    
    assert system_instruction in prompt
    assert "test query" in prompt

def test_query_end_to_end(rag_pipeline, mock_vector_store):
    """Test complete RAG query flow."""
    mock_vector_store.similarity_search.return_value = [
        {
            "content": "Relevant document",
            "metadata": {"source": "test.txt"},
            "distance": 0.2,
            "id": "id1"
        }
    ]
    
    result = rag_pipeline.query("What is the answer?", top_k=1)
    
    assert "query" in result
    assert "prompt" in result
    assert "context" in result
    assert "context_count" in result
    assert result["query"] == "What is the answer?"
    assert result["context_count"] == 1
    assert "Relevant document" in result["prompt"]

def test_query_with_system_instruction(rag_pipeline, mock_vector_store):
    """Test query with system instruction."""
    mock_vector_store.similarity_search.return_value = [
        {"content": "Test", "metadata": {}, "distance": 0.1, "id": "id1"}
    ]
    
    result = rag_pipeline.query(
        "test query",
        system_instruction="Be concise."
    )
    
    assert "Be concise." in result["prompt"]

def test_error_handling_vector_store_failure(rag_pipeline, mock_vector_store):
    """Test error handling when vector store fails."""
    mock_vector_store.similarity_search.side_effect = Exception("Vector store error")
    
    with pytest.raises(RAGPipelineError, match="Failed to retrieve context"):
        rag_pipeline.retrieve_context("test query")

def test_get_pipeline_stats(rag_pipeline, mock_vector_store):
    """Test getting pipeline statistics."""
    stats = rag_pipeline.get_pipeline_stats()
    
    assert "top_k" in stats
    assert "similarity_threshold" in stats
    assert "vector_store" in stats
    assert stats["top_k"] == 5
    assert stats["similarity_threshold"] == 0.7
