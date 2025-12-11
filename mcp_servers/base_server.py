"""
Base Class for MCP (Model Context Protocol) Servers.

This module defines the abstract base class and common interface for all MCP servers
in the Trivya platform. It handles connection management, authentication, message
routing, and error handling to ensure consistency across the ecosystem.
"""

import asyncio
import json
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Coroutine
from enum import Enum
from pydantic import BaseModel, Field

# Import shared core components
try:
    from shared.core_functions.config import Config
    from shared.core_functions.logger import get_logger, TrivyaLogger
    from shared.core_functions.security import SecurityManager  # Assuming exists based on prompt context
except ImportError:
    # Fallback for testing or partial environment
    Config = None
    get_logger = None
    SecurityManager = None
    TrivyaLogger = None

# --- Message Protocol Definitions ---

class MessageType(str, Enum):
    """Supported MCP message types"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"

class MCPMessageHeader(BaseModel):
    """Standard header for MCP messages"""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message_type: MessageType
    source: str
    destination: Optional[str] = None
    version: str = "1.0"

class MCPMessage(BaseModel):
    """Standard MCP message format"""
    header: MCPMessageHeader
    body: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# --- Error Classes ---

class MCPServerError(Exception):
    """Base exception for all MCP server errors"""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", details: Optional[Dict] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

class MCPAuthenticationError(MCPServerError):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, code="AUTH_FAILED")

class MCPValidationError(MCPServerError):
    """Raised when request validation fails"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, code="VALIDATION_ERROR", details=details)

class MCPConnectionError(MCPServerError):
    """Raised when connection issues occur"""
    def __init__(self, message: str):
        super().__init__(message, code="CONNECTION_ERROR")

# --- Base Server Class ---

class BaseMCPServer(ABC):
    """
    Abstract Base Class for all MCP Servers.
    
    Provides standardized functionality for:
    - Connection management
    - Message routing and handling
    - Authentication and Security
    - Logging and Error tracking
    """

    def __init__(self, name: str, config: Optional['Config'] = None):
        """
        Initialize the base MCP server.
        
        Args:
            name: Unique identifier for this server instance
            config: Configuration object (uses default if None)
        """
        self.name = name
        self.config = config or (Config() if Config else None)
        
        # Initialize Logger
        if get_logger:
            self.logger = get_logger(self.config) if self.config else get_logger()
            wrapper_cls = type('LoggerWrapper', (), {})
            self._log = lambda level, msg, **kwargs: getattr(self.logger.get_logger(f"mcp.{self.name}"), level)(msg, **kwargs)
        else:
            # Fallback simple logger
            import logging
            logging.basicConfig(level=logging.INFO)
            self._logger = logging.getLogger(f"mcp.{self.name}")
            self._log = lambda level, msg, **kwargs: getattr(self._logger, level)(msg)

        # Initialize Security (if available)
        self.security = SecurityManager(self.config) if SecurityManager and self.config else None
        
        # Connection Pool (simulate tracking active connections)
        self._active_connections: Dict[str, Dict[str, Any]] = {}
        self._is_running = False
        
        self.log("info", f"Initializing MCP Server: {self.name}", extra={"server_name": self.name})

    def log(self, level: str, message: str, **kwargs):
        """Internal helper for consistent logging"""
        if self._log:
            self._log(level, message, **kwargs)

    # --- Abstract Methods (Subclasses must implement) ---

    @abstractmethod
    async def handle_request(self, request: MCPMessage) -> Dict[str, Any]:
        """Process incoming request and return result data"""
        pass

    @abstractmethod
    async def validate_request(self, request: MCPMessage) -> bool:
        """Validate request format and content"""
        pass

    @abstractmethod
    async def format_response(self, data: Dict[str, Any], correlation_id: str) -> MCPMessage:
        """Format response data into standard MCP message"""
        pass

    @abstractmethod
    async def cleanup(self):
        """Clean up resources on shutdown"""
        pass

    # --- Connection Management ---

    async def connect(self, connection_id: str, client_info: Dict[str, Any]) -> bool:
        """
        Establish a new connection.
        
        Args:
            connection_id: Unique ID for the connection
            client_info: Metadata about the connecting client
            
        Returns:
            bool: True if connection accepted
        """
        try:
            if not self._is_running:
                await self.start()

            # Optional: Authenticate connection request
            if "api_key" in client_info:
                if not await self._authenticate_client(client_info["api_key"]):
                    self.log("warning", f"Connection rejected for {connection_id}: Auth failed")
                    raise MCPAuthenticationError("Invalid API Key")

            self._active_connections[connection_id] = {
                "info": client_info,
                "connected_at": datetime.utcnow()
            }
            self.log("info", f"Connection established: {connection_id}")
            return True

        except Exception as e:
            self.log("error", f"Connection error for {connection_id}: {str(e)}")
            raise MCPConnectionError(f"Failed to establish connection: {str(e)}")

    async def disconnect(self, connection_id: str):
        """Close an active connection"""
        if connection_id in self._active_connections:
            del self._active_connections[connection_id]
            self.log("info", f"Connection closed: {connection_id}")

    # --- Lifecycle Management ---

    async def start(self):
        """Start the server and resources"""
        if self._is_running:
            return
        
        self._is_running = True
        self.log("info", f"MCP Server '{self.name}' started.")

    async def stop(self):
        """Stop server and cleanup resources"""
        self._is_running = False
        self.log("info", "Stopping MCP Server...")
        
        # Close all connections
        connections = list(self._active_connections.keys())
        for conn_id in connections:
            await self.disconnect(conn_id)
            
        await self.cleanup()
        self.log("info", "MCP Server stopped.")

    # --- Message Processing ---

    async def process_message(self, raw_message: Union[str, Dict[str, Any]]) -> MCPMessage:
        """
        Main entry point for processing incoming messages.
        
        1. Deserializes message
        2. Validates structure
        3. Routes to handler
        4. Returns formatted response
        """
        correlation_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            # 1. Deserialize/Parse
            if isinstance(raw_message, str):
                try:
                    message_dict = json.loads(raw_message)
                except json.JSONDecodeError:
                    raise MCPValidationError("Invalid JSON format")
            else:
                message_dict = raw_message

            # 2. Convert to MCPMessage
            try:
                request = MCPMessage(**message_dict)
                correlation_id = request.header.correlation_id # Use client's correlation ID if present
            except Exception as e:
                raise MCPValidationError(f"Invalid message structure: {str(e)}")

            self.log("info", f"Processing {request.header.message_type} from {request.header.source}", 
                     correlation_id=correlation_id)

            # 3. Validate
            await self.validate_request(request)

            # 4. Handle based on type
            response_data = {}
            if request.header.message_type == MessageType.REQUEST:
                response_data = await self.handle_request(request)
            elif request.header.message_type == MessageType.NOTIFICATION:
                # Notifications might not need a response, but we acknowledge receipt
                await self.handle_request(request)
                response_data = {"status": "acknowledged"}
            else:
                raise MCPValidationError(f"Unsupported message type: {request.header.message_type}")

            # 5. Format Response
            response = await self.format_response(response_data, correlation_id)
            return response

        except MCPServerError as e:
            self.log("error", f"MCP Error: {e.message}", correlation_id=correlation_id)
            return self._create_error_response(e, correlation_id)
            
        except Exception as e:
            self.log("error", f"Unexpected Error: {str(e)}", correlation_id=correlation_id)
            return self._create_error_response(
                MCPServerError(f"Internal Server Error: {str(e)}"), 
                correlation_id
            )
        finally:
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.log("debug", f"Request processed in {duration:.4f}s", correlation_id=correlation_id)

    # --- Internal Helpers ---

    async def _authenticate_client(self, api_key: str) -> bool:
        """Verify API key using security manager if available"""
        if self.security:
            # Implement actual security check here using self.security.verify_api_key(api_key)
            # For now returning True as stub or placeholder logic
            return True 
        
        # Simple env-based check fallback
        if self.config and self.config.env.get("MCP_API_KEY"):
            return api_key == self.config.env.get("MCP_API_KEY")
        
        return True # Default open if no security config (Dev mode)

    def _create_error_response(self, error: MCPServerError, correlation_id: str) -> MCPMessage:
        """Create a standardized error message response"""
        header = MCPMessageHeader(
            message_type=MessageType.ERROR,
            source=self.name,
            correlation_id=correlation_id
        )
        
        body = {
            "error_code": error.code,
            "message": error.message,
            "details": error.details
        }
        
        return MCPMessage(header=header, body=body)
