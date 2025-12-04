"""
Unit tests for the Chat Agent.
"""

import pytest
from unittest import mock
from unittest.mock import MagicMock

from variants.mini.agents.chat_agent import ChatAgent
from variants.mini.agents.faq_agent import FAQAgent


@pytest.fixture
def mock_faq_agent():
    return MagicMock(spec=FAQAgent)


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def chat_agent(mock_faq_agent, mock_logger):
    return ChatAgent(faq_agent=mock_faq_agent, logger=mock_logger)


def test_initialization(mock_faq_agent, mock_logger):
    """Test successful agent initialization."""
    agent = ChatAgent(faq_agent=mock_faq_agent, logger=mock_logger)
    assert agent.faq_agent == mock_faq_agent
    assert agent.logger == mock_logger
    assert isinstance(agent.active_sessions, dict)
    mock_logger.info.assert_called()


def test_handle_new_answered_message(chat_agent, mock_faq_agent, mock_logger):
    """Test handling a new message that is successfully answered."""
    message = "How do I reset my password?"
    customer_id = "cust123"
    session_id = "sess456"
    
    # Mock FAQ agent response
    mock_faq_agent.process_question.return_value = {
        "status": "answered",
        "response": "You can reset your password by clicking 'Forgot Password'.",
        "escalated": False
    }
    
    result = chat_agent.handle_message(message, customer_id, session_id)
    
    assert result["status"] == "answered"
    assert result["requires_human_agent"] is False
    assert "password" in result["response"].lower()
    
    mock_faq_agent.process_question.assert_called_once()
    assert session_id in chat_agent.active_sessions


def test_handle_new_escalated_message(chat_agent, mock_faq_agent, mock_logger):
    """Test handling a new message that requires escalation."""
    message = "I have a complex integration issue"
    customer_id = "cust123"
    session_id = "sess457"
    
    # Mock FAQ agent escalation
    mock_faq_agent.process_question.return_value = {
        "status": "escalated",
        "response": "I've created a support ticket for you.",
        "escalated": True
    }
    
    result = chat_agent.handle_message(message, customer_id, session_id)
    
    assert result["status"] == "escalated"
    assert result["requires_human_agent"] is True
    assert "human agent" in result["response"].lower()


def test_handle_follow_up_message(chat_agent, mock_faq_agent, mock_logger):
    """Test handling a follow-up message."""
    # First, establish a session
    first_message = "How do I reset my password?"
    customer_id = "cust123"
    session_id = "sess458"
    
    mock_faq_agent.process_question.return_value = {
        "status": "answered",
        "response": "You can reset your password...",
        "escalated": False
    }
    
    chat_agent.handle_message(first_message, customer_id, session_id)
    
    # Now send a follow-up
    follow_up = "thanks"
    result = chat_agent.handle_message(follow_up, customer_id, session_id)
    
    assert result["status"] == "answered"
    assert result["requires_human_agent"] is False
    assert "welcome" in result["response"].lower() or "else" in result["response"].lower()


def test_handle_message_exception(chat_agent, mock_faq_agent, mock_logger):
    """Test error handling when processing message."""
    message = "Test message"
    customer_id = "cust123"
    session_id = "sess459"
    
    # Mock an exception in FAQ agent
    mock_faq_agent.process_question.side_effect = Exception("Test error")
    
    result = chat_agent.handle_message(message, customer_id, session_id)
    
    assert result["status"] == "error"
    assert result["requires_human_agent"] is True
    assert "human agent" in result["response"].lower()
    
    mock_logger.error.assert_called()
