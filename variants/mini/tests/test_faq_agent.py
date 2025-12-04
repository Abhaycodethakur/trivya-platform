"""
Unit tests for the FAQ Agent.
"""

import pytest
from unittest import mock
from unittest.mock import MagicMock, patch

from variants.mini.agents.faq_agent import FAQAgent
from shared.knowledge_base.kb_manager import KnowledgeBaseManager


@pytest.fixture
def mock_kb_manager():
    return MagicMock(spec=KnowledgeBaseManager)


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def faq_agent(mock_kb_manager, mock_logger):
    # Patch the get_logger call inside FAQAgent if it's used, 
    # but we are passing a logger explicitly so it should use that.
    return FAQAgent(kb_manager=mock_kb_manager, logger=mock_logger)


def test_initialization(mock_kb_manager, mock_logger):
    """Test successful agent initialization."""
    agent = FAQAgent(kb_manager=mock_kb_manager, logger=mock_logger)
    assert agent.kb_manager == mock_kb_manager
    assert agent.logger == mock_logger
    assert agent.confidence_threshold == 0.75
    mock_logger.info.assert_called()


def test_process_question_answered(faq_agent, mock_kb_manager, mock_logger):
    """Test a question that is successfully answered."""
    question = "What is the refund policy?"
    customer_id = "cust_123"
    channel = "web"

    # Mock KB search result
    mock_kb_manager.search.return_value = {
        "context": [
            {
                "content": "Refunds are allowed within 30 days.",
                "metadata": {"source": "policy.pdf"},
                "similarity_score": 0.85
            }
        ]
    }

    result = faq_agent.process_question(question, customer_id, channel)

    assert result["status"] == "answered"
    assert "Refunds are allowed within 30 days." in result["response"]
    assert result["escalated"] is False
    
    mock_kb_manager.search.assert_called_once_with(question)
    mock_logger.info.assert_called()


def test_process_question_escalated_low_score(faq_agent, mock_kb_manager, mock_logger):
    """Test a question that is escalated due to a low search score."""
    question = "Who is the CEO?"
    customer_id = "cust_123"
    channel = "web"

    # Mock KB search result with low score
    mock_kb_manager.search.return_value = {
        "context": [
            {
                "content": "The CEO is John Doe.",
                "metadata": {"source": "org_chart.pdf"},
                "similarity_score": 0.50
            }
        ]
    }

    result = faq_agent.process_question(question, customer_id, channel)

    assert result["status"] == "escalated"
    assert "created a support ticket" in result["response"]
    assert result["escalated"] is True
    
    mock_kb_manager.search.assert_called_once_with(question)


def test_process_question_escalated_no_results(faq_agent, mock_kb_manager, mock_logger):
    """Test a question that is escalated because no results are found."""
    question = "Unknown question"
    customer_id = "cust_123"
    channel = "web"

    # Mock KB search result with no context
    mock_kb_manager.search.return_value = {
        "context": []
    }

    result = faq_agent.process_question(question, customer_id, channel)

    assert result["status"] == "escalated"
    assert "created a support ticket" in result["response"]
    assert result["escalated"] is True


def test_escalate_to_human_generates_unique_id(faq_agent):
    """Test that escalation generates a unique ticket ID each time."""
    question = "Help"
    customer_id = "cust_123"
    channel = "web"

    response1 = faq_agent._escalate_to_human(question, customer_id, channel)
    response2 = faq_agent._escalate_to_human(question, customer_id, channel)

    # Extract IDs (assuming format "ID: SUP-XXXXXXX")
    import re
    id_pattern = r"SUP-[A-Z0-9]+"
    
    id1 = re.search(id_pattern, response1).group()
    id2 = re.search(id_pattern, response2).group()

    assert id1 != id2


def test_process_question_kb_search_exception(faq_agent, mock_kb_manager, mock_logger):
    """Test error handling when KB search raises an exception."""
    question = "Crash me"
    customer_id = "cust_123"
    channel = "web"

    # Mock _search_knowledge_base to raise exception
    # We need to mock the method on the agent instance itself
    faq_agent._search_knowledge_base = MagicMock(side_effect=Exception("KB Down"))

    result = faq_agent.process_question(question, customer_id, channel)

    assert result["status"] == "error"
    assert "unexpected error" in result["response"]
    assert result["escalated"] is True
    
    mock_logger.error.assert_called()
