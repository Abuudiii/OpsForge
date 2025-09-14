# AI API Client Manager

A unified Python interface for interacting with multiple AI APIs including Groq, Perplexity Sonar, and Azure OpenAI.

## Features

- **Unified Interface**: Single manager class to handle multiple AI APIs
- **Robust Error Handling**: Built-in retry logic with exponential backoff
- **Rate Limiting**: Automatic rate limit management for all APIs
- **Configuration Management**: Environment-based configuration with `.env` support
- **Logging**: Comprehensive logging for debugging and monitoring
- **Type Hints**: Full type annotation for better IDE support
- **Modular Design**: Easy to extend with new API providers

## Supported APIs

### 1. Groq
- Chat completions with various models (Mixtral, LLaMA, etc.)
- Embeddings generation
- Audio transcription (placeholder for implementation)
- Token counting utilities

### 2. Perplexity Sonar
- Web search with real-time information
- Research capabilities with citations
- Fact-checking with sources
- URL summarization
- Topic comparison and analysis

### 3. Azure OpenAI
- Chat completions (GPT-3.5, GPT-4, etc.)
- Embeddings with multiple models
- Image generation with DALL-E 3
- Image analysis with GPT-4 Vision
- Function calling support
- JSON response mode
- Content moderation

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up configuration:
```bash
cp config/.env.example config/.env
# Edit config/.env with your API keys
```

## Configuration

### Environment Variables

Create a `.env` file in the `config/` directory with your API credentials:

```env
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_DEFAULT_MODEL=mixtral-8x7b-32768

# Perplexity API Configuration
PERPLEXITY_API_KEY=your_perplexity_api_key_here
PERPLEXITY_DEFAULT_MODEL=sonar-medium-online

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
```

## Quick Start

### Basic Usage

```python
from main import APIManager

# Initialize the API manager
manager = APIManager()

# Initialize specific clients
groq = manager.initialize_groq()
perplexity = manager.initialize_perplexity()
azure = manager.initialize_azure_openai()

# Or initialize all available clients
initialized = manager.initialize_all()

# Test connections
status = manager.test_connections()
print(f"Connection status: {status}")

# Clean up when done
manager.close_all()
```

### Groq Example

```python
from api_clients.groq import GroqClient
from config.config import Config

# Get configuration
config = Config.get_groq_config()

# Initialize client
client = GroqClient(**config)

# Simple completion
response = client.simple_completion(
    prompt="Explain machine learning",
    temperature=0.7,
    max_tokens=200
)
print(response)

# With conversation context
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is Python?"}
]
response = client.create_completion(messages)
print(response['choices'][0]['message']['content'])
```

### Perplexity Example

```python
from api_clients.perplexity import PerplexityClient
from config.config import Config

# Initialize client
config = Config.get_perplexity_config()
client = PerplexityClient(**config)

# Web search
result = client.simple_search("Latest AI developments 2024")
print(result)

# Research with citations
research = client.research_topic(
    topic="Quantum Computing",
    questions=[
        "Current applications?",
        "Leading companies?",
        "Main challenges?"
    ]
)

# Get citations from response
citations = client.get_citations(research)
print(f"Found {len(citations)} citations")
```

### Azure OpenAI Example

```python
from api_clients.openai_azure import AzureOpenAIClient
from config.config import Config

# Initialize client
config = Config.get_azure_openai_config()
client = AzureOpenAIClient(**config)

# Chat completion
response = client.simple_completion(
    prompt="Write a haiku about coding",
    deployment_name="gpt-4",
    temperature=0.9
)
print(response)

# Generate embeddings
embeddings = client.create_embedding(
    input=["Hello world", "How are you?"],
    deployment_name="text-embedding-ada-002"
)

# Image generation
image_response = client.create_image(
    prompt="A futuristic city at sunset",
    deployment_name="dall-e-3",
    size="1024x1024",
    quality="hd"
)
```

## API Client Structure

```
api_clients/
├── base/
│   ├── __init__.py
│   └── base_client.py      # Abstract base class
├── groq/
│   ├── __init__.py
│   └── groq_client.py      # Groq implementation
├── perplexity/
│   ├── __init__.py
│   └── perplexity_client.py # Perplexity implementation
└── openai_azure/
    ├── __init__.py
    └── azure_openai_client.py # Azure OpenAI implementation
```

## Advanced Features

### Rate Limiting

All clients include automatic rate limiting:

```python
client = GroqClient(
    api_key="...",
    rate_limit_calls=60,  # Max calls
    rate_limit_period=60  # Period in seconds
)
```

### Retry Logic

Automatic retry with exponential backoff:

```python
client = PerplexityClient(
    api_key="...",
    max_retries=3,
    retry_delay=1  # Initial delay in seconds
)
```

### Custom Configuration

Load configuration from JSON:

```python
from config.config import Config

# Load from file
config = Config.load_from_file('custom_config.json')

# Save configuration
Config.save_to_file(config, 'backup_config.json')
```

### Logging

Configure logging for debugging:

```python
from utils.logger import setup_logger

logger = setup_logger(
    name="my_app",
    level="DEBUG",
    log_file="app.log"
)
```

## Error Handling

All clients include comprehensive error handling:

```python
try:
    response = client.create_completion(messages)
except ValueError as e:
    print(f"Configuration error: {e}")
except requests.RequestException as e:
    print(f"API request failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Testing

Run the example scripts:

```bash
# Test individual APIs
python main.py  # Follow the prompts

# Or import and use directly
python -c "from main import example_groq_usage; example_groq_usage()"
python -c "from main import example_perplexity_usage; example_perplexity_usage()"
python -c "from main import example_azure_openai_usage; example_azure_openai_usage()"
python -c "from main import example_multi_api_usage; example_multi_api_usage()"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## TODO

- [ ] Implement audio transcription for Groq
- [ ] Add streaming response support
- [ ] Implement async versions of clients
- [ ] Add comprehensive test suite
- [ ] Add support for more AI providers
- [ ] Implement caching mechanisms
- [ ] Add webhook support for async operations
- [ ] Create CLI interface
- [ ] Add batch processing capabilities
- [ ] Implement token usage tracking

## License

[Your License Here]

## Support

For issues, questions, or contributions, please open an issue on the repository.

## Acknowledgments

- Groq for their fast inference API
- Perplexity for their powerful search capabilities
- Microsoft for Azure OpenAI Service