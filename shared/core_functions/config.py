"""
Central Configuration Management System for Trivya Platform

This module provides a centralized, validated, and secure configuration system
for all Trivya variants and shared components.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from cryptography.fernet import Fernet
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DatabaseConfig(BaseSettings):
    """Database configuration schema"""
    DATABASE_URL: str = Field(...)
    REDIS_URL: str = Field(default="redis://localhost:6379")
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class APIConfig(BaseSettings):
    """API configuration schema"""
    API_KEY: Optional[str] = Field(default=None)
    TIMEOUT: int = Field(default=30, validation_alias="API_TIMEOUT")
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class FeatureFlagConfig(BaseSettings):
    """Feature flag configuration schema"""
    FEATURE_FLAGS_DIR: str = Field(default="feature_flags")
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class LoggingConfig(BaseSettings):
    """Logging configuration schema"""
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="json")
    LOG_OUTPUT: str = Field(default="console")
    LOG_FILE_PATH: str = Field(default="logs/trivya.log")
    LOG_MAX_FILE_SIZE: str = Field(default="10MB")
    LOG_BACKUP_COUNT: int = Field(default=5, ge=1, le=50)
    LOG_CORRELATION_TRACKING: bool = Field(default=True)
    LOG_PERFORMANCE_MONITORING: bool = Field(default=True)
    LOG_SANITIZE_SENSITIVE_DATA: bool = Field(default=True)
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of: {valid_levels}")
        return v.upper()
    
    @field_validator('LOG_FORMAT')
    @classmethod
    def validate_log_format(cls, v):
        """Validate log format"""
        valid_formats = ['json', 'text']
        if v.lower() not in valid_formats:
            raise ValueError(f"LOG_FORMAT must be one of: {valid_formats}")
        return v.lower()
    
    @field_validator('LOG_OUTPUT')
    @classmethod
    def validate_log_output(cls, v):
        """Validate log output"""
        valid_outputs = ['console', 'file', 'both']
        if v.lower() not in valid_outputs:
            raise ValueError(f"LOG_OUTPUT must be one of: {valid_outputs}")
        return v.lower()

class VectorDBConfig(BaseSettings):
    """Vector Database configuration schema"""
    VECTOR_DB_TYPE: str = Field(default="chromadb")
    VECTOR_DB_PATH: str = Field(default="./data/chroma")
    COLLECTION_NAME: str = Field(default="trivya_kb")
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class Config:
    """Main configuration class"""
    
    def __init__(self):
        """Initialize configuration"""
        self.env = self.load_from_env()
        self.encryption_key = os.getenv("ENCRYPTION_KEY")
        if not self.encryption_key:
            # Generate a key if not provided (Note: This is for dev/demo, in prod it should be persistent)
            self.encryption_key = Fernet.generate_key().decode()
        self.fernet = Fernet(self.encryption_key.encode() if isinstance(self.encryption_key, str) else self.encryption_key)
        
        # We need to ensure required env vars are present or handle errors
        # Pydantic will raise ValidationError if required fields are missing
        self.database_config = DatabaseConfig()
        self.api_config = APIConfig()
        self.feature_flag_config = FeatureFlagConfig()
        self.logging_config = LoggingConfig()
        self.vector_db_config = VectorDBConfig()

    def load_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        return dict(os.environ)

    def load_from_file(self, file_path: str) -> Dict[str, Any]:
        """Load configuration from file"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
            
        with open(path, 'r') as f:
            if path.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f) or {}
            elif path.suffix == '.json':
                return json.load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {path.suffix}")

    def get_feature_flags(self, variant: str) -> Dict[str, bool]:
        """Get feature flags for specific variant"""
        flags_dir = Path(self.feature_flag_config.FEATURE_FLAGS_DIR)
        # Try different naming conventions
        possible_files = [
            flags_dir / f"{variant}_flags.json",
            flags_dir / f"{variant}.json",
            flags_dir / "flags.json" # Fallback
        ]
        
        for file_path in possible_files:
            if file_path.exists():
                try:
                    return self.load_from_file(str(file_path))
                except Exception as e:
                    print(f"Error loading flags from {file_path}: {e}")
                    continue
                    
        return {}

    def encrypt_value(self, value: str) -> str:
        """Encrypt sensitive configuration value"""
        if not value:
            return ""
        return self.fernet.encrypt(value.encode()).decode()

    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt sensitive configuration value"""
        if not encrypted_value:
            return ""
        try:
            return self.fernet.decrypt(encrypted_value.encode()).decode()
        except Exception:
            raise ValueError("Invalid encryption key or corrupted data")

    def is_production(self) -> bool:
        return self.env.get("ENVIRONMENT", "development").lower() == "production"

    def get_database_config(self) -> DatabaseConfig:
        return self.database_config

    def get_api_config(self) -> APIConfig:
        return self.api_config