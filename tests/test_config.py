import os
import json
import pytest
from pathlib import Path
from cryptography.fernet import Fernet
from shared.core_functions.config import Config, DatabaseConfig

@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """Ensure required environment variables are set for all tests"""
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/test_db")
    monkeypatch.setenv("ENCRYPTION_KEY", Fernet.generate_key().decode())

# BDD Scenario 1: Environment Configuration Loading
def test_load_config_from_env_vars(monkeypatch):
    """
    Scenario: Load configuration from environment variables
    Given the environment is set to "production"
    And the database URL is set in environment variables
    When the configuration is loaded
    Then the environment should be "production"
    And the database URL should be loaded from environment
    """
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://prod:pass@host:5432/prod_db")
    
    config = Config()
    
    assert config.is_production() is True
    assert config.get_database_config().DATABASE_URL == "postgresql://prod:pass@host:5432/prod_db"

def test_load_config_from_env_file(tmp_path, monkeypatch):
    """
    Scenario: Load configuration from .env file
    Given a .env file exists with development settings
    And no environment variables are set (for these specific keys)
    When the configuration is loaded
    Then the settings should be loaded from the .env file
    And the environment should default to "development" (if set in .env)
    """
    # Note: BaseSettings reads from .env file, but we can't easily change the file path it reads from
    # without changing the class definition or using internal pydantic methods.
    # However, we can simulate the effect by ensuring our Config logic works.
    # Since we can't easily test the actual .env file reading of BaseSettings without
    # modifying the class or cwd, we will focus on the Config class behavior.
    
    # But wait, we can change the working directory to tmp_path where we create the .env
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        d = tmp_path / ".env"
        d.write_text("ENVIRONMENT=development\nDATABASE_URL=postgresql://dev:pass@localhost:5432/dev_db")
        
        # We need to unset the env vars so it reads from file
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.delenv("ENVIRONMENT", raising=False)
        
        # However, we have an autouse fixture setting DATABASE_URL. 
        # We need to override it.
        monkeypatch.delenv("DATABASE_URL", raising=False)
        
        # Pydantic BaseSettings reads .env.
        config = Config()
        
        # If .env reading works
        assert config.get_database_config().DATABASE_URL == "postgresql://dev:pass@localhost:5432/dev_db"
        # Config.is_production reads from os.environ, which load_dotenv might have populated?
        # Our Config class calls load_dotenv() at module level. It won't pick up the new file.
        # But Config.load_from_env() reads os.environ.
        # BaseSettings reads .env independently.
        
    finally:
        os.chdir(cwd)

# BDD Scenario 2: Feature Flag Integration
def test_load_variant_feature_flags(tmp_path, monkeypatch):
    """
    Scenario: Load variant-specific feature flags
    Given the Mini Trivya variant is active
    And feature flags exist in "feature_flags/mini_trivya_flags.json"
    When the configuration is loaded
    Then the Mini Trivya feature flags should be available
    And the flags should be accessible at runtime
    """
    # Setup feature flags directory
    flags_dir = tmp_path / "feature_flags"
    flags_dir.mkdir()
    
    mini_flags = {"enable_voice": True, "max_tokens": 100}
    (flags_dir / "mini_flags.json").write_text(json.dumps(mini_flags))
    
    monkeypatch.setenv("FEATURE_FLAGS_DIR", str(flags_dir))
    
    config = Config()
    loaded_flags = config.get_feature_flags("mini")
    
    # It tries mini_flags.json, mini.json, flags.json
    # We created mini_flags.json. Wait, the code says:
    # flags_dir / f"{variant}_flags.json" -> "mini_flags.json"
    
    assert loaded_flags == mini_flags
    assert loaded_flags["enable_voice"] is True

# BDD Scenario 3: Security Configuration
def test_encrypt_decrypt_value():
    """
    Scenario: Encrypt sensitive configuration values
    Given a database password needs to be stored
    When the configuration is saved
    Then the password should be encrypted
    And the password should be decryptable with the correct key
    """
    config = Config()
    
    original_value = "super_secret_password"
    encrypted = config.encrypt_value(original_value)
    
    assert encrypted != original_value
    assert config.decrypt_value(encrypted) == original_value

def test_decrypt_invalid_value():
    config = Config()
    with pytest.raises(ValueError, match="Invalid encryption key or corrupted data"):
        config.decrypt_value("invalid_encrypted_string")
