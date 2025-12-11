
import pytest
import pytest_asyncio
import asyncio
import os
import shutil
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

# Import actual components
from shared.core_functions.config import Config
from shared.core_functions.logger import get_logger, TrivyaLogger
from shared.core_functions.security import TrivyaSecurity as SecurityManager
from mcp_servers.base_server import BaseMCPServer, MCPMessage, MCPMessageHeader, MessageType

# --- integration setup ---

TEST_LOG_DIR = "tests/integration/logs"
TEST_ENV_FILE = ".env.test"

@pytest.fixture(scope="session")
def test_env():
    """Setup test environment variables"""
    from cryptography.fernet import Fernet
    # Backup original env if needed or just set for process
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["LOG_OUTPUT"] = "file"
    os.environ["LOG_FILE_PATH"] = f"{TEST_LOG_DIR}/integration_test.log"
    os.environ["JWT_SECRET_KEY"] = "test_secret_key"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
    
    yield
    
    # Cleanup env (optional, OS env is process bound)
    pass

@pytest.fixture(scope="session")
def setup_logging(test_env):
    """Ensure log directory exists"""
    Path(TEST_LOG_DIR).mkdir(parents=True, exist_ok=True)
    yield
    # Cleanup logs after session
    try:
        shutil.rmtree(TEST_LOG_DIR)
    except Exception:
        pass

@pytest.fixture
def real_config(test_env):
    """Return a real Config object"""
    return Config()

@pytest.fixture
def real_security(real_config):
    """Return a real SecurityManager"""
    return SecurityManager(real_config)

# --- Concrete Server for Integration ---

class IntegrationMCPServer(BaseMCPServer):
    """Concrete implementation for integration testing"""
    def __init__(self, name, config):
        super().__init__(name, config)
        self.received_messages = []

    async def handle_request(self, request: MCPMessage):
        self.received_messages.append(request)
        if request.body.get("action") == "secure_echo":
            # Simulate security usage
            token = self.security.generate_jwt_token(user_id="integration_user")
            return {"echo": request.body, "token": token}
        if request.body.get("action") == "log_test":
             self.log("info", "Logging integration test message")
             return {"status": "logged"}
        return {"status": "processed"}

    async def validate_request(self, request: MCPMessage):
        if "invalid" in request.body:
            return False
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

@pytest_asyncio.fixture
async def integration_server(real_config, setup_logging):
    """Create and start an integration server"""
    server = IntegrationMCPServer("integration_test_server", real_config)
    await server.start()
    yield server
    await server.stop()

# --- Integration Tests ---

@pytest.mark.asyncio
async def test_configuration_loading(integration_server):
    """Test that the server loads configuration correctly"""
    assert integration_server.config is not None
    # Verify a value from our test_env fixture
    assert integration_server.config.env.get("JWT_SECRET_KEY") == "test_secret_key"

@pytest.mark.asyncio
async def test_logging_integration(integration_server):
    """Test that the server writes to the real log file"""
    # Trigger a log
    msg = {
        "header": {
            "message_type": "request",
            "source": "tester",
            "message_id": "log1",
            "correlation_id": "log_corr_1",
            "timestamp": datetime.utcnow().isoformat()
        },
        "body": {"action": "log_test"}
    }
    await integration_server.process_message(msg)
    
    # Check log file content
    log_file = Path(f"{TEST_LOG_DIR}/integration_test.log")
    assert log_file.exists()
    content = log_file.read_text()
    assert "Logging integration test message" in content
    assert "integration_test_server" in content

@pytest.mark.asyncio
async def test_security_integration(integration_server):
    """Test that the server uses the real SecurityManager"""
    assert integration_server.security is not None
    
    msg = {
        "header": {
            "message_type": "request",
            "source": "tester",
             "message_id": "sec1",
             "correlation_id": "sec_corr_1",
             "timestamp": datetime.utcnow().isoformat()
        },
        "body": {"action": "secure_echo"}
    }
    
    response = await integration_server.process_message(msg)
    
    assert response.body["token"] is not None
    # Validation using the security manager directly to confirm it works
    is_valid, payload, _ = integration_server.security.validate_jwt_token(response.body["token"])
    assert is_valid
    assert payload["user_id"] == "integration_user"

@pytest.mark.asyncio
async def test_full_request_response_cycle(integration_server):
    """Test a full request/response cycle with proper message formatting"""
    correlation_id = "cycle_123"
    msg = {
        "header": {
            "message_type": "request",
            "source": "client_a",
            "message_id": "msg_1",
            "correlation_id": correlation_id,
            "timestamp": datetime.utcnow().isoformat()
        },
        "body": {"action": "ping"}
    }
    
    response = await integration_server.process_message(msg)
    
    assert response.header.message_type == MessageType.RESPONSE
    assert response.header.correlation_id == correlation_id
    assert response.header.source == "integration_test_server"
    assert response.body["status"] == "processed"

@pytest.mark.asyncio
async def test_connection_lifecycle(integration_server):
    """Test connection management"""
    conn_id = "conn_integration"
    data = {"ip": "127.0.0.1", "device": "test_device"}
    
    # Connect
    await integration_server.connect(conn_id, data)
    assert conn_id in integration_server._active_connections
    assert integration_server._active_connections[conn_id]["info"]["ip"] == "127.0.0.1"
    
    # Disconnect
    await integration_server.disconnect(conn_id)
    assert conn_id not in integration_server._active_connections
