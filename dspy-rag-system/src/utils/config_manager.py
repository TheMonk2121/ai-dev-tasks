"""
Configuration Manager

Handles configuration loading with hot-reload support and environment variable overrides.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages system configuration with hot-reload support"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), '..', '..', 'config', 'system.json'
        )
        self._config_cache = None
        self._last_modified = 0
    
    def load_config(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        Load configuration with caching and hot-reload support.
        
        Args:
            force_reload: Force reload even if file hasn't changed
            
        Returns:
            Configuration dictionary
        """
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            return self._get_default_config()
        
        # Check if file has been modified
        current_mtime = config_file.stat().st_mtime
        if not force_reload and self._config_cache and current_mtime <= self._last_modified:
            return self._config_cache
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Apply environment variable overrides
            config = self._apply_env_overrides(config)
            
            self._config_cache = config
            self._last_modified = current_mtime
            
            logger.info(f"Configuration loaded from {self.config_path}")
            return config
            
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration"""
        
        # Security configuration overrides
        if 'security' not in config:
            config['security'] = {}
        
        # File size limit override
        env_max_size = os.getenv('SECURITY_MAX_FILE_MB')
        if env_max_size:
            try:
                max_size = int(env_max_size)
                if 'file_validation' not in config['security']:
                    config['security']['file_validation'] = {}
                config['security']['file_validation']['max_size_mb'] = max_size
                logger.info(f"File size limit overridden to {max_size}MB via SECURITY_MAX_FILE_MB")
            except ValueError:
                logger.warning(f"Invalid SECURITY_MAX_FILE_MB value: {env_max_size}")
        
        # LLM timeout override
        env_llm_timeout = os.getenv('LLM_TIMEOUT_SEC')
        if env_llm_timeout:
            try:
                llm_timeout = int(env_llm_timeout)
                if 'error_policy' not in config:
                    config['error_policy'] = {}
                config['error_policy']['llm_timeout_seconds'] = llm_timeout
                logger.info(f"LLM timeout overridden to {llm_timeout}s via LLM_TIMEOUT_SEC")
            except ValueError:
                logger.warning(f"Invalid LLM_TIMEOUT_SEC value: {env_llm_timeout}")
        
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration when config file is not available"""
        return {
            "version": "0.3.1",
            "error_policy": {
                "retry_max": 3,
                "retry_backoff_secs": 1,
                "timeout_seconds": 30,
                "llm_timeout_seconds": 90,
                "fatal_errors": ["ResourceBusyError", "AuthenticationError"]
            },
            "security": {
                "prompt_blocklist": ["{{", "}}", "<script>"],
                "prompt_whitelist": ["<b>", "<i>"],
                "file_validation": {
                    "max_size_mb": 50,
                    "allowed_ext": ["txt", "md", "pdf", "csv"]
                }
            }
        }
    
    def reload_config(self) -> Dict[str, Any]:
        """Force reload configuration"""
        return self.load_config(force_reload=True)
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration with overrides"""
        config = self.load_config()
        return config.get('security', {})
    
    def get_error_policy(self) -> Dict[str, Any]:
        """Get error policy configuration with overrides"""
        config = self.load_config()
        return config.get('error_policy', {})

# Global config manager instance
config_manager = ConfigManager()

def get_config() -> Dict[str, Any]:
    """Get current configuration"""
    return config_manager.load_config()

def reload_config() -> Dict[str, Any]:
    """Reload configuration"""
    return config_manager.reload_config()

def get_security_config() -> Dict[str, Any]:
    """Get security configuration"""
    return config_manager.get_security_config()

def get_error_policy() -> Dict[str, Any]:
    """Get error policy configuration"""
    return config_manager.get_error_policy() 