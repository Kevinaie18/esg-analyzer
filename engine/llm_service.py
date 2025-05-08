"""
LLM service interface for handling interactions with different LLM providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
import os
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

class LLMService(ABC):
    """Abstract base class for LLM services."""
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response from the LLM."""
        pass

class OpenAIService(LLMService):
    """OpenAI LLM service implementation."""
    
    def __init__(self, model: str = "gpt-4-turbo-preview", temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
            
        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response using OpenAI's API."""
        try:
            # Test API key permissions first
            try:
                self.client.models.list()
            except Exception as e:
                if "insufficient permissions" in str(e).lower():
                    logger.error("""
                    OpenAI API key has insufficient permissions. Please:
                    1. Go to https://platform.openai.com/api-keys
                    2. Create a new API key with the following scopes:
                       - model.request
                       - completion.request
                    3. Update your API key in the environment variables
                    """)
                raise
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response from OpenAI: {str(e)}")
            raise

class AnthropicService(LLMService):
    """Anthropic LLM service implementation."""
    
    def __init__(self, model: str = "claude-3-opus-20240229", temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            
        import anthropic
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response using Anthropic's API."""
        try:
            response = self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                **kwargs
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error generating response from Anthropic: {str(e)}")
            raise

def get_llm_service(provider: str = "openai", **kwargs) -> LLMService:
    """Factory function to get the appropriate LLM service."""
    if provider.lower() == "openai":
        return OpenAIService(**kwargs)
    elif provider.lower() == "anthropic":
        return AnthropicService(**kwargs)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}") 