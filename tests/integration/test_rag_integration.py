import pytest
import shutil
import tempfile
import os
from shared.knowledge_base.vector_store import VectorStore
from shared.knowledge_base.rag_pipeline import RAGPipeline
from shared.knowledge_base.kb_manager import KnowledgeBaseManager
from shared.core_functions.config import Config

@pytest.fixture
def temp_vector_db():
    """Create a temporary directory for the vector DB."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_rag_integration_end_to_end(temp_vector_db):
    """Test complete RAG pipeline with real vector store."""
    
    # Ensure DATABASE_URL is set for Config init
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    
    # Setup config to use temp dir
    config = Config()
    config.vector_db_config.VECTOR_DB_PATH = temp_vector_db
    config.vector_db_config.COLLECTION_NAME = "rag_test_collection"
    
    # Initialize components
    vector_store = VectorStore(config)
    rag_pipeline = RAGPipeline(
        config=config,
        vector_store=vector_store,
        top_k=3,
        similarity_threshold=0.0
    )
    kb_manager = KnowledgeBaseManager(
        config=config,
        vector_store=vector_store,
        rag_pipeline=rag_pipeline
    )
    
    # Ingest documents
    documents = [
        {
            "content": "Trivya is an AI-powered customer support platform.",
            "metadata": {"source": "about.txt", "category": "product"}
        },
        {
            "content": "Mini Trivya costs $1,000 per month and handles 2 concurrent calls.",
            "metadata": {"source": "pricing.txt", "category": "pricing"}
        },
        {
            "content": "Trivya High costs $4,000 per month and handles 5 concurrent calls.",
            "metadata": {"source": "pricing.txt", "category": "pricing"}
        },
        {
            "content": "The platform uses RAG (Retrieval-Augmented Generation) for accurate responses.",
            "metadata": {"source": "tech.txt", "category": "technology"}
        }
    ]
    
    ingestion_result = kb_manager.ingest_documents(documents)
    assert ingestion_result["successful"] == 4
    assert ingestion_result["failed"] == 0
    
    # Test RAG query
    query_result = kb_manager.search("What is Trivya?", top_k=2)
    
    assert "query" in query_result
    assert "prompt" in query_result
    assert "context" in query_result
    assert query_result["context_count"] > 0
    
    # Verify context contains relevant information
    context_text = " ".join([doc["content"] for doc in query_result["context"]])
    assert "Trivya" in context_text or "AI" in context_text
    
    # Test pricing query
    pricing_query = kb_manager.search("How much does Mini Trivya cost?", top_k=2)
    pricing_context = " ".join([doc["content"] for doc in pricing_query["context"]])
    assert "$1,000" in pricing_context or "Mini Trivya" in pricing_context
    
    # Test statistics
    stats = kb_manager.get_stats()
    assert stats["total_documents"] == 4
    assert stats["total_queries"] == 2
    assert stats["vector_store"]["document_count"] == 4
    
    # Test health check
    health = kb_manager.health_check()
    assert health["status"] == "healthy"
    assert health["checks"]["vector_store"] is True
    assert health["checks"]["rag_pipeline"] is True
    assert health["checks"]["document_count"] == 4
    
    # Cleanup
    vector_store.delete_collection()

def test_rag_context_retrieval_quality(temp_vector_db):
    """Test that RAG retrieves high-quality, relevant context."""
    
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    
    config = Config()
    config.vector_db_config.VECTOR_DB_PATH = temp_vector_db
    config.vector_db_config.COLLECTION_NAME = "quality_test"
    
    vector_store = VectorStore(config)
    rag_pipeline = RAGPipeline(
        config=config,
        vector_store=vector_store,
        similarity_threshold=0.5  # Higher threshold for quality
    )
    
    # Add documents with varying relevance
    docs = [
        {"content": "Python is a programming language.", "metadata": {"topic": "programming"}},
        {"content": "The sky is blue during the day.", "metadata": {"topic": "nature"}},
        {"content": "Python code is easy to read and write.", "metadata": {"topic": "programming"}},
    ]
    
    vector_store.add_documents(docs)
    
    # Query about Python
    context = rag_pipeline.retrieve_context("Tell me about Python programming", top_k=3)
    
    # Should retrieve programming-related documents
    assert len(context) > 0
    programming_docs = [doc for doc in context if "Python" in doc["content"]]
    assert len(programming_docs) > 0
    
    # Cleanup
    vector_store.delete_collection()

def test_kb_manager_document_update(temp_vector_db):
    """Test document update functionality."""
    
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    
    config = Config()
    config.vector_db_config.VECTOR_DB_PATH = temp_vector_db
    config.vector_db_config.COLLECTION_NAME = "update_test"
    
    vector_store = VectorStore(config)
    rag_pipeline = RAGPipeline(config=config, vector_store=vector_store)
    kb_manager = KnowledgeBaseManager(
        config=config,
        vector_store=vector_store,
        rag_pipeline=rag_pipeline
    )
    
    # Add initial document
    docs = [{"content": "Initial version of document", "metadata": {"version": 1}}]
    result = kb_manager.ingest_documents(docs)
    original_id = result["document_ids"][0]
    
    # Update document
    success = kb_manager.update_document(
        doc_id=original_id,
        new_content="Updated version of document",
        metadata={"version": 2}
    )
    
    assert success is True
    
    # Verify update
    stats = kb_manager.get_stats()
    assert stats["total_documents"] == 2  # Original + updated version
    
    # Cleanup
    vector_store.delete_collection()
