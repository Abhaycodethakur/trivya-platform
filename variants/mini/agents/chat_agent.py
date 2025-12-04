"""
Chat Agent for Mini Trivya

Handles real-time conversations with customers on live chat platforms.
"""

from typing import Dict, Any, Optional

from variants.mini.agents.faq_agent import FAQAgent
from shared.core_functions.logger import get_logger


class ChatAgent:
    """
    Agent for handling real-time customer conversations on live chat.
    """
    
    def __init__(
        self,
        faq_agent: FAQAgent,
        logger: Optional[Any] = None
    ):
        """
        Initialize the Chat Agent.
        
        Args:
            faq_agent: Instance of FAQAgent for handling questions
            logger: Optional logger instance
        """
        self.faq_agent = faq_agent
        
        # Try to get logger from faq_agent if not provided
        if logger:
            self.logger = logger
        elif hasattr(faq_agent, 'logger'):
            self.logger = faq_agent.logger
        else:
            self.logger = get_logger(None).get_logger("ChatAgent")
        
        # Track active chat sessions
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("Chat Agent initialized")
    
    def handle_message(
        self,
        message: str,
        customer_id: str,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Handle an incoming chat message.
        
        Args:
            message: The customer's message
            customer_id: Unique customer identifier
            session_id: Unique session identifier
            
        Returns:
            Dictionary containing:
                - status: 'answered', 'escalated', or 'error'
                - response: Message to send to customer
                - requires_human_agent: Boolean indicating if human agent needed
        """
        try:
            self.logger.info(
                "Processing incoming chat message",
                extra={
                    "customer_id": customer_id,
                    "session_id": session_id,
                    "message_length": len(message)
                }
            )
            
            # Check if this is a follow-up message
            if self._is_follow_up(message, session_id):
                self.logger.info(
                    "Message identified as follow-up",
                    extra={"session_id": session_id}
                )
                return {
                    "status": "answered",
                    "response": "You're welcome! Is there anything else I can help you with?",
                    "requires_human_agent": False
                }
            
            # Process as new question via FAQ agent
            faq_result = self.faq_agent.process_question(
                question=message,
                customer_id=customer_id,
                channel='chat'
            )
            
            # Store last question in session
            if session_id not in self.active_sessions:
                self.active_sessions[session_id] = {}
            self.active_sessions[session_id]['last_question'] = message
            self.active_sessions[session_id]['last_status'] = faq_result['status']
            
            # Analyze FAQ agent response
            if faq_result['status'] == 'answered':
                # Format response for chat
                formatted_response = self._format_for_chat(faq_result['response'])
                
                self.logger.info(
                    "Chat message answered successfully",
                    extra={"session_id": session_id}
                )
                
                return {
                    "status": "answered",
                    "response": formatted_response,
                    "requires_human_agent": False
                }
            
            else:
                # FAQ agent escalated or error
                self.logger.info(
                    "Chat message requires human agent",
                    extra={
                        "session_id": session_id,
                        "reason": faq_result['status']
                    }
                )
                
                return {
                    "status": "escalated",
                    "response": "Let me connect you with one of our human agents who can better assist you with this. They'll be with you in just a moment.",
                    "requires_human_agent": True
                }
        
        except Exception as e:
            self.logger.error(
                f"Error handling chat message: {str(e)}",
                extra={"error": str(e), "session_id": session_id},
                exc_info=True
            )
            
            return {
                "status": "error",
                "response": "I'm having trouble processing your request. Let me get a human agent to help you.",
                "requires_human_agent": True
            }
    
    def _is_follow_up(self, message: str, session_id: str) -> bool:
        """
        Check if message is a follow-up to previous conversation.
        
        Args:
            message: The customer's message
            session_id: Session identifier
            
        Returns:
            True if message appears to be a follow-up, False otherwise
        """
        # Simple follow-up detection based on common phrases
        message_lower = message.lower().strip()
        
        follow_up_phrases = [
            'thanks', 'thank you', 'ty', 'thx',
            'ok', 'okay', 'got it', 'understood',
            'perfect', 'great', 'awesome',
            'that helps', 'that worked'
        ]
        
        # Check if message is just a follow-up phrase
        if message_lower in follow_up_phrases:
            return True
        
        # Check if it's a short acknowledgment
        if len(message.split()) <= 3 and any(phrase in message_lower for phrase in follow_up_phrases):
            return True
        
        return False
    
    def _format_for_chat(self, response: str) -> str:
        """
        Format response to be more suitable for chat interface.
        
        Args:
            response: Original response from FAQ agent
            
        Returns:
            Formatted response for chat
        """
        # For chat, we want responses to be concise and friendly
        # Remove source citations if present
        if "(Source:" in response:
            response = response.split("(Source:")[0].strip()
        
        # Ensure response is not too long for chat
        if len(response) > 500:
            # Truncate and add ellipsis if needed
            response = response[:497] + "..."
        
        return response
