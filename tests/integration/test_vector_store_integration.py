import pytest
import shutil
import tempfile
import os
from shared.knowledge_base.vector_store import VectorStore
from shared.core_functions.config import Config

@pytest.fixture
def temp_vector_db():
    """Create a temporary directory for the vector DB."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_vector_store_end_to_end(temp_vector_db):
    """Test the full flow of VectorStore with a real (temporary) ChromaDB."""
    
    # Ensure DATABASE_URL is set for Config init
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    
    # Setup config to use temp dir
    config = Config()
    config.vector_db_config.VECTOR_DB_PATH = temp_vector_db
    config.vector_db_config.COLLECTION_NAME = "integration_test_collection"
    
    # Initialize
    vs = VectorStore(config)
    
    # Add documents
    docs = [
        {"content": "The sky is blue.", "metadata": {"topic": "nature"}},
        {"content": "The sun is bright.", "metadata": {"topic": "nature"}},
        {"content": "Python is a programming language.", "metadata": {"topic": "tech"}}
    ]
    ids = vs.add_documents(docs)
    assert len(ids) == 3
    
    # Search
    results = vs.similarity_search("sky", n_results=1)
    assert len(results) == 1
    assert "blue" in results[0]['content']
    assert results[0]['metadata']['topic'] == "nature"
    
    # Search for tech
    results = vs.similarity_search("programming", n_results=1)
    assert len(results) == 1
    assert "Python" in results[0]['content']
    
    # Cleanup (delete collection)
    vs.delete_collection()
