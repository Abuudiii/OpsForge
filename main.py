"""
Main API Client Manager

This module provides a unified interface for interacting with multiple AI APIs:
- Groq
- Perplexity Sonar
- Azure OpenAI
"""

import logging
from typing import Optional, Dict, Any, List
from api_clients.groq import GroqClient
from api_clients.perplexity import PerplexityClient
from api_clients.openai_azure import AzureOpenAIClient
from config.config import Config
from utils.logger import setup_logger

# Set up logging
logger = setup_logger(
    name="api_manager",
    level=Config.LOG_LEVEL,
    log_file=Config.LOG_FILE,
    format_string=Config.LOG_FORMAT
)


class APIManager:
    """Unified manager for all API clients"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize API Manager
        
        Args:
            config_file: Optional path to configuration file
        """
        self.groq_client: Optional[GroqClient] = None
        self.perplexity_client: Optional[PerplexityClient] = None
        self.azure_client: Optional[AzureOpenAIClient] = None
        
        # Load configuration
        if config_file:
            self.config = Config.load_from_file(config_file)
        else:
            self.config = Config.get_all_configs()
        
        logger.info("API Manager initialized")
    
    def initialize_groq(self, **kwargs) -> GroqClient:
        """
        Initialize Groq client
        
        Args:
            **kwargs: Override configuration parameters
            
        Returns:
            Initialized Groq client
        """
        config = self.config.get('groq', {})
        config.update(kwargs)
        
        if not config.get('api_key'):
            raise ValueError("Groq API key not provided")
        
        self.groq_client = GroqClient(**config)
        logger.info("Groq client initialized")
        return self.groq_client
    
    def initialize_perplexity(self, **kwargs) -> PerplexityClient:
        """
        Initialize Perplexity client
        
        Args:
            **kwargs: Override configuration parameters
            
        Returns:
            Initialized Perplexity client
        """
        config = self.config.get('perplexity', {})
        config.update(kwargs)
        
        if not config.get('api_key'):
            raise ValueError("Perplexity API key not provided")
        
        self.perplexity_client = PerplexityClient(**config)
        logger.info("Perplexity client initialized")
        return self.perplexity_client
    
    def initialize_azure_openai(self, **kwargs) -> AzureOpenAIClient:
        """
        Initialize Azure OpenAI client
        
        Args:
            **kwargs: Override configuration parameters
            
        Returns:
            Initialized Azure OpenAI client
        """
        config = self.config.get('azure_openai', {})
        config.update(kwargs)
        
        if not (config.get('api_key') or config.get('azure_ad_token')):
            raise ValueError("Azure OpenAI authentication not provided")
        
        if not config.get('azure_endpoint'):
            raise ValueError("Azure OpenAI endpoint not provided")
        
        self.azure_client = AzureOpenAIClient(**config)
        logger.info("Azure OpenAI client initialized")
        return self.azure_client
    
    def initialize_all(self):
        """Initialize all available API clients"""
        initialized = []
        
        # Try to initialize each client
        try:
            if Config.validate_config('groq'):
                self.initialize_groq()
                initialized.append('Groq')
        except Exception as e:
            logger.warning(f"Failed to initialize Groq: {e}")
        
        try:
            if Config.validate_config('perplexity'):
                self.initialize_perplexity()
                initialized.append('Perplexity')
        except Exception as e:
            logger.warning(f"Failed to initialize Perplexity: {e}")
        
        try:
            if Config.validate_config('azure_openai'):
                self.initialize_azure_openai()
                initialized.append('Azure OpenAI')
        except Exception as e:
            logger.warning(f"Failed to initialize Azure OpenAI: {e}")
        
        logger.info(f"Initialized clients: {', '.join(initialized)}")
        return initialized
    
    def test_connections(self) -> Dict[str, bool]:
        """
        Test all initialized API connections
        
        Returns:
            Dictionary with connection status for each client
        """
        results = {}
        
        if self.groq_client:
            try:
                results['groq'] = self.groq_client.validate_connection()
            except Exception as e:
                logger.error(f"Groq connection test failed: {e}")
                results['groq'] = False
        
        if self.perplexity_client:
            try:
                results['perplexity'] = self.perplexity_client.validate_connection()
            except Exception as e:
                logger.error(f"Perplexity connection test failed: {e}")
                results['perplexity'] = False
        
        if self.azure_client:
            try:
                results['azure_openai'] = self.azure_client.validate_connection()
            except Exception as e:
                logger.error(f"Azure OpenAI connection test failed: {e}")
                results['azure_openai'] = False
        
        return results
    
    def close_all(self):
        """Close all client connections"""
        if self.groq_client:
            self.groq_client.close()
        if self.perplexity_client:
            self.perplexity_client.close()
        if self.azure_client:
            self.azure_client.close()
        logger.info("All client connections closed")


# Example usage functions
def example_groq_usage():
    """Example of using Groq API"""
    manager = APIManager()
    
    # Initialize Groq client
    groq = manager.initialize_groq()
    
    # Simple completion
    response = groq.simple_completion(
        prompt="Explain quantum computing in simple terms",
        temperature=0.7,
        max_tokens=200
    )
    
    print("Groq Response:", response)
    
    # Clean up
    manager.close_all()


def example_perplexity_usage():
    """Example of using Perplexity API"""
    manager = APIManager()
    
    # Initialize Perplexity client
    perplexity = manager.initialize_perplexity()
    
    # Web search
    response = perplexity.simple_search(
        query="What are the latest developments in AI?",
    )
    
    print("Perplexity Response:", response)
    
    # Research a topic
    research = perplexity.research_topic(
        topic="Quantum Computing",
        questions=[
            "What are the current applications?",
            "What companies are leading the field?",
            "What are the main challenges?"
        ]
    )
    
    print("Research Response:", research)
    
    # Clean up
    manager.close_all()


def example_azure_openai_usage():
    """Example of using Azure OpenAI API"""
    manager = APIManager()
    
    # Initialize Azure OpenAI client
    azure = manager.initialize_azure_openai()
    
    # Simple completion
    response = azure.simple_completion(
        prompt="Write a haiku about technology",
        deployment_name="gpt-4",  # Specify your deployment
        temperature=0.9,
        max_tokens=50
    )
    
    print("Azure OpenAI Response:", response)
    
    # JSON response
    json_response = azure.create_json_response(
        prompt="List 3 benefits of cloud computing",
        deployment_name="gpt-4"
    )
    
    print("JSON Response:", json_response)
    
    # Clean up
    manager.close_all()


def example_multi_api_usage():
    """Example of using multiple APIs together"""
    manager = APIManager()
    
    # Initialize all available clients
    initialized = manager.initialize_all()
    print(f"Initialized: {initialized}")
    
    # Test connections
    connection_status = manager.test_connections()
    print(f"Connection Status: {connection_status}")
    
    prompt = "What is machine learning?"
    
    # Get responses from all available APIs
    responses = {}
    
    if manager.groq_client and connection_status.get('groq'):
        try:
            responses['groq'] = manager.groq_client.simple_completion(prompt, max_tokens=100)
        except Exception as e:
            logger.error(f"Groq request failed: {e}")
    
    if manager.perplexity_client and connection_status.get('perplexity'):
        try:
            responses['perplexity'] = manager.perplexity_client.simple_search(prompt)
        except Exception as e:
            logger.error(f"Perplexity request failed: {e}")
    
    if manager.azure_client and connection_status.get('azure_openai'):
        try:
            responses['azure'] = manager.azure_client.simple_completion(prompt, max_tokens=100)
        except Exception as e:
            logger.error(f"Azure request failed: {e}")
    
    # Display all responses
    for api, response in responses.items():
        print(f"\n{api.upper()} Response:")
        print(response[:200] + "..." if len(response) > 200 else response)
    
    # Clean up
    manager.close_all()


if __name__ == "__main__":
    print("API Client Manager - Example Usage")
    print("=" * 50)
    
    # Uncomment the example you want to run:
    
    # example_groq_usage()
    # example_perplexity_usage()
    # example_azure_openai_usage()
    # example_multi_api_usage()
    
    print("\nTo use the API clients:")
    print("1. Copy config/.env.example to config/.env")
    print("2. Fill in your API keys in the .env file")
    print("3. Uncomment one of the example functions above")
    print("4. Run: python main.py")