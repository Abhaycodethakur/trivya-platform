"""
Unit tests for the SMS Agent.
"""

import pytest
from unittest import mock
from unittest.mock import MagicMock

from variants.mini.agents.sms_agent import SMSAgent
from variants.mini.agents.faq_agent import FAQAgent
from shared.integrations.sms_client import SMSClient


@pytest.fixture
def mock_faq_agent():
    return MagicMock(spec=FAQAgent)


@pytest.fixture
def mock_sms_client():
    return MagicMock(spec=SMSClient)


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def sms_agent(mock_faq_agent, mock_sms_client, mock_logger):
    return SMSAgent(
        faq_agent=mock_faq_agent,
        sms_client=mock_sms_client,
        logger=mock_logger
    )


def test_initialization(mock_faq_agent, mock_sms_client, mock_logger):
    """Test successful agent initialization."""
    agent = SMSAgent(
        faq_agent=mock_faq_agent,
        sms_client=mock_sms_client,
        logger=mock_logger
    )
    assert agent.faq_agent == mock_faq_agent
    assert agent.sms_client == mock_sms_client
    assert agent.logger == mock_logger
    mock_logger.info.assert_called()


def test_process_faq_sms(sms_agent, mock_faq_agent, mock_logger):
    """Test processing an SMS with FAQ intent."""
    sender = "+1234567890"
    message = "What's your phone number?"
    msg_id = "sms123"
    
    # Mock FAQ agent response
    mock_faq_agent.process_question.return_value = {
        "status": "answered",
        "response": "Our phone number is 1-800-TRIVYA (1-800-874-8921).",
        "escalated": False
    }
    
    result = sms_agent.process_sms(sender, message, msg_id)
    
    assert result["status"] == "answered"
    assert result["intent"] == "faq"
    assert len(result["response"]) <= 160
    assert "800" in result["response"] or "TRIVYA" in result["response"]
    
    mock_faq_agent.process_question.assert_called_once()


def test_process_order_status_sms(sms_agent, mock_logger):
    """Test processing an SMS with order status intent."""
    sender = "+1234567890"
    message = "Where is order #12345?"
    msg_id = "sms124"
    
    result = sms_agent.process_sms(sender, message, msg_id)
    
    assert result["status"] == "answered"
    assert result["intent"] == "order_status"
    assert "12345" in result["response"]
    assert len(result["response"]) <= 160


def test_process_refund_request_sms(sms_agent, mock_logger):
    """Test processing an SMS with refund request intent."""
    sender = "+1234567890"
    message = "I want a refund"
    msg_id = "sms125"
    
    result = sms_agent.process_sms(sender, message, msg_id)
    
    assert result["status"] == "ticket_created"
    assert result["intent"] == "refund_request"
    assert "ticket" in result["response"].lower() or "email" in result["response"].lower()
    assert len(result["response"]) <= 160


def test_process_unclassified_sms(sms_agent, mock_logger):
    """Test processing an SMS with unclassified intent."""
    sender = "+1234567890"
    message = "Random text"
    msg_id = "sms126"
    
    result = sms_agent.process_sms(sender, message, msg_id)
    
    assert result["status"] == "ticket_created"
    assert result["intent"] == "general"
    assert "email" in result["response"].lower() or "support" in result["response"].lower()
    assert len(result["response"]) <= 160


def test_process_sms_exception(sms_agent, mock_faq_agent, mock_logger):
    """Test error handling when processing SMS."""
    sender = "+1234567890"
    message = "Test"
    msg_id = "sms127"
    
    # Mock an exception
    sms_agent._classify_intent = MagicMock(side_effect=Exception("Test error"))
    
    result = sms_agent.process_sms(sender, message, msg_id)
    
    assert result["status"] == "error"
    assert result["intent"] == "error"
    assert "error" in result["response"].lower() or "support" in result["response"].lower()
    assert len(result["response"]) <= 160
    
    mock_logger.error.assert_called()
