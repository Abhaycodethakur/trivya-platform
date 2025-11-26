#!/usr/bin/env python3
"""
Test runner for security.py module
"""

import os
import sys
import subprocess
from pathlib import Path

# Set environment variables for testing
os.environ["JWT_SECRET_KEY"] = "test_jwt_secret_key_for_development_only"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["JWT_REFRESH_TOKEN_EXPIRE_DAYS"] = "7"

# Generate a valid Fernet key for testing
from cryptography.fernet import Fernet
test_key = Fernet.generate_key().decode()
os.environ["ENCRYPTION_KEY"] = test_key

os.environ["PASSWORD_MIN_LENGTH"] = "8"
os.environ["PASSWORD_REQUIRE_UPPERCASE"] = "true"
os.environ["PASSWORD_REQUIRE_LOWERCASE"] = "true"
os.environ["PASSWORD_REQUIRE_DIGITS"] = "true"
os.environ["PASSWORD_REQUIRE_SPECIAL"] = "true"
os.environ["RATE_LIMIT_ENABLED"] = "true"
os.environ["RATE_LIMIT_PER_MINUTE"] = "60"
os.environ["RATE_LIMIT_PER_HOUR"] = "1000"

def main():
    """Run security tests"""
    print("=" * 60)
    print("Running Security Module Tests")
    print("=" * 60)
    
    # Run pytest with the test file
    test_file = "tests/test_security.py"
    
    # Check if test file exists
    if not Path(test_file).exists():
        print(f"Error: Test file {test_file} not found!")
        print("Make sure you've created the test file in the tests directory.")
        return 1
    
    # Run pytest
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_file, "-v"],
        capture_output=True,
        text=True
    )
    
    # Print output
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    # Return exit code
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
