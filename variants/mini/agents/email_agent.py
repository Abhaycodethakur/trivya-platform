"""
Email Agent for Mini Trivya

Processes incoming customer emails, classifies intent, and routes appropriately.
"""

import re
import uuid
from typing import Dict, Any, Optional

from variants.mini.agents.faq_agent import FAQAgent
from shared.integrations.email_client import EmailClient
from shared.core_functions.logger import get_logger


class EmailAgent:
    """
    Agent for autonomously processing incoming customer emails.
    """
    
    def __init__(
        self,
        faq_agent: FAQAgent,
        email_client: EmailClient,
        logger: Optional[Any] = None
    ):
        """
        Initialize the Email Agent.
        
        Args:
            faq_agent: Instance of FAQAgent for handling FAQ questions
            email_client: Instance of EmailClient for sending responses
            logger: Optional logger instance
        """
        self.faq_agent = faq_agent
        self.email_client = email_client
        
        # Try to get logger from faq_agent if not provided
        if logger:
            self.logger = logger
        elif hasattr(faq_agent, 'logger'):
            self.logger = faq_agent.logger
        else:
            self.logger = get_logger(None).get_logger("EmailAgent")
        
        self.logger.info("Email Agent initialized")
    
    def process_email(self, raw_email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming email.
        
        Args:
            raw_email_data: Dictionary containing email data with keys:
                - subject: Email subject line
                - body: Email body content
                - sender: Sender email address
                - message_id: Unique message identifier
        
        Returns:
            Dictionary containing:
                - status: 'answered', 'ticket_created', or 'error'
                - response: Summary of action taken
                - intent: Classified intent string
        """
        try:
            # Parse email data
            subject = raw_email_data.get('subject', '')
            body = raw_email_data.get('body', '')
            sender = raw_email_data.get('sender', '')
            message_id = raw_email_data.get('message_id', '')
            
            self.logger.info(
                "Processing incoming email",
                extra={
                    "sender": sender,
                    "subject": subject,
                    "message_id": message_id
                }
            )
            
            # Classify intent
            intent = self._classify_intent(subject, body)
            
            self.logger.info(
                f"Email intent classified as: {intent}",
                extra={"intent": intent, "message_id": message_id}
            )
            
            # Route based on intent
            if intent == 'faq':
                # Pass to FAQ agent
                faq_result = self.faq_agent.process_question(
                    question=body,
                    customer_id=sender,
                    channel='email'
                )
                
                if faq_result['status'] == 'answered':
                    response = f"Thank you for your question. {faq_result['response']}"
                    status = 'answered'
                else:
                    # FAQ agent escalated
                    response = self._create_support_ticket(raw_email_data, "FAQ agent escalation")
                    status = 'ticket_created'
            
            elif intent == 'order_status':
                response = self._handle_order_status(body)
                status = 'answered'
            
            elif intent in ['refund_request', 'complaint']:
                response = self._create_support_ticket(raw_email_data, intent)
                status = 'ticket_created'
            
            else:
                # Unclassified intent - escalate
                response = self._create_support_ticket(raw_email_data, "unclassified intent")
                status = 'ticket_created'
            
            # Log outcome
            self.logger.info(
                "Email processed successfully",
                extra={
                    "intent": intent,
                    "status": status,
                    "message_id": message_id
                }
            )
            
            return {
                "status": status,
                "response": response,
                "intent": intent
            }
        
        except Exception as e:
            self.logger.error(
                f"Error processing email: {str(e)}",
                extra={"error": str(e)},
                exc_info=True
            )
            
            return {
                "status": "error",
                "response": "An error occurred while processing your email. Our team has been notified.",
                "intent": "error"
            }
    
    def _classify_intent(self, subject: str, body: str) -> str:
        """
        Classify the intent of an email using keyword matching.
        
        Args:
            subject: Email subject
            body: Email body
            
        Returns:
            Intent string: 'faq', 'order_status', 'refund_request', 'complaint', or 'general_inquiry'
        """
        text = (subject + ' ' + body).lower()
        
        # Order status keywords
        if any(keyword in text for keyword in [
            'where is my order', 'order status', 'tracking', 'shipment',
            'when will it arrive', 'not received', 'order #'
        ]):
            return 'order_status'
        
        # Refund/return keywords
        if any(keyword in text for keyword in [
            'refund', 'return', 'money back', 'cancel order', 'cancelled'
        ]):
            return 'refund_request'
        
        # Complaint keywords
        if any(keyword in text for keyword in [
            'complaint', 'unhappy', 'disappointed', 'terrible', 'awful',
            'not satisfied', 'poor service'
        ]):
            return 'complaint'
        
        # FAQ keywords
        if any(keyword in text for keyword in [
            'how do i', 'how to', 'what is', 'can i', 'is it possible',
            'how does', 'password', 'account', 'reset'
        ]):
            return 'faq'
        
        return 'general_inquiry'
    
    def _handle_order_status(self, body: str) -> str:
        """
        Handle order status inquiries.
        
        Args:
            body: Email body content
            
        Returns:
            Status message with simulated order information
        """
        # Extract order number using regex
        order_match = re.search(r'#?(\d{4,6})', body)
        
        if order_match:
            order_number = order_match.group(1)
            self.logger.info(f"Order number extracted: {order_number}")
            return f"Order #{order_number} is currently in transit and should arrive within 3-5 business days. You can track your shipment using the tracking number sent to your email."
        else:
            return "We'd be happy to help you track your order. Please provide your order number, and we'll look into it right away."
    
    def _create_support_ticket(self, email_data: Dict[str, Any], reason: str) -> str:
        """
        Create a support ticket for the email.
        
        Args:
            email_data: Original email data
            reason: Reason for ticket creation
            
        Returns:
            Message confirming ticket creation
        """
        ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        
        self.logger.info(
            "Support ticket created",
            extra={
                "ticket_id": ticket_id,
                "reason": reason,
                "sender": email_data.get('sender', 'unknown')
            }
        )
        
        return f"A support ticket (ID: {ticket_id}) has been created for this request. Our team will respond within 24 hours."
