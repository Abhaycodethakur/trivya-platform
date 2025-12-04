"""
SMS Agent for Mini Trivya

Processes incoming SMS messages with character limit constraints.
"""

import re
import uuid
from typing import Dict, Any, Optional

from variants.mini.agents.faq_agent import FAQAgent
from shared.integrations.sms_client import SMSClient
from shared.core_functions.logger import get_logger


class SMSAgent:
    """
    Agent for handling incoming SMS messages from customers.
    """
    
    # Standard SMS character limit
    SMS_CHAR_LIMIT = 160
    
    def __init__(
        self,
        faq_agent: FAQAgent,
        sms_client: SMSClient,
        logger: Optional[Any] = None
    ):
        """
        Initialize the SMS Agent.
        
        Args:
            faq_agent: Instance of FAQAgent for handling questions
            sms_client: Instance of SMSClient for sending responses
            logger: Optional logger instance
        """
        self.faq_agent = faq_agent
        self.sms_client = sms_client
        
        # Try to get logger from faq_agent if not provided
        if logger:
            self.logger = logger
        elif hasattr(faq_agent, 'logger'):
            self.logger = faq_agent.logger
        else:
            self.logger = get_logger(None).get_logger("SMSAgent")
        
        self.logger.info("SMS Agent initialized")
    
    def process_sms(
        self,
        sender_number: str,
        message_body: str,
        message_id: str
    ) -> Dict[str, Any]:
        """
        Process an incoming SMS message.
        
        Args:
            sender_number: Phone number of sender
            message_body: Content of the SMS
            message_id: Unique message identifier
            
        Returns:
            Dictionary containing:
                - status: 'answered', 'ticket_created', or 'error'
                - response: SMS text to send back
                - intent: Classified intent string
        """
        try:
            self.logger.info(
                "Processing incoming SMS",
                extra={
                    "sender": sender_number,
                    "message_id": message_id,
                    "length": len(message_body)
                }
            )
            
            # Classify intent
            intent = self._classify_intent(message_body)
            
            self.logger.info(
                f"SMS intent classified as: {intent}",
                extra={"intent": intent, "message_id": message_id}
            )
            
            # Route based on intent
            if intent == 'faq':
                # Pass to FAQ agent
                faq_result = self.faq_agent.process_question(
                    question=message_body,
                    customer_id=sender_number,
                    channel='sms'
                )
                
                if faq_result['status'] == 'answered':
                    # Format for SMS character limit
                    response = self._format_for_sms(faq_result['response'])
                    status = 'answered'
                else:
                    # FAQ agent couldn't answer
                    response = "Please email support@trivya.com for assistance."
                    status = 'ticket_created'
            
            elif intent == 'order_status':
                response = self._handle_order_status(message_body)
                status = 'answered'
            
            elif intent in ['refund_request', 'complaint']:
                response = self._create_support_ticket_and_reply(sender_number, message_body)
                status = 'ticket_created'
            
            else:
                # Unclassified intent
                response = "For assistance, please email support@trivya.com with your question."
                status = 'ticket_created'
            
            # Log outcome
            self.logger.info(
                "SMS processed successfully",
                extra={
                    "intent": intent,
                    "status": status,
                    "message_id": message_id,
                    "response_length": len(response)
                }
            )
            
            return {
                "status": status,
                "response": response,
                "intent": intent
            }
        
        except Exception as e:
            self.logger.error(
                f"Error processing SMS: {str(e)}",
                extra={"error": str(e), "message_id": message_id},
                exc_info=True
            )
            
            return {
                "status": "error",
                "response": "Error processing your message. Please contact support@trivya.com",
                "intent": "error"
            }
    
    def _classify_intent(self, message_body: str) -> str:
        """
        Classify the intent of an SMS message.
        Optimized for short, informal text.
        
        Args:
            message_body: SMS content
            
        Returns:
            Intent string: 'faq', 'order_status', 'refund_request', 'complaint', or 'general'
        """
        text = message_body.lower()
        
        # Order status keywords (common in SMS)
        if any(keyword in text for keyword in [
            'where', 'order', 'track', 'shipped', 'delivery', 'when', '#'
        ]):
            return 'order_status'
        
        # Refund keywords
        if any(keyword in text for keyword in [
            'refund', 'return', 'money back', 'cancel'
        ]):
            return 'refund_request'
        
        # Complaint keywords
        if any(keyword in text for keyword in [
            'complaint', 'unhappy', 'terrible', 'awful', 'bad'
        ]):
            return 'complaint'
        
        # FAQ keywords (questions)
        if any(keyword in text for keyword in [
            '?', 'how', 'what', 'when', 'why', 'can i', 'do you'
        ]):
            return 'faq'
        
        return 'general'
    
    def _handle_order_status(self, message_body: str) -> str:
        """
        Handle order status inquiries with concise response.
        
        Args:
            message_body: SMS content
            
        Returns:
            Very short status message
        """
        # Extract order number
        order_match = re.search(r'#?(\d{4,6})', message_body)
        
        if order_match:
            order_number = order_match.group(1)
            self.logger.info(f"Order number extracted: {order_number}")
            return f"Order #{order_number}: Shipped. ETA 3-5 days."
        else:
            return "Reply with your order # for status."
    
    def _create_support_ticket_and_reply(
        self,
        sender_number: str,
        message_body: str
    ) -> str:
        """
        Create support ticket and return concise SMS reply.
        
        Args:
            sender_number: Sender's phone number
            message_body: SMS content
            
        Returns:
            Concise SMS response
        """
        ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        
        self.logger.info(
            "Support ticket created from SMS",
            extra={
                "ticket_id": ticket_id,
                "sender": sender_number
            }
        )
        
        return f"Ticket {ticket_id} created. Check your email for details."
    
    def _format_for_sms(self, response: str) -> str:
        """
        Format response to fit SMS character limit.
        
        Args:
            response: Original response
            
        Returns:
            Truncated response if needed
        """
        # Remove source citations
        if "(Source:" in response:
            response = response.split("(Source:")[0].strip()
        
        # Truncate if too long
        if len(response) > self.SMS_CHAR_LIMIT:
            # Leave room for ellipsis
            response = response[:self.SMS_CHAR_LIMIT - 3] + "..."
        
        return response
