"""
Configuration management for API clients
"""

import os
import json
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)


class Config:
    """Configuration manager for API clients"""
    
    # Groq Configuration
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_BASE_URL = os.getenv('GROQ_BASE_URL', 'https://api.groq.com/openai/v1')
    GROQ_DEFAULT_MODEL = os.getenv('GROQ_DEFAULT_MODEL', 'mixtral-8x7b-32768')
    
    # Perplexity Configuration
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
    PERPLEXITY_BASE_URL = os.getenv('PERPLEXITY_BASE_URL', 'https://api.perplexity.ai')
    PERPLEXITY_DEFAULT_MODEL = os.getenv('PERPLEXITY_DEFAULT_MODEL', 'sonar-medium-online')
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-01')
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
    AZURE_AD_TOKEN = os.getenv('AZURE_AD_TOKEN')
    
    # General API Settings
    DEFAULT_TIMEOUT = int(os.getenv('DEFAULT_TIMEOUT', '30'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY', '1'))
    RATE_LIMIT_CALLS = int(os.getenv('RATE_LIMIT_CALLS', '60'))
    RATE_LIMIT_PERIOD = int(os.getenv('RATE_LIMIT_PERIOD', '60'))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    LOG_FILE = os.getenv('LOG_FILE', 'api_clients.log')
    
    @classmethod
    def get_groq_config(cls) -> Dict[str, Any]:
        """Get Groq API configuration"""
        return {
            'api_key': cls.GROQ_API_KEY,
            'base_url': cls.GROQ_BASE_URL,
            'model': cls.GROQ_DEFAULT_MODEL,
            'timeout': cls.DEFAULT_TIMEOUT,
            'max_retries': cls.MAX_RETRIES,
            'retry_delay': cls.RETRY_DELAY,
            'rate_limit_calls': cls.RATE_LIMIT_CALLS,
            'rate_limit_period': cls.RATE_LIMIT_PERIOD
        }
    
    @classmethod
    def get_perplexity_config(cls) -> Dict[str, Any]:
        """Get Perplexity API configuration"""
        return {
            'api_key': cls.PERPLEXITY_API_KEY,
            'base_url': cls.PERPLEXITY_BASE_URL,
            'model': cls.PERPLEXITY_DEFAULT_MODEL,
            'timeout': cls.DEFAULT_TIMEOUT,
            'max_retries': cls.MAX_RETRIES,
            'retry_delay': cls.RETRY_DELAY,
            'rate_limit_calls': cls.RATE_LIMIT_CALLS,
            'rate_limit_period': cls.RATE_LIMIT_PERIOD
        }
    
    @classmethod
    def get_azure_openai_config(cls) -> Dict[str, Any]:
        """Get Azure OpenAI configuration"""
        config = {
            'api_key': cls.AZURE_OPENAI_API_KEY,
            'azure_endpoint': cls.AZURE_OPENAI_ENDPOINT,
            'api_version': cls.AZURE_OPENAI_API_VERSION,
            'deployment_name': cls.AZURE_OPENAI_DEPLOYMENT_NAME,
            'timeout': cls.DEFAULT_TIMEOUT,
            'max_retries': cls.MAX_RETRIES,
            'retry_delay': cls.RETRY_DELAY,
            'rate_limit_calls': cls.RATE_LIMIT_CALLS,
            'rate_limit_period': cls.RATE_LIMIT_PERIOD
        }
        
        if cls.AZURE_AD_TOKEN:
            config['azure_ad_token'] = cls.AZURE_AD_TOKEN
            
        return config
    
    @classmethod
    def load_from_file(cls, config_file: str) -> Dict[str, Any]:
        """
        Load configuration from a JSON file
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        with open(config_file, 'r') as f:
            return json.load(f)
    
    @classmethod
    def save_to_file(cls, config: Dict[str, Any], config_file: str):
        """
        Save configuration to a JSON file
        
        Args:
            config: Configuration dictionary
            config_file: Path to save configuration
        """
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    @classmethod
    def validate_config(cls, service: str) -> bool:
        """
        Validate configuration for a specific service
        
        Args:
            service: Service name ('groq', 'perplexity', 'azure_openai')
            
        Returns:
            True if configuration is valid
        """
        if service.lower() == 'groq':
            return bool(cls.GROQ_API_KEY)
        elif service.lower() == 'perplexity':
            return bool(cls.PERPLEXITY_API_KEY)
        elif service.lower() == 'azure_openai':
            return bool(cls.AZURE_OPENAI_API_KEY or cls.AZURE_AD_TOKEN) and bool(cls.AZURE_OPENAI_ENDPOINT)
        else:
            return False
    
    @classmethod
    def get_all_configs(cls) -> Dict[str, Dict[str, Any]]:
        """Get all API configurations"""
        return {
            'groq': cls.get_groq_config(),
            'perplexity': cls.get_perplexity_config(),
            'azure_openai': cls.get_azure_openai_config()
        }