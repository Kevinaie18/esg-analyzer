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
import time
import openai
from openai import OpenAI
import anthropic
from anthropic import Anthropic
import litellm
from litellm import completion

class LLMService(ABC):
    """Abstract base class for LLM services."""
    
    def __init__(self, model: str, temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.max_retries = 3
        self.retry_delay = 1  # seconds
    
    @abstractmethod
    def generate_response(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate a response from the LLM."""
        pass
    
    def _handle_rate_limit(self, retry_count: int) -> None:
        """Handle rate limit errors with exponential backoff."""
        if retry_count >= self.max_retries:
            raise Exception("Maximum retry attempts reached")
        
        delay = self.retry_delay * (2 ** retry_count)
        logger.warning(f"Rate limit hit, retrying in {delay} seconds...")
        time.sleep(delay)

class OpenAIService(LLMService):
    """OpenAI LLM service implementation."""
    
    def __init__(self, model: str, temperature: float = 0.7):
        super().__init__(model, temperature)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=api_key)
        
    def generate_response(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate a response using OpenAI's API."""
        retry_count = 0
        while True:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            except openai.RateLimitError:
                self._handle_rate_limit(retry_count)
                retry_count += 1
            except Exception as e:
                logger.error(f"Error generating response: {str(e)}")
                raise

class AnthropicService(LLMService):
    """Anthropic LLM service implementation."""
    
    def __init__(self, model: str, temperature: float = 0.7):
        super().__init__(model, temperature)
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = Anthropic(api_key=api_key)
        
    def generate_response(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate a response using Anthropic's API."""
        retry_count = 0
        while True:
            try:
                response = self.client.messages.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=max_tokens
                )
                return response.content[0].text
            except anthropic.RateLimitError:
                self._handle_rate_limit(retry_count)
                retry_count += 1
            except Exception as e:
                logger.error(f"Error generating response: {str(e)}")
                raise

class DeepSeekService(LLMService):
    """DeepSeek LLM service implementation via Fireworks."""
    
    def __init__(self, model: str, temperature: float = 0.7):
        super().__init__(model, temperature)
        api_key = os.getenv("FIREWORKS_API_KEY")
        if not api_key:
            raise ValueError("FIREWORKS_API_KEY environment variable not set")
        self.api_key = api_key
        
    def generate_response(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate a response using DeepSeek via Fireworks API."""
        retry_count = 0
        while True:
            try:
                # Remove proxies from kwargs if present
                kwargs = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": self.temperature,
                    "max_tokens": max_tokens,
                    "api_key": self.api_key
                }
                kwargs.pop('proxies', None)  # Remove proxies if present
                
                response = completion(**kwargs)
                return response.choices[0].message.content
            except litellm.RateLimitError:
                self._handle_rate_limit(retry_count)
                retry_count += 1
            except Exception as e:
                logger.error(f"Error generating response: {str(e)}")
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


@lru_cache(maxsize=100)
def get_llm_service(provider: str, model: str, temperature: float = 0.7) -> LLMService:
    """
    Get an LLM service instance for the specified provider.
    
    Args:
        provider: The LLM provider ("openai", "anthropic", or "deepseek")
        model: The model name to use
        temperature: The temperature parameter for generation
        
    Returns:
        An instance of the appropriate LLM service
    """
    provider = provider.lower()
    if provider == "openai":
        return OpenAIService(model, temperature)
    elif provider == "anthropic":
        return AnthropicService(model, temperature)
    elif provider == "deepseek":
        return DeepSeekService(model, temperature)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}") 