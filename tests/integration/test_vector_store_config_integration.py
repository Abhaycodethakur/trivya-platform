import pytest
from shared.knowledge_base.vector_store import VectorStore
from shared.core_functions.config import Config

def test_vector_store_config_integration():
    """Test that VectorStore correctly reads from the Config object."""
    
    import os
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    
    config = Config()
    # Ensure we are using defaults or set values
    expected_type = config.vector_db_config.VECTOR_DB_TYPE
    expected_path = config.vector_db_config.VECTOR_DB_PATH
    expected_collection = config.vector_db_config.COLLECTION_NAME
    
    # We don't want to actually create the DB in the default location during this test if possible,
    # but we want to verify it READS the config.
    # So we can just check the attributes after init, assuming init doesn't fail.
    # To be safe, we can mock the client creation part if we want to avoid side effects,
    # but this is an integration test, so maybe we let it run?
    # Actually, let's just check if the attributes match.
    
    # To avoid creating a real DB at the default path, we can temporarily override the path in the config object
    # passed to the constructor, but we want to test that it reads *whatever* is in the config.
    
    vs = VectorStore(config)
    
    assert vs.db_type == expected_type
    assert vs.db_path == expected_path
    assert vs.collection_name == expected_collection
