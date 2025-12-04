"""
Integration tests for the Email Agent.
"""

import pytest
import os
import tempfile
from unittest import mock

from variants.mini.agents.email_agent import EmailAgent
from variants.mini.agents.faq_agent import FAQAgent
from shared.integrations.email_client import EmailClient
from shared.knowledge_base.kb_manager import KnowledgeBaseManager
from shared.knowledge_base.vector_store import VectorStore
from shared.knowledge_base.rag_pipeline import RAGPipeline
from shared.core_functions.config import Config


@pytest.fixture
def integration_environment():
    """
    Setup real integration environment with in-memory KB.
    """
    temp_dir = tempfile.mkdtemp()
    
    env_vars = {
        "DATABASE_URL": "sqlite:///:memory:",
        "VECTOR_DB_PATH": temp_dir,
        "VECTOR_DB_TYPE": "chromadb",
        "COLLECTION_NAME": "test_email_agent_kb"
    }
    
    with mock.patch.dict(os.environ, env_vars):
        config = Config()
        
        # Setup real KB with test data
        vector_store = VectorStore(config=config)
        rag_pipeline = RAGPipeline(config=config, vector_store=vector_store)
        kb_manager = KnowledgeBaseManager(config=config, vector_store=vector_store, rag_pipeline=rag_pipeline)
        
        # Add test FAQs
        docs = [
            {
                "content": "To reset your password, click on 'Forgot Password' on the login page and follow the instructions sent to your email.",
                "metadata": {"source": "password_reset_faq.txt"}
            }
        ]
        kb_manager.ingest_documents(docs)
        
        # Create real FAQ agent
        faq_agent = FAQAgent(kb_manager=kb_manager)
        # Lower threshold for test
        faq_agent.confidence_threshold = 0.0
        
        # Mock email client (we don't want to send real emails)
        email_client = mock.MagicMock(spec=EmailClient)
        
        # Create email agent
        email_agent = EmailAgent(faq_agent=faq_agent, email_client=email_client)
        
        yield email_agent
        
        # Cleanup
        try:
            vector_store.delete_collection()
        except:
            pass
    
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_integration_faq_email_routing(integration_environment):
    """
    Test that FAQ emails are correctly routed to FAQAgent and answered.
    """
    email_agent = integration_environment
    
    raw_email = {
        "subject": "Password Reset Question",
        "body": "How do I reset my password?",
        "sender": "test@example.com",
        "message_id": "int_test_1"
    }
    
    result = email_agent.process_email(raw_email)
    
    assert result["status"] == "answered"
    assert result["intent"] == "faq"
    assert "password" in result["response"].lower() or "forgot" in result["response"].lower()


def test_integration_order_status_routing(integration_environment):
    """
    Test that order status emails are handled correctly.
    """
    email_agent = integration_environment
    
    raw_email = {
        "subject": "Order Status Inquiry",
        "body": "I need to check the status of my order #54321. When will it arrive?",
        "sender": "test@example.com",
        "message_id": "int_test_2"
    }
    
    result = email_agent.process_email(raw_email)
    
    assert result["status"] == "answered"
    assert result["intent"] == "order_status"
    assert "54321" in result["response"]
    assert "transit" in result["response"].lower() or "track" in result["response"].lower()
