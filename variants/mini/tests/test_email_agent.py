"""
Unit tests for the Email Agent.
"""

import pytest
from unittest import mock
from unittest.mock import MagicMock

from variants.mini.agents.email_agent import EmailAgent
from variants.mini.agents.faq_agent import FAQAgent
from shared.integrations.email_client import EmailClient


@pytest.fixture
def mock_faq_agent():
    return MagicMock(spec=FAQAgent)


@pytest.fixture
def mock_email_client():
    return MagicMock(spec=EmailClient)


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def email_agent(mock_faq_agent, mock_email_client, mock_logger):
    return EmailAgent(
        faq_agent=mock_faq_agent,
        email_client=mock_email_client,
        logger=mock_logger
    )


def test_initialization(mock_faq_agent, mock_email_client, mock_logger):
    """Test successful agent initialization."""
    agent = EmailAgent(
        faq_agent=mock_faq_agent,
        email_client=mock_email_client,
        logger=mock_logger
    )
    assert agent.faq_agent == mock_faq_agent
    assert agent.email_client == mock_email_client
    assert agent.logger == mock_logger
    mock_logger.info.assert_called()


def test_process_faq_email(email_agent, mock_faq_agent, mock_logger):
    """Test processing an email with FAQ intent."""
    raw_email = {
        "subject": "How do I reset my password?",
        "body": "I forgot my password and need help resetting it.",
        "sender": "customer@example.com",
        "message_id": "msg123"
    }
    
    # Mock FAQ agent response
    mock_faq_agent.process_question.return_value = {
        "status": "answered",
        "response": "You can reset your password by clicking 'Forgot Password' on the login page.",
        "escalated": False
    }
    
    result = email_agent.process_email(raw_email)
    
    assert result["status"] == "answered"
    assert result["intent"] == "faq"
    assert "password" in result["response"].lower()
    
    mock_faq_agent.process_question.assert_called_once()
    mock_logger.info.assert_called()


def test_process_order_status_email(email_agent, mock_logger):
    """Test processing an email with order status intent."""
    raw_email = {
        "subject": "Where is my order?",
        "body": "I ordered something last week (order #12345) and haven't received it yet.",
        "sender": "customer@example.com",
        "message_id": "msg124"
    }
    
    result = email_agent.process_email(raw_email)
    
    assert result["status"] == "answered"
    assert result["intent"] == "order_status"
    assert "12345" in result["response"]
    assert "transit" in result["response"].lower()


def test_process_refund_request_email(email_agent, mock_logger):
    """Test processing an email with refund request intent."""
    raw_email = {
        "subject": "I want a refund",
        "body": "I'm not happy with my purchase and would like a refund.",
        "sender": "customer@example.com",
        "message_id": "msg125"
    }
    
    result = email_agent.process_email(raw_email)
    
    assert result["status"] == "ticket_created"
    assert result["intent"] == "refund_request"
    assert "ticket" in result["response"].lower()
    assert "TKT-" in result["response"]


def test_process_unclassified_email(email_agent, mock_logger):
    """Test processing an email with unclassified intent."""
    raw_email = {
        "subject": "Random question",
        "body": "This is some random text that doesn't match any pattern.",
        "sender": "customer@example.com",
        "message_id": "msg126"
    }
    
    result = email_agent.process_email(raw_email)
    
    assert result["status"] == "ticket_created"
    assert result["intent"] == "general_inquiry"
    assert "ticket" in result["response"].lower()


def test_process_email_exception(email_agent, mock_faq_agent, mock_logger):
    """Test error handling when processing email."""
    raw_email = {
        "subject": "Test",
        "body": "Test body",
        "sender": "customer@example.com",
        "message_id": "msg127"
    }
    
    # Mock an exception in FAQ agent
    email_agent._classify_intent = MagicMock(side_effect=Exception("Test error"))
    
    result = email_agent.process_email(raw_email)
    
    assert result["status"] == "error"
    assert "error" in result["response"].lower()
    assert result["intent"] == "error"
    
    mock_logger.error.assert_called()
