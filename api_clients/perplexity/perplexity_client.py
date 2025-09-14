"""
Perplexity Sonar API Client Implementation
"""

from typing import Optional, Dict, Any, List, Union
import logging
from ..base import BaseAPIClient

logger = logging.getLogger(__name__)


class PerplexityClient(BaseAPIClient):
    """Client for interacting with Perplexity Sonar API"""
    
    DEFAULT_BASE_URL = "https://api.perplexity.ai"
    DEFAULT_MODEL = "sonar-medium-online"  # Default Perplexity model
    
    # Available Perplexity models
    MODELS = {
        "sonar_small": "sonar-small-chat",
        "sonar_medium": "sonar-medium-chat",
        "sonar_small_online": "sonar-small-online",
        "sonar_medium_online": "sonar-medium-online",
        "codellama_instruct": "codellama-70b-instruct",
        "llama_chat": "llama-3.1-70b-instruct",
        "llama_large": "llama-3.1-405b-instruct"
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Perplexity API client
        
        Args:
            api_key: Perplexity API key
            base_url: Base URL for Perplexity API (defaults to official endpoint)
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
        """Set Perplexity-specific authentication header"""
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}'
        })
    
    def validate_connection(self) -> bool:
        """
        Validate the Perplexity API connection
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            # Try a minimal completion request
            response = self.create_completion(
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return 'choices' in response
        except Exception as e:
            logger.error(f"Connection validation failed: {str(e)}")
            return False
    
    def create_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        top_p: float = 0.9,
        return_citations: bool = False,
        return_images: bool = False,
        return_related_questions: bool = False,
        search_domain_filter: Optional[List[str]] = None,
        search_recency_filter: Optional[str] = None,
        top_k: int = 0,
        stream: bool = False,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 1.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a chat completion with Perplexity
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (defaults to instance model)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            return_citations: Whether to return citations for sourced information
            return_images: Whether to return images in the response
            return_related_questions: Whether to return related follow-up questions
            search_domain_filter: List of domains to restrict search to
            search_recency_filter: Time filter for search results ("day", "week", "month", "year")
            top_k: Number of search results to consider
            stream: Whether to stream the response
            presence_penalty: Presence penalty (0 to 1)
            frequency_penalty: Frequency penalty (1 to 2)
            **kwargs: Additional parameters
            
        Returns:
            Completion response dictionary
        """
        data = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "return_citations": return_citations,
            "return_images": return_images,
            "return_related_questions": return_related_questions,
            "top_k": top_k,
            "stream": stream,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
        }
        
        # Add optional parameters
        if max_tokens is not None:
            data["max_tokens"] = max_tokens
        if search_domain_filter is not None:
            data["search_domain_filter"] = search_domain_filter
        if search_recency_filter is not None:
            data["search_recency_filter"] = search_recency_filter
            
        # Add any additional parameters
        data.update(kwargs)
        
        return self.post("chat/completions", data=data)
    
    def search_web(
        self,
        query: str,
        model: Optional[str] = None,
        search_domains: Optional[List[str]] = None,
        search_recency: Optional[str] = None,
        return_citations: bool = True,
        return_images: bool = False,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform a web search with Perplexity
        
        Args:
            query: Search query
            model: Model to use (should be an online model)
            search_domains: Domains to restrict search to
            search_recency: Time filter ("day", "week", "month", "year")
            return_citations: Whether to return source citations
            return_images: Whether to return relevant images
            max_tokens: Maximum tokens in response
            **kwargs: Additional parameters
            
        Returns:
            Search response with results and optional citations
        """
        # Ensure we're using an online model for web search
        if model is None:
            model = self.DEFAULT_MODEL
        elif "online" not in model.lower():
            logger.warning(f"Model {model} may not support web search. Consider using an 'online' model.")
        
        messages = [{"role": "user", "content": query}]
        
        return self.create_completion(
            messages=messages,
            model=model,
            search_domain_filter=search_domains,
            search_recency_filter=search_recency,
            return_citations=return_citations,
            return_images=return_images,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def research_topic(
        self,
        topic: str,
        questions: Optional[List[str]] = None,
        model: Optional[str] = None,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Research a topic in depth
        
        Args:
            topic: Main topic to research
            questions: Specific questions about the topic
            model: Model to use
            max_tokens: Maximum tokens for response
            **kwargs: Additional parameters
            
        Returns:
            Comprehensive research response
        """
        prompt = f"Please provide comprehensive research on: {topic}"
        
        if questions:
            prompt += "\n\nSpecifically address these questions:\n"
            for i, question in enumerate(questions, 1):
                prompt += f"{i}. {question}\n"
        
        prompt += "\nProvide detailed information with sources."
        
        return self.search_web(
            query=prompt,
            model=model or self.DEFAULT_MODEL,
            return_citations=True,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def fact_check(
        self,
        statement: str,
        context: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Fact-check a statement
        
        Args:
            statement: Statement to fact-check
            context: Additional context for the statement
            model: Model to use
            **kwargs: Additional parameters
            
        Returns:
            Fact-check response with sources
        """
        prompt = f"Please fact-check the following statement: '{statement}'"
        
        if context:
            prompt += f"\n\nContext: {context}"
        
        prompt += "\n\nProvide accurate information with reliable sources."
        
        return self.search_web(
            query=prompt,
            model=model or self.DEFAULT_MODEL,
            return_citations=True,
            search_recency="month",  # Focus on recent information
            **kwargs
        )
    
    def summarize_url(
        self,
        url: str,
        summary_type: str = "concise",
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Summarize content from a URL
        
        Args:
            url: URL to summarize
            summary_type: Type of summary ("concise", "detailed", "bullet_points")
            model: Model to use
            **kwargs: Additional parameters
            
        Returns:
            Summary of the URL content
        """
        prompt = f"Please summarize the content at this URL: {url}"
        
        if summary_type == "concise":
            prompt += "\n\nProvide a concise summary in 2-3 paragraphs."
        elif summary_type == "detailed":
            prompt += "\n\nProvide a comprehensive, detailed summary."
        elif summary_type == "bullet_points":
            prompt += "\n\nProvide a summary in bullet points covering key information."
        
        return self.search_web(
            query=prompt,
            model=model or self.DEFAULT_MODEL,
            search_domains=[url.split('/')[2]],  # Focus on the specific domain
            **kwargs
        )
    
    def compare_topics(
        self,
        topics: List[str],
        aspects: Optional[List[str]] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Compare multiple topics
        
        Args:
            topics: List of topics to compare
            aspects: Specific aspects to compare
            model: Model to use
            **kwargs: Additional parameters
            
        Returns:
            Comparative analysis response
        """
        prompt = f"Please provide a detailed comparison of: {', '.join(topics)}"
        
        if aspects:
            prompt += f"\n\nFocus on these aspects: {', '.join(aspects)}"
        
        prompt += "\n\nProvide a structured comparison with sources."
        
        return self.search_web(
            query=prompt,
            model=model or self.DEFAULT_MODEL,
            return_citations=True,
            max_tokens=3000,
            **kwargs
        )
    
    # Convenience methods
    def simple_search(
        self,
        query: str,
        **kwargs
    ) -> str:
        """
        Simple web search returning just the text response
        
        Args:
            query: Search query
            **kwargs: Additional parameters
            
        Returns:
            Text response
        """
        response = self.search_web(query, **kwargs)
        return response['choices'][0]['message']['content']
    
    def get_citations(
        self,
        response: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract citations from a response
        
        Args:
            response: API response dictionary
            
        Returns:
            List of citation dictionaries
        """
        citations = []
        if 'citations' in response:
            citations = response['citations']
        elif 'choices' in response and response['choices']:
            choice = response['choices'][0]
            if 'citations' in choice:
                citations = choice['citations']
        
        return citations
    
    def get_related_questions(
        self,
        response: Dict[str, Any]
    ) -> List[str]:
        """
        Extract related questions from a response
        
        Args:
            response: API response dictionary
            
        Returns:
            List of related questions
        """
        questions = []
        if 'related_questions' in response:
            questions = response['related_questions']
        elif 'choices' in response and response['choices']:
            choice = response['choices'][0]
            if 'related_questions' in choice:
                questions = choice['related_questions']
        
        return questions