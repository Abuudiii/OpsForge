"""
Groq API Client Implementation
"""

from typing import Optional, Dict, Any, List, Union
import logging
from ..base import BaseAPIClient

logger = logging.getLogger(__name__)


class GroqClient(BaseAPIClient):
    """Client for interacting with Groq API"""
    
    DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"
    DEFAULT_MODEL = "mixtral-8x7b-32768"  # Default Groq model
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Groq API client
        
        Args:
            api_key: Groq API key
            base_url: Base URL for Groq API (defaults to official endpoint)
            model: Default model to use for completions
            **kwargs: Additional configuration parameters
        """
        super().__init__(
            api_key=api_key,
            base_url=base_url or self.DEFAULT_BASE_URL,
            **kwargs
        )
        self.model = model or self.DEFAULT_MODEL
        
    def _set_auth_header(self, api_key: str):
        """Set Groq-specific authentication header"""
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}'
        })
    
    def validate_connection(self) -> bool:
        """
        Validate the Groq API connection
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            # Try to list available models
            response = self.list_models()
            return 'data' in response
        except Exception as e:
            logger.error(f"Connection validation failed: {str(e)}")
            return False
    
    def list_models(self) -> Dict[str, Any]:
        """
        List available models
        
        Returns:
            Dictionary containing available models
        """
        return self.get("models")
    
    def create_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        n: int = 1,
        stream: bool = False,
        stop: Optional[Union[str, List[str]]] = None,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        user: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a chat completion
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (defaults to instance model)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            n: Number of completions to generate
            stream: Whether to stream the response
            stop: Stop sequences
            presence_penalty: Presence penalty (-2.0 to 2.0)
            frequency_penalty: Frequency penalty (-2.0 to 2.0)
            user: Unique identifier for end-user
            **kwargs: Additional parameters
            
        Returns:
            Completion response dictionary
        """
        data = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "n": n,
            "stream": stream,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
        }
        
        # Add optional parameters
        if max_tokens is not None:
            data["max_tokens"] = max_tokens
        if stop is not None:
            data["stop"] = stop
        if user is not None:
            data["user"] = user
            
        # Add any additional parameters
        data.update(kwargs)
        
        return self.post("chat/completions", data=data)
    
    def create_embedding(
        self,
        input: Union[str, List[str]],
        model: str = "nomic-embed-text-v1.5",
        encoding_format: str = "float",
        user: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create embeddings for text
        
        Args:
            input: Text or list of texts to embed
            model: Embedding model to use
            encoding_format: Format of the embeddings ("float" or "base64")
            user: Unique identifier for end-user
            **kwargs: Additional parameters
            
        Returns:
            Embedding response dictionary
        """
        data = {
            "input": input,
            "model": model,
            "encoding_format": encoding_format,
        }
        
        if user is not None:
            data["user"] = user
            
        data.update(kwargs)
        
        return self.post("embeddings", data=data)
    
    def transcribe_audio(
        self,
        file_path: str,
        model: str = "whisper-large-v3",
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: str = "json",
        temperature: float = 0.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Transcribe audio file
        
        Args:
            file_path: Path to audio file
            model: Transcription model to use
            language: Language of the audio (ISO-639-1)
            prompt: Optional prompt to guide the model
            response_format: Output format (json, text, srt, verbose_json, vtt)
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Transcription response
        """
        # TODO: Implement file upload logic
        # This is a placeholder - you'll need to handle file uploads properly
        raise NotImplementedError("Audio transcription requires file upload implementation")
    
    def translate_audio(
        self,
        file_path: str,
        model: str = "whisper-large-v3",
        prompt: Optional[str] = None,
        response_format: str = "json",
        temperature: float = 0.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Translate audio file to English
        
        Args:
            file_path: Path to audio file
            model: Translation model to use
            prompt: Optional prompt to guide the model
            response_format: Output format (json, text, srt, verbose_json, vtt)
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Translation response
        """
        # TODO: Implement file upload logic
        # This is a placeholder - you'll need to handle file uploads properly
        raise NotImplementedError("Audio translation requires file upload implementation")
    
    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        Estimate token count for text
        
        Args:
            text: Text to count tokens for
            model: Model to use for tokenization
            
        Returns:
            Estimated token count
        """
        # Simple approximation - you may want to use tiktoken for accurate counting
        # This is a rough estimate: ~4 characters per token
        return len(text) // 4
    
    def create_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ):
        """
        Create a streaming chat completion
        
        Args:
            messages: List of message dictionaries
            model: Model to use
            **kwargs: Additional parameters
            
        Yields:
            Streaming response chunks
        """
        # Set stream to True
        kwargs['stream'] = True
        
        # TODO: Implement proper streaming logic
        # This would require handling Server-Sent Events (SSE)
        raise NotImplementedError("Streaming responses require SSE implementation")
    
    # Convenience methods
    def simple_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Simple completion with just a prompt
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters for create_completion
            
        Returns:
            Generated text response
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.create_completion(messages, **kwargs)
        return response['choices'][0]['message']['content']
    
    def conversation_completion(
        self,
        conversation: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        Continue a conversation
        
        Args:
            conversation: List of message dictionaries representing the conversation
            **kwargs: Additional parameters for create_completion
            
        Returns:
            Generated response
        """
        response = self.create_completion(conversation, **kwargs)
        return response['choices'][0]['message']['content']