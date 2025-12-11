
import unittest
import asyncio
import json
from unittest.mock import MagicMock, patch
from datetime import datetime

from mcp_servers.base_server import (
    BaseMCPServer, 
    MCPMessage, 
    MCPMessageHeader, 
    MessageType,
    MCPServerError,
    MCPAuthenticationError
)

# Concrete implementation for testing
class MockMCPServer(BaseMCPServer):
    async def handle_request(self, request: MCPMessage):
        if request.body.get("action") == "fail":
            raise ValueError("Intentional failure")
        return {"status": "success", "echo": request.body}

    async def validate_request(self, request: MCPMessage):
        if request.body.get("action") == "invalid":
            raise MCPServerError("Invalid action", code="VALIDATION_ERROR")
        return True

    async def format_response(self, data, correlation_id):
        header = MCPMessageHeader(
            message_type=MessageType.RESPONSE,
            source=self.name,
            correlation_id=correlation_id
        )
        return MCPMessage(header=header, body=data)

    async def cleanup(self):
        pass

class TestBaseMCPServer(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.server = MockMCPServer(name="test_server")
        # Disable logging output during tests
        self.server._log = MagicMock()

    async def test_initialization(self):
        self.assertEqual(self.server.name, "test_server")
        self.assertFalse(self.server._is_running)

    async def test_lifecycle(self):
        await self.server.start()
        self.assertTrue(self.server._is_running)
        await self.server.stop()
        self.assertFalse(self.server._is_running)

    async def test_connection_management(self):
        conn_id = "conn_1"
        client_info = {"user_agent": "test_client"}
        
        # Test Connect
        success = await self.server.connect(conn_id, client_info)
        self.assertTrue(success)
        self.assertIn(conn_id, self.server._active_connections)
        self.assertTrue(self.server._is_running) # Should auto-start

        # Test Disconnect
        await self.server.disconnect(conn_id)
        self.assertNotIn(conn_id, self.server._active_connections)

    async def test_process_valid_message(self):
        msg_payload = {
            "header": {
                "message_type": "request",
                "source": "client",
                "message_id": "123",
                "correlation_id": "abc",
                "timestamp": datetime.utcnow().isoformat()
            },
            "body": {"action": "ping"}
        }
        
        response = await self.server.process_message(msg_payload)
        
        self.assertEqual(response.header.message_type, MessageType.RESPONSE)
        self.assertEqual(response.body["status"], "success")
        self.assertEqual(response.header.correlation_id, "abc")

    async def test_process_invalid_json_message(self):
        response = await self.server.process_message("{invalid_json}")
        self.assertEqual(response.header.message_type, MessageType.ERROR)
        self.assertIn("Invalid JSON", response.body["message"])

    async def test_validation_error(self):
        msg_payload = {
            "header": {
                "message_type": "request",
                "source": "client",
                "version": "1.0",
                "message_id": "1",
                "correlation_id": "1"
            },
            "body": {"action": "invalid"}
        }
        response = await self.server.process_message(msg_payload)
        self.assertEqual(response.header.message_type, MessageType.ERROR)
        self.assertEqual(response.body["error_code"], "VALIDATION_ERROR")

    async def test_internal_error_handling(self):
        msg_payload = {
            "header": {
                "message_type": "request",
                "source": "client",
                "version": "1.0",
                "message_id": "1",
                "correlation_id": "1"
            },
            "body": {"action": "fail"}
        }
        response = await self.server.process_message(msg_payload)
        self.assertEqual(response.header.message_type, MessageType.ERROR)
        self.assertIn("Internal Server Error", response.body["message"])

if __name__ == '__main__':
    unittest.main()
