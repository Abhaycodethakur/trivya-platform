import os
import pytest
from shared.core_functions.config import Config

def test_full_configuration_lifecycle(tmp_path, monkeypatch):
    """
    Integration test simulating a full configuration lifecycle:
    1. Setup environment variables (simulating production)
    2. Initialize Config
    3. Verify critical settings
    4. Test security (encryption/decryption)
    5. Test feature flags
    """
    # 1. Setup Environment
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://prod_user:prod_pass@db.trivya.com:5432/trivya_prod")
    monkeypatch.setenv("API_KEY", "prod_api_key_12345")
    monkeypatch.setenv("FEATURE_FLAGS_DIR", str(tmp_path / "flags"))
    
    # Setup feature flags file
    flags_dir = tmp_path / "flags"
    flags_dir.mkdir()
    with open(flags_dir / "production_flags.json", "w") as f:
        f.write('{"new_ui": true, "beta_features": false}')

    # 2. Initialize Config
    config = Config()

    # 3. Verify Critical Settings
    assert config.is_production() is True
    assert config.get_database_config().DATABASE_URL == "postgresql://prod_user:prod_pass@db.trivya.com:5432/trivya_prod"
    assert config.get_api_config().API_KEY == "prod_api_key_12345"

    # 4. Test Security
    secret_data = "user_credit_card_token"
    encrypted = config.encrypt_value(secret_data)
    assert encrypted != secret_data
    decrypted = config.decrypt_value(encrypted)
    assert decrypted == secret_data

    # 5. Test Feature Flags
    # The new config looks for "{variant}_flags.json"
    flags = config.get_feature_flags("production")
    assert flags["new_ui"] is True
    assert flags["beta_features"] is False

    print("\nIntegration Test Passed: Full Configuration Lifecycle Verified")
