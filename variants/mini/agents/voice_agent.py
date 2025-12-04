"""
Voice Agent for Mini Trivya

Handles inbound phone calls with speech-to-text and text-to-speech.
"""

from typing import Dict, Any, Optional

from variants.mini.agents.faq_agent import FAQAgent
from shared.integrations.twilio_client import TwilioClient
from shared.core_functions.logger import get_logger


class VoiceAgent:
    """
    Agent for handling inbound phone calls.
    Acts as a virtual receptionist with voice capabilities.
    """
    
    def __init__(
        self,
        faq_agent: FAQAgent,
        twilio_client: TwilioClient,
        logger: Optional[Any] = None
    ):
        """
        Initialize the Voice Agent.
        
        Args:
            faq_agent: Instance of FAQAgent for handling questions
            twilio_client: Instance of TwilioClient for voice operations
            logger: Optional logger instance
        """
        self.faq_agent = faq_agent
        self.twilio_client = twilio_client
        
        # Try to get logger from faq_agent if not provided
        if logger:
            self.logger = logger
        elif hasattr(faq_agent, 'logger'):
            self.logger = faq_agent.logger
        else:
            self.logger = get_logger(None).get_logger("VoiceAgent")
        
        self.logger.info("Voice Agent initialized")
    
    def handle_call(
        self,
        call_sid: str,
        from_number: str
    ) -> Dict[str, Any]:
        """
        Handle an incoming phone call.
        
        Args:
            call_sid: Twilio call SID
            from_number: Caller's phone number
            
        Returns:
            Dictionary containing TwiML response and call status
        """
        try:
            self.logger.info(
                "Processing incoming call",
                extra={
                    "call_sid": call_sid,
                    "from": from_number
                }
            )
            
            # Answer the call
            self.twilio_client.answer_call(call_sid)
            
            # Play greeting
            greeting = self._generate_greeting_message()
            self.twilio_client.play_message(call_sid, greeting)
            
            # Transcribe caller's speech
            # In real implementation, this would wait for recording
            transcribed_text = self.twilio_client.transcribe_speech(
                call_sid,
                recording_url=f"stub_recording_{call_sid}"
            )
            
            if not transcribed_text:
                # Transcription failed
                self.logger.warning("Speech transcription failed", extra={"call_sid": call_sid})
                error_msg = "I'm sorry, I couldn't understand that. Let me transfer you to a human agent."
                self.twilio_client.play_message(call_sid, error_msg)
                
                return {
                    "status": "transcription_failed",
                    "twiml": self._generate_twiml_transfer(),
                    "transcription": None
                }
            
            self.logger.info(
                "Speech transcribed",
                extra={"call_sid": call_sid, "transcription": transcribed_text}
            )
            
            # Process with FAQ agent
            faq_result = self.faq_agent.process_question(
                question=transcribed_text,
                customer_id=from_number,
                channel='voice'
            )
            
            # Handle FAQ response
            if faq_result['status'] == 'answered':
                # Speak the answer
                response_text = faq_result['response']
                self.twilio_client.play_message(call_sid, response_text)
                
                self.logger.info(
                    "Call answered successfully",
                    extra={"call_sid": call_sid}
                )
                
                return {
                    "status": "answered",
                    "twiml": self._generate_twiml_response(response_text),
                    "transcription": transcribed_text
                }
            
            else:
                # Escalate to human
                transfer_msg = self._generate_transfer_message()
                self.twilio_client.play_message(call_sid, transfer_msg)
                
                self.logger.info(
                    "Call escalated to human",
                    extra={"call_sid": call_sid}
                )
                
                return {
                    "status": "escalated",
                    "twiml": self._generate_twiml_transfer(),
                    "transcription": transcribed_text
                }
        
        except Exception as e:
            self.logger.error(
                f"Error handling call: {str(e)}",
                extra={"error": str(e), "call_sid": call_sid},
                exc_info=True
            )
            
            # Play error message and transfer
            error_msg = self._generate_error_message()
            try:
                self.twilio_client.play_message(call_sid, error_msg)
            except:
                pass
            
            return {
                "status": "error",
                "twiml": self._generate_twiml_transfer(),
                "transcription": None
            }
    
    def _generate_greeting_message(self) -> str:
        """
        Generate the initial greeting message.
        
        Returns:
            Greeting text
        """
        return "Hello, you've reached the virtual assistant for Trivya. How can I help you today?"
    
    def _generate_transfer_message(self) -> str:
        """
        Generate the message for transferring to human.
        
        Returns:
            Transfer message text
        """
        return "Let me transfer you to one of our team members who can better assist you. Please hold."
    
    def _generate_error_message(self) -> str:
        """
        Generate the error message.
        
        Returns:
            Error message text
        """
        return "I apologize, but I'm experiencing technical difficulties. Let me transfer you to a human agent."
    
    def _generate_twiml_response(self, message: str) -> str:
        """
        Generate TwiML response for speaking a message.
        
        Args:
            message: Text to speak
            
        Returns:
            TwiML XML string
        """
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>{message}</Say>
    <Hangup/>
</Response>"""
    
    def _generate_twiml_transfer(self) -> str:
        """
        Generate TwiML response for transferring call.
        
        Returns:
            TwiML XML string with transfer instruction
        """
        transfer_msg = self._generate_transfer_message()
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>{transfer_msg}</Say>
    <Dial>+1-800-SUPPORT</Dial>
</Response>"""
