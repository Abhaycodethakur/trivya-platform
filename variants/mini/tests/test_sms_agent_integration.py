"""
Integration tests for the SMS Agent.
"""

import pytest
import os
import tempfile
from unittest import mock

from variants.mini.agents.sms_agent import SMSAgent
from variants.mini.agents.faq_agent import FAQAgent
from shared.integrations.sms_client import SMSClient
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
        "COLLECTION_NAME": "test_sms_agent_kb"
    }
    
    with mock.patch.dict(os.environ, env_vars):
        config = Config()
        
        # Setup real KB with test data
        vector_store = VectorStore(config=config)
        rag_pipeline = RAGPipeline(config=config, vector_store=vector_store)
        kb_manager = KnowledgeBaseManager(config=config, vector_store=vector_store, rag_pipeline=rag_pipeline)
        
        # Add short FAQ suitable for SMS
        docs = [
            {
                "content": "Our phone number is 1-800-TRIVYA.",
                "metadata": {"source": "contact_faq.txt"}
            }
        ]
        kb_manager.ingest_documents(docs)
        
        # Create real FAQ agent
        faq_agent = FAQAgent(kb_manager=kb_manager)
        # Use low threshold for test
        faq_agent.confidence_threshold = 0.0
        
        # Mock SMS client (we don't want to send real SMS)
        sms_client = mock.MagicMock(spec=SMSClient)
        
        # Create SMS agent
        sms_agent = SMSAgent(faq_agent=faq_agent, sms_client=sms_client)
        
        yield sms_agent
        
        # Cleanup
        try:
            vector_store.delete_collection()
        except:
            pass
    
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_integration_faq_sms_routing(integration_environment):
    """
    Test that FAQ SMS messages are correctly routed and answered.
    """
    sms_agent = integration_environment
    
    sender = "+1234567890"
    message = "What's your number?"
    msg_id = "int_test_1"
    
    result = sms_agent.process_sms(sender, message, msg_id)
    
    assert result["status"] == "answered"
    assert result["intent"] == "faq"
    assert len(result["response"]) <= 160
    assert ("800" in result["response"] or "TRIVYA" in result["response"].upper())


def test_integration_refund_request_routing(integration_environment):
    """
    Test that refund request SMS creates ticket and directs to email.
    """
    sms_agent = integration_environment
    
    sender = "+1234567890"
    message = "I want a refund please"
    msg_id = "int_test_2"
    
    result = sms_agent.process_sms(sender, message, msg_id)
    
    assert result["status"] == "ticket_created"
    assert result["intent"] == "refund_request"
    assert "ticket" in result["response"].lower() or "email" in result["response"].lower()
    assert len(result["response"]) <= 160
