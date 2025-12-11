
import sys
import os

print("Starting debug script...", flush=True)

try:
    print("Importing shared.core_functions.config...", flush=True)
    from shared.core_functions.config import Config
    print("Config imported.", flush=True)

    print("Importing shared.core_functions.logger...", flush=True)
    from shared.core_functions.logger import get_logger
    print("Logger imported.", flush=True)

    print("Importing shared.core_functions.security...", flush=True)
    from shared.core_functions.security import SecurityManager
    print("Security imported.", flush=True)

    print("Importing mcp_servers.base_server...", flush=True)
    from mcp_servers.base_server import BaseMCPServer
    print("BaseMCPServer imported.", flush=True)

    print("All imports successful.", flush=True)

except Exception as e:
    print(f"IMPORT ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()

import pytest
print(f"Pytest version: {pytest.__version__}", flush=True)
