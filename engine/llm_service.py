"""
LLM service interface for handling interactions with different LLM providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
import os
import requests
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from functools import lru_cache
import re

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

class DeepSeekService(LLMService):
    """DeepSeek LLM service implementation via Fireworks."""
    
    def __init__(self, model: str = "accounts/fireworks/models/deepseek-r1-basic", temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.api_key = os.getenv("FIREWORKS_API_KEY")
        if not self.api_key:
            raise ValueError("FIREWORKS_API_KEY environment variable not set")
        
        self.api_url = "https://api.fireworks.ai/inference/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response using DeepSeek via Fireworks API."""
        try:
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                **kwargs
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            content = response.json()["choices"][0]["message"]["content"]
            # Remove 'Reasoning:' or similar sections
            content = re.split(r'\n?Reasoning:?\n?', content, flags=re.IGNORECASE)[0].strip()
            return content
        except Exception as e:
            logger.error(f"Error generating response from DeepSeek: {str(e)}")
            raise

# Simple in-memory cache for LLM responses (can be replaced with diskcache for persistence)
def llm_cache_key(prompt: str, model: str, provider: str, **kwargs):
    # Create a cache key based on prompt, model, provider, and relevant kwargs
    key = f"{provider}|{model}|{prompt[:100]}|{str(kwargs)}"
    return key

class CachedLLMService(LLMService):
    """LLM service with in-memory caching."""
    def __init__(self, base_service: LLMService, provider: str, model: str):
        self.base_service = base_service
        self.provider = provider
        self.model = model

    @lru_cache(maxsize=128)
    def _cached_response(self, prompt: str, kwargs_str: str):
        # kwargs_str is a stringified version of kwargs for cache key
        import ast
        kwargs = ast.literal_eval(kwargs_str)
        return self.base_service.generate_response(prompt, **kwargs)

    def generate_response(self, prompt: str, **kwargs) -> str:
        kwargs_str = str(kwargs)
        return self._cached_response(prompt, kwargs_str)


def get_llm_service(provider: str = "openai", **kwargs) -> LLMService:
    """Factory function to get the appropriate LLM service with caching."""
    if provider.lower() == "openai":
        base = OpenAIService(**kwargs)
    elif provider.lower() == "anthropic":
        base = AnthropicService(**kwargs)
    elif provider.lower() == "deepseek":
        base = DeepSeekService(**kwargs)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    return CachedLLMService(base, provider, kwargs.get('model', '')) 