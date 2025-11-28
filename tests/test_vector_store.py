import pytest
from unittest.mock import MagicMock, patch
from shared.knowledge_base.vector_store import VectorStore
from shared.core_functions.config import Config

@pytest.fixture
def mock_config():
    config = MagicMock(spec=Config)
    config.vector_db_config = MagicMock()
    config.vector_db_config.VECTOR_DB_TYPE = "chromadb"
    config.vector_db_config.VECTOR_DB_PATH = "./test_db"
    config.vector_db_config.COLLECTION_NAME = "test_collection"
    config.env = {} # Mock env dictionary
    return config

@patch("shared.knowledge_base.vector_store.chromadb.PersistentClient")
def test_initialization(mock_client, mock_config):
    """Test that VectorStore initializes correctly."""
    mock_collection = MagicMock()
    mock_client.return_value.get_or_create_collection.return_value = mock_collection
    
    vs = VectorStore(mock_config)
    
    mock_client.assert_called_with(path="./test_db")
    mock_client.return_value.get_or_create_collection.assert_called_with(name="test_collection")
    assert vs.collection == mock_collection

@patch("shared.knowledge_base.vector_store.chromadb.PersistentClient")
def test_initialization_invalid_type(mock_client, mock_config):
    """Test that VectorStore raises error for invalid DB type."""
    mock_config.vector_db_config.VECTOR_DB_TYPE = "invalid_type"
    
    with pytest.raises(ValueError, match="Unsupported VECTOR_DB_TYPE"):
        VectorStore(mock_config)

@patch("shared.knowledge_base.vector_store.chromadb.PersistentClient")
def test_add_documents(mock_client, mock_config):
    """Test adding documents."""
    mock_collection = MagicMock()
    mock_client.return_value.get_or_create_collection.return_value = mock_collection
    
    vs = VectorStore(mock_config)
    
    documents = [
        {"content": "doc1", "metadata": {"source": "test"}},
        {"content": "doc2", "metadata": {"source": "test"}}
    ]
    
    ids = vs.add_documents(documents)
    
    assert len(ids) == 2
    mock_collection.add.assert_called_once()
    call_args = mock_collection.add.call_args[1]
    assert call_args['documents'] == ["doc1", "doc2"]
    assert call_args['metadatas'] == [{"source": "test"}, {"source": "test"}]

@patch("shared.knowledge_base.vector_store.chromadb.PersistentClient")
def test_similarity_search(mock_client, mock_config):
    """Test similarity search."""
    mock_collection = MagicMock()
    mock_client.return_value.get_or_create_collection.return_value = mock_collection
    
    # Mock return value of query
    mock_collection.query.return_value = {
        'ids': [['id1', 'id2']],
        'documents': [['doc1', 'doc2']],
        'metadatas': [[{'source': 'test1'}, {'source': 'test2'}]]
    }
    
    vs = VectorStore(mock_config)
    
    results = vs.similarity_search("query", n_results=2)
    
    assert len(results) == 2
    assert results[0]['content'] == 'doc1'
    assert results[0]['metadata'] == {'source': 'test1'}
    mock_collection.query.assert_called_with(query_texts=["query"], n_results=2)

@patch("shared.knowledge_base.vector_store.chromadb.PersistentClient")
def test_error_handling(mock_client, mock_config):
    """Test error handling in add_documents."""
    mock_collection = MagicMock()
    mock_collection.add.side_effect = Exception("ChromaDB Error")
    mock_client.return_value.get_or_create_collection.return_value = mock_collection
    
    vs = VectorStore(mock_config)
    
    with pytest.raises(Exception, match="ChromaDB Error"):
        vs.add_documents([{"content": "test", "metadata": {}}])
