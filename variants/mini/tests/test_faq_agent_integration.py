"""
Integration tests for the FAQ Agent.
"""

import pytest
import os
import shutil
import tempfile
from unittest import mock

from variants.mini.agents.faq_agent import FAQAgent
from shared.knowledge_base.kb_manager import KnowledgeBaseManager
from shared.knowledge_base.vector_store import VectorStore
from shared.knowledge_base.rag_pipeline import RAGPipeline
from shared.core_functions.config import Config


@pytest.fixture
def integration_environment():
    """
    Setup a real integration environment with in-memory vector store.
    """
    # Create a temporary directory for vector store
    temp_dir = tempfile.mkdtemp()
    
    # Setup environment variables required by Config
    env_vars = {
        "DATABASE_URL": "sqlite:///:memory:",  # Dummy URL to satisfy validation
        "VECTOR_DB_PATH": temp_dir,
        "VECTOR_DB_TYPE": "chromadb",
        "COLLECTION_NAME": "test_integration_kb"
    }
    
    with mock.patch.dict(os.environ, env_vars):
        # Instantiate Config inside the patch context so it picks up the env vars
        config = Config()
        
        # Initialize real dependencies
        # VectorStore will use the temp_dir from config
        vector_store = VectorStore(config=config)
        
        rag_pipeline = RAGPipeline(config=config, vector_store=vector_store)
        kb_manager = KnowledgeBaseManager(config=config, vector_store=vector_store, rag_pipeline=rag_pipeline)
        
        # Add a known document
        doc = {
            "content": "The company's refund policy allows for returns within 30 days of purchase.",
            "metadata": {"source": "policy_test.txt"}
        }
        kb_manager.ingest_documents([doc])
        
        agent = FAQAgent(kb_manager=kb_manager)
        
        yield agent
        
        # Cleanup
        # Delete the collection to release resources if possible
        try:
            vector_store.delete_collection()
        except:
            pass
            
    # Remove temp directory
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_integration_successful_answer(integration_environment):
    """
    Test that the agent can answer a question present in the KB.
    """
    agent = integration_environment
    # Lower threshold to ensure we accept the match with default embedding model
    agent.confidence_threshold = 0.0
    
    question = "What is the refund policy?"
    customer_id = "test_user"
    channel = "integration_test"
    
    result = agent.process_question(question, customer_id, channel)
    
    assert result["status"] == "answered"
    assert "30 days" in result["response"]
    assert result["escalated"] is False


def test_integration_escalation_on_unknown_question(integration_environment):
    """
    Test that the agent escalates a question not in the KB.
    """
    agent = integration_environment
    question = "Who is the CEO?"
    customer_id = "test_user"
    channel = "integration_test"
    
    result = agent.process_question(question, customer_id, channel)
    
    assert result["status"] == "escalated"
    assert "ticket" in result["response"]
    assert result["escalated"] is True
