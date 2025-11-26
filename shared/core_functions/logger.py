"""
Centralized Logging System for Trivya Platform

This module provides structured, scalable logging across the entire Trivya platform
with support for correlation tracking, performance monitoring, and security compliance.
"""

import logging
import json
import uuid
import time
import traceback
import sys
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger

# Import config (will be used for configuration)
try:
    from shared.core_functions.config import Config
except ImportError:
    Config = None


class SensitiveDataFilter(logging.Filter):
    """Filter to sanitize sensitive data from log records"""
    
    SENSITIVE_FIELDS = {
        'password', 'token', 'api_key', 'secret', 'credit_card',
        'ssn', 'social_security', 'auth_token', 'bearer', 'jwt'
    }
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Sanitize sensitive data from log record"""
        if hasattr(record, 'msg') and isinstance(record.msg, dict):
            record.msg = self._sanitize_dict(record.msg)
        return True
    
    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize dictionary"""
        sanitized = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in self.SENSITIVE_FIELDS):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        return sanitized


class CorrelationIdFilter(logging.Filter):
    """Filter to add correlation ID to log records"""
    
    def __init__(self, correlation_id: Optional[str] = None):
        super().__init__()
        self.correlation_id = correlation_id or str(uuid.uuid4())
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add correlation ID to log record"""
        record.correlation_id = self.correlation_id
        return True


class TrivyaLogger:
    """Main logging class for Trivya platform"""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize logger with configuration"""
        self.config = config
        self._loggers: Dict[str, logging.Logger] = {}
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        import os
        
        # Get configuration from LoggingConfig or environment variables
        if self.config and hasattr(self.config, 'logging_config'):
            log_config = self.config.logging_config
            log_level = log_config.LOG_LEVEL
            log_format = log_config.LOG_FORMAT
            log_output = log_config.LOG_OUTPUT
            log_file_path = log_config.LOG_FILE_PATH
        elif self.config:
            # Fallback to env dict for backward compatibility
            log_level = self.config.env.get('LOG_LEVEL', 'INFO')
            log_format = self.config.env.get('LOG_FORMAT', 'json')
            log_output = self.config.env.get('LOG_OUTPUT', 'console')
            log_file_path = self.config.env.get('LOG_FILE_PATH', 'logs/trivya.log')
        else:
            # Read directly from os.environ for testing
            log_level = os.environ.get('LOG_LEVEL', 'INFO')
            log_format = os.environ.get('LOG_FORMAT', 'json')
            log_output = os.environ.get('LOG_OUTPUT', 'console')
            log_file_path = os.environ.get('LOG_FILE_PATH', 'logs/trivya.log')
        
        # Convert string log level to logging constant
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        
        # Setup root logger
        root_logger = logging.getLogger('trivya')
        root_logger.setLevel(numeric_level)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Setup formatters
        if log_format == 'json':
            formatter = jsonlogger.JsonFormatter(
                '%(timestamp)s %(level)s %(name)s %(message)s %(correlation_id)s'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        # Setup handlers based on output configuration
        if log_output in ['console', 'both']:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            console_handler.addFilter(SensitiveDataFilter())
            root_logger.addHandler(console_handler)
        
        if log_output in ['file', 'both']:
            # Create log directory if it doesn't exist
            log_path = Path(log_file_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Setup rotating file handler
            file_handler = RotatingFileHandler(
                log_file_path,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setFormatter(formatter)
            file_handler.addFilter(SensitiveDataFilter())
            root_logger.addHandler(file_handler)
    
    def get_logger(self, component: str) -> logging.Logger:
        """Get logger for specific component"""
        if component not in self._loggers:
            logger = logging.getLogger(f'trivya.{component}')
            self._loggers[component] = logger
        return self._loggers[component]
    
    def create_correlation_id(self) -> str:
        """Generate unique correlation ID for request tracking"""
        return f"req_{uuid.uuid4().hex[:16]}"
    
    def log_agent_action(
        self,
        agent_id: str,
        action: str,
        correlation_id: Optional[str] = None,
        **kwargs
    ):
        """Log AI agent action with context"""
        logger = self.get_logger('agent')
        
        log_data = {
            'agent_id': agent_id,
            'action': action,
            'correlation_id': correlation_id or self.create_correlation_id(),
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        # Sanitize sensitive data
        log_data = self.sanitize_log_data(log_data)
        
        logger.info(json.dumps(log_data))
    
    def log_workflow_step(
        self,
        workflow_id: str,
        step: str,
        correlation_id: Optional[str] = None,
        **kwargs
    ):
        """Log workflow execution step"""
        logger = self.get_logger('workflow')
        
        log_data = {
            'workflow_id': workflow_id,
            'step': step,
            'correlation_id': correlation_id or self.create_correlation_id(),
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        # Sanitize sensitive data
        log_data = self.sanitize_log_data(log_data)
        
        logger.info(json.dumps(log_data))
    
    def log_performance(
        self,
        component: str,
        metric: str,
        value: float,
        correlation_id: Optional[str] = None,
        **kwargs
    ):
        """Log performance metric"""
        logger = self.get_logger('performance')
        
        log_data = {
            'component': component,
            'metric': metric,
            'value': value,
            'correlation_id': correlation_id,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        logger.info(json.dumps(log_data))
    
    def log_error(
        self,
        component: str,
        error: Exception,
        correlation_id: Optional[str] = None,
        **kwargs
    ):
        """Log error with traceback"""
        logger = self.get_logger('error')
        
        log_data = {
            'component': component,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'correlation_id': correlation_id or self.create_correlation_id(),
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        # Sanitize sensitive data
        log_data = self.sanitize_log_data(log_data)
        
        logger.error(json.dumps(log_data))
    
    def sanitize_log_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from log entries"""
        sensitive_filter = SensitiveDataFilter()
        return sensitive_filter._sanitize_dict(data)
    
    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for all subsequent logs"""
        for logger in self._loggers.values():
            # Remove existing correlation filters
            logger.filters = [f for f in logger.filters if not isinstance(f, CorrelationIdFilter)]
            # Add new correlation filter
            logger.addFilter(CorrelationIdFilter(correlation_id))


class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self, logger: TrivyaLogger, component: str, operation: str, correlation_id: Optional[str] = None):
        self.logger = logger
        self.component = component
        self.operation = operation
        self.correlation_id = correlation_id
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = time.time() - self.start_time
        self.logger.log_performance(
            component=self.component,
            metric=f"{self.operation}_execution_time",
            value=execution_time,
            correlation_id=self.correlation_id
        )


# Singleton instance
_logger_instance: Optional[TrivyaLogger] = None


def get_logger(config: Optional[Config] = None) -> TrivyaLogger:
    """Get singleton logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = TrivyaLogger(config)
    return _logger_instance


# Export public API
__all__ = [
    'TrivyaLogger',
    'PerformanceTimer',
    'get_logger',
    'SensitiveDataFilter',
    'CorrelationIdFilter',
]
