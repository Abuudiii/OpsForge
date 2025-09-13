"""
Azure OpenAI API Client Implementation
"""

from typing import Optional, Dict, Any, List, Union
import logging
from datetime import datetime
from ..base import BaseAPIClient

logger = logging.getLogger(__name__)


class AzureOpenAIClient(BaseAPIClient):
    """Client for interacting with Azure OpenAI Service"""
    
    # Available Azure OpenAI models (deployment names may vary)
    MODELS = {
        "gpt_35_turbo": "gpt-35-turbo",
        "gpt_35_turbo_16k": "gpt-35-turbo-16k",
        "gpt_4": "gpt-4",
        "gpt_4_32k": "gpt-4-32k",
        "gpt_4_turbo": "gpt-4-turbo",
        "gpt_4o": "gpt-4o",
        "gpt_4o_mini": "gpt-4o-mini",
        "text_embedding_ada": "text-embedding-ada-002",
        "text_embedding_3_small": "text-embedding-3-small",
        "text_embedding_3_large": "text-embedding-3-large",
        "dall_e_3": "dall-e-3"
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        api_version: str = "2024-02-01",
        deployment_name: Optional[str] = None,
        azure_ad_token: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Azure OpenAI API client
        
        Args:
            api_key: Azure API key
            azure_endpoint: Azure OpenAI endpoint (https://<resource-name>.openai.azure.com/)
            api_version: API version to use
            deployment_name: Default deployment name for operations
            azure_ad_token: Azure Active Directory token for authentication (alternative to api_key)
            **kwargs: Additional configuration parameters
        """
        # Construct base URL with API version
        if azure_endpoint:
            base_url = f"{azure_endpoint.rstrip('/')}/openai"
        else:
            base_url = None
            
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            **kwargs
        )
        
        self.api_version = api_version
        self.deployment_name = deployment_name
        self.azure_ad_token = azure_ad_token
        self.azure_endpoint = azure_endpoint
        
        # Update session headers for Azure
        if azure_ad_token:
            self._set_ad_auth_header(azure_ad_token)
    
    def _set_auth_header(self, api_key: str):
        """Set Azure-specific authentication header"""
        self.session.headers.update({
            'api-key': api_key
        })
    
    def _set_ad_auth_header(self, token: str):
        """Set Azure AD authentication header"""
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })
    
    def _construct_url(self, deployment: str, operation: str) -> str:
        """
        Construct Azure OpenAI API URL
        
        Args:
            deployment: Deployment name
            operation: API operation (e.g., 'chat/completions')
            
        Returns:
            Complete URL for the API call
        """
        return f"deployments/{deployment}/{operation}?api-version={self.api_version}"
    
    def validate_connection(self) -> bool:
        """
        Validate the Azure OpenAI connection
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            # Try to get model details if deployment is specified
            if self.deployment_name:
                response = self.get_deployment_details(self.deployment_name)
                return response is not None
            else:
                logger.warning("No deployment name specified for validation")
                return False
        except Exception as e:
            logger.error(f"Connection validation failed: {str(e)}")
            return False
    
    def get_deployment_details(self, deployment_name: str) -> Dict[str, Any]:
        """
        Get details about a specific deployment
        
        Args:
            deployment_name: Name of the deployment
            
        Returns:
            Deployment details dictionary
        """
        url = f"deployments/{deployment_name}?api-version={self.api_version}"
        return self.get(url)
    
    def create_completion(
        self,
        messages: List[Dict[str, str]],
        deployment_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        n: int = 1,
        stream: bool = False,
        stop: Optional[Union[str, List[str]]] = None,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        user: Optional[str] = None,
        response_format: Optional[Dict[str, str]] = None,
        seed: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a chat completion using Azure OpenAI
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            deployment_name: Deployment to use (defaults to instance deployment)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            n: Number of completions to generate
            stream: Whether to stream the response
            stop: Stop sequences
            presence_penalty: Presence penalty (-2.0 to 2.0)
            frequency_penalty: Frequency penalty (-2.0 to 2.0)
            user: Unique identifier for end-user
            response_format: Response format specification
            seed: Random seed for deterministic output
            tools: List of available tools/functions
            tool_choice: How to choose tools
            **kwargs: Additional parameters
            
        Returns:
            Completion response dictionary
        """
        deployment = deployment_name or self.deployment_name
        if not deployment:
            raise ValueError("Deployment name must be specified")
        
        data = {
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
        if response_format is not None:
            data["response_format"] = response_format
        if seed is not None:
            data["seed"] = seed
        if tools is not None:
            data["tools"] = tools
        if tool_choice is not None:
            data["tool_choice"] = tool_choice
            
        # Add any additional parameters
        data.update(kwargs)
        
        url = self._construct_url(deployment, "chat/completions")
        return self.post(url, data=data)
    
    def create_embedding(
        self,
        input: Union[str, List[str]],
        deployment_name: Optional[str] = None,
        user: Optional[str] = None,
        encoding_format: str = "float",
        dimensions: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create embeddings using Azure OpenAI
        
        Args:
            input: Text or list of texts to embed
            deployment_name: Embedding deployment to use
            user: Unique identifier for end-user
            encoding_format: Format of the embeddings ("float" or "base64")
            dimensions: Number of dimensions for the embedding
            **kwargs: Additional parameters
            
        Returns:
            Embedding response dictionary
        """
        deployment = deployment_name or self.deployment_name
        if not deployment:
            raise ValueError("Deployment name must be specified")
        
        data = {
            "input": input,
            "encoding_format": encoding_format,
        }
        
        if user is not None:
            data["user"] = user
        if dimensions is not None:
            data["dimensions"] = dimensions
            
        data.update(kwargs)
        
        url = self._construct_url(deployment, "embeddings")
        return self.post(url, data=data)
    
    def create_image(
        self,
        prompt: str,
        deployment_name: Optional[str] = None,
        n: int = 1,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid",
        user: Optional[str] = None,
        response_format: str = "url",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate images using DALL-E 3
        
        Args:
            prompt: Text description of the image to generate
            deployment_name: DALL-E deployment to use
            n: Number of images to generate (1 for DALL-E 3)
            size: Image size ("1024x1024", "1792x1024", "1024x1792")
            quality: Quality level ("standard" or "hd")
            style: Style preset ("vivid" or "natural")
            user: Unique identifier for end-user
            response_format: Response format ("url" or "b64_json")
            **kwargs: Additional parameters
            
        Returns:
            Image generation response
        """
        deployment = deployment_name or self.deployment_name
        if not deployment:
            raise ValueError("Deployment name must be specified")
        
        data = {
            "prompt": prompt,
            "n": n,
            "size": size,
            "quality": quality,
            "style": style,
            "response_format": response_format,
        }
        
        if user is not None:
            data["user"] = user
            
        data.update(kwargs)
        
        url = self._construct_url(deployment, "images/generations")
        return self.post(url, data=data)
    
    def analyze_image(
        self,
        image_url: str,
        prompt: str = "What's in this image?",
        deployment_name: Optional[str] = None,
        detail: str = "auto",
        max_tokens: int = 300,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze an image using GPT-4 Vision
        
        Args:
            image_url: URL of the image to analyze
            prompt: Question or prompt about the image
            deployment_name: GPT-4 Vision deployment to use
            detail: Level of detail ("low", "high", or "auto")
            max_tokens: Maximum tokens in response
            **kwargs: Additional parameters
            
        Returns:
            Image analysis response
        """
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                            "detail": detail
                        }
                    }
                ]
            }
        ]
        
        return self.create_completion(
            messages=messages,
            deployment_name=deployment_name,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def create_function_call(
        self,
        messages: List[Dict[str, str]],
        functions: List[Dict[str, Any]],
        deployment_name: Optional[str] = None,
        function_call: Union[str, Dict[str, str]] = "auto",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a completion with function calling
        
        Args:
            messages: Conversation messages
            functions: List of available functions
            deployment_name: Deployment to use
            function_call: How to call functions ("auto", "none", or specific function)
            **kwargs: Additional parameters
            
        Returns:
            Completion response with function call
        """
        # Convert to new tools format
        tools = [{"type": "function", "function": func} for func in functions]
        
        return self.create_completion(
            messages=messages,
            deployment_name=deployment_name,
            tools=tools,
            tool_choice=function_call if function_call != "auto" else None,
            **kwargs
        )
    
    def create_assistants_message(
        self,
        thread_id: str,
        assistant_id: str,
        deployment_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a message in an Assistants API thread
        
        Args:
            thread_id: Thread ID
            assistant_id: Assistant ID
            deployment_name: Deployment to use
            **kwargs: Additional parameters
            
        Returns:
            Message response
        """
        deployment = deployment_name or self.deployment_name
        if not deployment:
            raise ValueError("Deployment name must be specified")
        
        # Note: Azure OpenAI Assistants API may have different endpoints
        # This is a placeholder implementation
        raise NotImplementedError("Assistants API implementation pending Azure specifications")
    
    def moderate_content(
        self,
        text: str,
        deployment_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Check content for policy violations
        
        Args:
            text: Text to moderate
            deployment_name: Moderation deployment to use
            **kwargs: Additional parameters
            
        Returns:
            Moderation response
        """
        deployment = deployment_name or self.deployment_name
        if not deployment:
            raise ValueError("Deployment name must be specified")
        
        data = {"input": text}
        data.update(kwargs)
        
        url = self._construct_url(deployment, "moderations")
        return self.post(url, data=data)
    
    # Convenience methods
    def simple_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        deployment_name: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Simple completion with just a prompt
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            deployment_name: Deployment to use
            **kwargs: Additional parameters
            
        Returns:
            Generated text response
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.create_completion(
            messages,
            deployment_name=deployment_name,
            **kwargs
        )
        return response['choices'][0]['message']['content']
    
    def count_tokens(self, text: str, model: str = "gpt-4") -> int:
        """
        Estimate token count for text
        
        Args:
            text: Text to count tokens for
            model: Model to base estimation on
            
        Returns:
            Estimated token count
        """
        # Rough estimation - you may want to use tiktoken for accurate counting
        # Different models have different tokenization
        if "gpt-4" in model:
            return len(text) // 3
        else:
            return len(text) // 4
    
    def create_json_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        deployment_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a completion with JSON response format
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            deployment_name: Deployment to use
            **kwargs: Additional parameters
            
        Returns:
            Parsed JSON response
        """
        import json
        
        # Add JSON instruction to system prompt
        json_system = "You must respond with valid JSON only."
        if system_prompt:
            json_system = f"{system_prompt}\n\n{json_system}"
        
        response_text = self.simple_completion(
            prompt=prompt,
            system_prompt=json_system,
            deployment_name=deployment_name,
            response_format={"type": "json_object"},
            **kwargs
        )
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return {"error": "Invalid JSON response", "raw": response_text}
    
    def batch_embeddings(
        self,
        texts: List[str],
        batch_size: int = 100,
        deployment_name: Optional[str] = None,
        **kwargs
    ) -> List[List[float]]:
        """
        Create embeddings for multiple texts in batches
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts per batch
            deployment_name: Embedding deployment to use
            **kwargs: Additional parameters
            
        Returns:
            List of embedding vectors
        """
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.create_embedding(
                input=batch,
                deployment_name=deployment_name,
                **kwargs
            )
            
            # Extract embeddings from response
            for item in response['data']:
                all_embeddings.append(item['embedding'])
        
        return all_embeddings