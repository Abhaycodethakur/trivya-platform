"""
FAQ Agent for Mini Trivya
"""

import uuid
import traceback
from typing import Dict, Any, Optional

from shared.knowledge_base.kb_manager import KnowledgeBaseManager
from shared.core_functions.logger import get_logger

# Try to import settings, default to 0.75 if not found
try:
    from variants.mini.config import settings
    FAQ_CONFIDENCE_THRESHOLD = getattr(settings, 'FAQ_CONFIDENCE_THRESHOLD', 0.75)
except ImportError:
    FAQ_CONFIDENCE_THRESHOLD = 0.75


class FAQAgent:
    """
    Agent for handling FAQ inquiries using the Knowledge Base.
    """

    def __init__(
        self,
        kb_manager: KnowledgeBaseManager,
        logger: Optional[Any] = None
    ):
        """
        Initialize the FAQ Agent.

        Args:
            kb_manager: Instance of KnowledgeBaseManager
            logger: Optional logger instance
        """
        self.kb_manager = kb_manager
        # If logger is not provided, we can try to get it from kb_manager's config if available,
        # or just use the default get_logger. Since get_logger requires config, and we don't
        # strictly pass config here, we'll assume kb_manager has it or use a default.
        # However, the prompt says "optional logger instance (from shared.core_functions.logger)".
        # We'll use the passed logger or get a new one.
        if logger:
            self.logger = logger
        elif hasattr(kb_manager, 'config'):
             self.logger = get_logger(kb_manager.config).get_logger("FAQAgent")
        else:
             # Fallback if no config is available easily, though ideally we should have it.
             # For now, we'll try to get a generic logger.
             self.logger = get_logger(None).get_logger("FAQAgent")

        self.confidence_threshold = FAQ_CONFIDENCE_THRESHOLD

        self.logger.info(
            "FAQ Agent initialized",
            extra={"confidence_threshold": self.confidence_threshold}
        )

    def process_question(
        self,
        question: str,
        customer_id: str,
        channel: str
    ) -> Dict[str, Any]:
        """
        Process an incoming customer question.

        Args:
            question: The customer's question
            customer_id: Unique identifier for the customer
            channel: Communication channel (e.g., 'web', 'email')

        Returns:
            Dictionary containing status, response, and escalation flag
        """
        try:
            self.logger.info(
                "Processing incoming question",
                extra={
                    "customer_id": customer_id,
                    "channel": channel,
                    "question_length": len(question)
                }
            )

            # Search Knowledge Base
            search_results = self._search_knowledge_base(question)
            
            # Evaluate results
            # The search_results from kb_manager.search() returns a dict with 'context' list.
            # We need to check if we have results and if the top result meets the threshold.
            # RAGPipeline.retrieve_context returns a list of dicts with 'similarity_score'.
            
            # kb_manager.search returns:
            # {
            #     "query": user_query,
            #     "prompt": prompt,
            #     "context": context,  # List of docs
            #     "context_count": len(context)
            # }
            
            context = search_results.get("context", [])
            best_score = 0.0
            
            if context:
                # Assuming the first result is the best match
                # RAGPipeline filters by threshold if configured, but we double check here
                # or rely on the score of the top result.
                top_result = context[0]
                best_score = top_result.get("similarity_score", 0.0)

            status = "escalated"
            response = ""
            escalated = True

            if context and best_score >= self.confidence_threshold:
                status = "answered"
                response = self._generate_response(search_results)
                escalated = False
            elif not context:
                # No results found
                response = self._escalate_to_human(question, customer_id, channel)
            else:
                # Results found but score too low
                response = self._escalate_to_human(question, customer_id, channel)

            self._log_interaction(
                question=question,
                response=response,
                status=status,
                escalated=escalated,
                score=best_score,
                customer_id=customer_id,
                channel=channel
            )

            return {
                "status": status,
                "response": response,
                "escalated": escalated
            }

        except Exception as e:
            self.logger.error(
                f"Error processing question: {str(e)}",
                extra={"traceback": traceback.format_exc()}
            )
            return {
                "status": "error",
                "response": "An unexpected error occurred. We have escalated this to a human agent.",
                "escalated": True
            }

    def _search_knowledge_base(self, question: str) -> Dict[str, Any]:
        """
        Search the knowledge base for the given question.

        Args:
            question: The question to search for

        Returns:
            Search results dictionary or empty dict on failure
        """
        try:
            # We use search() which returns the RAG result
            return self.kb_manager.search(question)
        except Exception as e:
            self.logger.error(f"Knowledge base search failed: {str(e)}")
            return {}

    def _generate_response(self, search_results: Dict[str, Any]) -> str:
        """
        Generate a user-friendly response from search results.

        Args:
            search_results: Dictionary containing search context

        Returns:
            Formatted response string
        """
        context = search_results.get("context", [])
        if not context:
            return "I couldn't find any information to answer your question."

        # Use the top result
        top_result = context[0]
        content = top_result.get("content", "").strip()
        metadata = top_result.get("metadata", {})
        source = metadata.get("source", "Knowledge Base")

        return f"{content}\n\n(Source: {source})"

    def _escalate_to_human(self, question: str, customer_id: str, channel: str) -> str:
        """
        Escalate the question to a human agent.

        Args:
            question: The original question
            customer_id: The customer ID
            channel: The channel

        Returns:
            Customer-facing escalation message
        """
        ticket_id = f"SUP-{uuid.uuid4().hex[:8].upper()}"
        
        self.logger.info(
            "Escalating to human agent",
            extra={
                "ticket_id": ticket_id,
                "customer_id": customer_id,
                "reason": "Low confidence or no answer found"
            }
        )
        
        return f"I've created a support ticket for you (ID: {ticket_id}). A human agent will be with you shortly."

    def _log_interaction(
        self,
        question: str,
        response: str,
        status: str,
        escalated: bool,
        score: float,
        customer_id: str,
        channel: str
    ):
        """
        Log the full details of the interaction.
        """
        self.logger.info(
            "Interaction processed",
            extra={
                "question": question,
                "response_preview": response[:50] + "..." if len(response) > 50 else response,
                "status": status,
                "escalated": escalated,
                "confidence_score": score,
                "customer_id": customer_id,
                "channel": channel
            }
        )
