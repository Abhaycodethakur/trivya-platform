"""
Unit tests for the Voice Agent.
"""

import pytest
from unittest import mock
from unittest.mock import MagicMock

from variants.mini.agents.voice_agent import VoiceAgent
from variants.mini.agents.faq_agent import FAQAgent
from shared.integrations.twilio_client import TwilioClient


@pytest.fixture
def mock_faq_agent():
    return MagicMock(spec=FAQAgent)


@pytest.fixture
def mock_twilio_client():
    return MagicMock(spec=TwilioClient)


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def voice_agent(mock_faq_agent, mock_twilio_client, mock_logger):
    return VoiceAgent(
        faq_agent=mock_faq_agent,
        twilio_client=mock_twilio_client,
        logger=mock_logger
    )


def test_initialization(mock_faq_agent, mock_twilio_client, mock_logger):
    """Test successful agent initialization."""
    agent = VoiceAgent(
        faq_agent=mock_faq_agent,
        twilio_client=mock_twilio_client,
        logger=mock_logger
    )
    assert agent.faq_agent == mock_faq_agent
    assert agent.twilio_client == mock_twilio_client
    assert agent.logger == mock_logger
    mock_logger.info.assert_called()


def test_handle_answered_call(voice_agent, mock_faq_agent, mock_twilio_client, mock_logger):
    """Test handling a call that is successfully answered."""
    call_sid = "CA123456"
    from_number = "+1234567890"
    
    # Mock transcription
    mock_twilio_client.transcribe_speech.return_value = "What are your hours?"
    
    # Mock FAQ agent response
    mock_faq_agent.process_question.return_value = {
        "status": "answered",
        "response": "Our hours are 9 AM to 6 PM Monday through Friday.",
        "escalated": False
    }
    
    result = voice_agent.handle_call(call_sid, from_number)
    
    assert result["status"] == "answered"
    assert result["transcription"] == "What are your hours?"
    assert "<?xml" in result["twiml"]
    assert "<Say>" in result["twiml"]
    
    mock_twilio_client.answer_call.assert_called_once_with(call_sid)
    mock_twilio_client.play_message.assert_called()
    mock_faq_agent.process_question.assert_called_once()


def test_handle_escalated_call(voice_agent, mock_faq_agent, mock_twilio_client, mock_logger):
    """Test handling a call that requires escalation."""
    call_sid = "CA123456"
    from_number = "+1234567890"
    
    # Mock transcription
    mock_twilio_client.transcribe_speech.return_value = "Complex technical issue"
    
    # Mock FAQ agent escalation
    mock_faq_agent.process_question.return_value = {
        "status": "escalated",
        "response": "Ticket created",
        "escalated": True
    }
    
    result = voice_agent.handle_call(call_sid, from_number)
    
    assert result["status"] == "escalated"
    assert "<Dial>" in result["twiml"]
    assert "transfer" in result["twiml"].lower()


def test_handle_transcription_failure(voice_agent, mock_twilio_client, mock_logger):
    """Test handling a call when transcription fails."""
    call_sid = "CA123456"
    from_number = "+1234567890"
    
    # Mock transcription failure
    mock_twilio_client.transcribe_speech.return_value = ""
    
    result = voice_agent.handle_call(call_sid, from_number)
    
    assert result["status"] == "transcription_failed"
    assert result["transcription"] is None
    assert "<Dial>" in result["twiml"]


def test_handle_call_exception(voice_agent, mock_faq_agent, mock_twilio_client, mock_logger):
    """Test error handling when processing call."""
    call_sid = "CA123456"
    from_number = "+1234567890"
    
    # Mock an exception
    mock_twilio_client.answer_call.side_effect = Exception("Test error")
    
    result = voice_agent.handle_call(call_sid, from_number)
    
    assert result["status"] == "error"
    assert result["transcription"] is None
    assert "<Dial>" in result["twiml"]
    
    mock_logger.error.assert_called()
