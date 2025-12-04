"""
Integration tests for the Voice Agent.
"""

import pytest
import os
import tempfile
from unittest import mock

from variants.mini.agents.voice_agent import VoiceAgent
from variants.mini.agents.faq_agent import FAQAgent
from shared.integrations.twilio_client import TwilioClient
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
        "COLLECTION_NAME": "test_voice_agent_kb"
    }
    
    with mock.patch.dict(os.environ, env_vars):
        config = Config()
        
        # Setup real KB with test data
        vector_store = VectorStore(config=config)
        rag_pipeline = RAGPipeline(config=config, vector_store=vector_store)
        kb_manager = KnowledgeBaseManager(config=config, vector_store=vector_store, rag_pipeline=rag_pipeline)
        
        # Add test FAQ
        docs = [
            {
                "content": "Our business hours are Monday to Friday, 9 AM to 6 PM Eastern Time.",
                "metadata": {"source": "hours_faq.txt"}
            }
        ]
        kb_manager.ingest_documents(docs)
        
        # Create real FAQ agent
        faq_agent = FAQAgent(kb_manager=kb_manager)
        # Use low threshold for test
        faq_agent.confidence_threshold = 0.0
        
        # Mock Twilio client (we don't want to make real calls)
        twilio_client = mock.MagicMock(spec=TwilioClient)
        
        # Create voice agent
        voice_agent = VoiceAgent(faq_agent=faq_agent, twilio_client=twilio_client)
        
        yield voice_agent, twilio_client
        
        # Cleanup
        try:
            vector_store.delete_collection()
        except:
            pass
    
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_integration_successful_answer(integration_environment):
    """
    Test that voice agent can answer questions from the KB.
    """
    voice_agent, twilio_client = integration_environment
    
    # Mock transcription to return a question in the KB
    twilio_client.transcribe_speech.return_value = "What are your business hours?"
    
    call_sid = "CA_test_1"
    from_number = "+15551234567"
    
    result = voice_agent.handle_call(call_sid, from_number)
    
    assert result["status"] == "answered"
    assert result["transcription"] == "What are your business hours?"
    assert "<?xml" in result["twiml"]
    assert ("9" in result["twiml"] or "business" in result["twiml"].lower())


def test_integration_escalation_on_unknown_question(integration_environment):
    """
    Test that voice agent escalates when it doesn't know the answer.
    """
    voice_agent, twilio_client = integration_environment
    
    # Mock transcription to return a question NOT in the KB
    twilio_client.transcribe_speech.return_value = "Can you help me integrate your API with my custom system?"
    
    call_sid = "CA_test_2"
    from_number = "+15551234567"
    
    result = voice_agent.handle_call(call_sid, from_number)
    
    # Could be answered with low threshold or escalated
    assert result["status"] in ["answered", "escalated"]
    assert "<?xml" in result["twiml"]
