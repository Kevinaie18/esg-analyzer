"""
Enhanced LLM service interface for handling interactions with different LLM providers.
Includes robust error handling, provider fallback, and Streamlit Cloud integration.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Union, Any
import os
import json
import time
import requests
from dataclasses import dataclass
from enum import Enum
import streamlit as st
from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from functools import lru_cache
import litellm
from litellm import completion
from datetime import datetime

# Configure logger
logger.remove()
logger.add(
    "logs/llm_service.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

class ProviderError(Exception):
    """Base exception for provider-specific errors."""
    pass

class RateLimitError(ProviderError):
    """Raised when a rate limit is hit."""
    pass

class TokenLimitError(ProviderError):
    """Raised when token limit is exceeded."""
    pass

class TimeoutError(ProviderError):
    """Raised when a request times out."""
    pass

class ProviderType(Enum):
    """Enum for supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"

# Model name mappings
MODEL_MAPPINGS = {
    "gpt-4-turbo-preview": "gpt-4-turbo-preview",
    "gpt-4": "gpt-4",
    "gpt-3.5-turbo": "gpt-3.5-turbo",
    "claude-3-opus-20240229": "anthropic/claude-3-opus-20240229",
    "anthropic/claude-3-opus-20240229": "anthropic/claude-3-opus-20240229",
    "claude-3-sonnet-20240229": "anthropic/claude-3-sonnet-20240229",
    "anthropic/claude-3-sonnet-20240229": "anthropic/claude-3-sonnet-20240229",
    "claude-3-haiku-20240307": "anthropic/claude-3-haiku-20240307",
    "anthropic/claude-3-haiku-20240307": "anthropic/claude-3-haiku-20240307",
    "accounts/fireworks/models/deepseek-r1-basic": "fireworks_ai/accounts/fireworks/models/deepseek-r1-basic",
    "fireworks_ai/accounts/fireworks/models/deepseek-r1-basic": "fireworks_ai/accounts/fireworks/models/deepseek-r1-basic"
}

@dataclass
class ProviderConfig:
    """Configuration for an LLM provider."""
    api_key: str
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: int = 60
    max_retries: int = 3
    retry_delay: int = 1

@dataclass
class RequestMetrics:
    """Metrics for an LLM request."""
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float
    latency: float
    timestamp: datetime
    success: bool
    error: Optional[str] = None

class LLMService(ABC):
    """Abstract base class for LLM services."""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self._setup_client()
    
    @abstractmethod
    def _setup_client(self) -> None:
        """Set up the provider-specific client."""
        pass
    
    @abstractmethod
    def generate_response(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in the text."""
        pass
    
    def _handle_rate_limit(self, retry_count: int) -> None:
        """Handle rate limit errors with exponential backoff."""
        if retry_count >= self.config.max_retries:
            raise RateLimitError("Maximum retry attempts reached")
        
        delay = self.config.retry_delay * (2 ** retry_count)
        logger.warning(f"Rate limit hit, retrying in {delay} seconds...")
        time.sleep(delay)

class OpenAIService(LLMService):
    """OpenAI LLM service implementation using litellm."""
    
    def _setup_client(self) -> None:
        """Set up the OpenAI client."""
        try:
            os.environ["OPENAI_API_KEY"] = self.config.api_key
            logger.info("Successfully initialized OpenAI client")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(RateLimitError)
    )
    def generate_response(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Generate a response using OpenAI's API via litellm."""
        start_time = time.time()
        try:
            response = completion(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                timeout=self.config.timeout
            )
            
            # Calculate metrics
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            latency = time.time() - start_time
            
            # Log metrics
            self._log_metrics(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                latency=latency,
                success=True
            )
            
            return response.choices[0].message.content
            
        except litellm.RateLimitError as e:
            self._log_metrics(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                latency=time.time() - start_time,
                success=False,
                error=str(e)
            )
            raise RateLimitError(str(e))
        except Exception as e:
            self._log_metrics(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                latency=time.time() - start_time,
                success=False,
                error=str(e)
            )
            raise
    
    def count_tokens(self, text: str) -> int:
        """Count tokens using litellm's tokenizer."""
        try:
            return litellm.token_counter(model=self.config.model, text=text)
        except Exception as e:
            logger.error(f"Error counting tokens: {str(e)}")
            raise
    
    def _log_metrics(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        latency: float,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """Log request metrics."""
        metrics = RequestMetrics(
            provider="openai",
            model=self.config.model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost=self._calculate_cost(prompt_tokens, completion_tokens),
            latency=latency,
            timestamp=datetime.now(),
            success=success,
            error=error
        )
        logger.info(f"Request metrics: {metrics}")

    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate the cost of the request."""
        # OpenAI's pricing per 1K tokens (as of 2024)
        PRICING = {
            "gpt-4-turbo-preview": {"prompt": 0.01, "completion": 0.03},
            "gpt-4": {"prompt": 0.03, "completion": 0.06},
            "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002}
        }
        
        model = self.config.model
        if model not in PRICING:
            return 0.0
            
        prompt_cost = (prompt_tokens / 1000) * PRICING[model]["prompt"]
        completion_cost = (completion_tokens / 1000) * PRICING[model]["completion"]
        return prompt_cost + completion_cost

class AnthropicService(LLMService):
    """Anthropic LLM service implementation using litellm."""
    
    def _setup_client(self) -> None:
        """Set up the Anthropic client."""
        try:
            os.environ["ANTHROPIC_API_KEY"] = self.config.api_key
            logger.info("Successfully initialized Anthropic client")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {str(e)}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(RateLimitError)
    )
    def generate_response(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Generate a response using Anthropic's API via litellm."""
        start_time = time.time()
        try:
            response = completion(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                timeout=self.config.timeout
            )
            
            # Calculate metrics
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            latency = time.time() - start_time
            
            # Log metrics
            self._log_metrics(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                latency=latency,
                success=True
            )
            
            return response.choices[0].message.content
            
        except litellm.RateLimitError as e:
            self._log_metrics(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                latency=time.time() - start_time,
                success=False,
                error=str(e)
            )
            raise RateLimitError(str(e))
        except Exception as e:
            self._log_metrics(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                latency=time.time() - start_time,
                success=False,
                error=str(e)
            )
            raise
    
    def count_tokens(self, text: str) -> int:
        """Count tokens using litellm's tokenizer."""
        try:
            return litellm.token_counter(model=self.config.model, text=text)
        except Exception as e:
            logger.error(f"Error counting tokens: {str(e)}")
            raise
    
    def _log_metrics(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        latency: float,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """Log request metrics."""
        metrics = RequestMetrics(
            provider="anthropic",
            model=self.config.model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost=self._calculate_cost(prompt_tokens, completion_tokens),
            latency=latency,
            timestamp=datetime.now(),
            success=success,
            error=error
        )
        logger.info(f"Request metrics: {metrics}")

    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate the cost of the request."""
        # Anthropic's pricing per 1K tokens (as of 2024)
        PRICING = {
            "anthropic/claude-3-opus-20240229": {"prompt": 0.015, "completion": 0.075},
            "anthropic/claude-3-sonnet-20240229": {"prompt": 0.003, "completion": 0.015},
            "anthropic/claude-3-haiku-20240307": {"prompt": 0.00025, "completion": 0.00125}
        }
        
        model = self.config.model
        if model not in PRICING:
            return 0.0
            
        prompt_cost = (prompt_tokens / 1000) * PRICING[model]["prompt"]
        completion_cost = (completion_tokens / 1000) * PRICING[model]["completion"]
        return prompt_cost + completion_cost

class DeepSeekService(LLMService):
    """DeepSeek LLM service implementation using litellm."""
    
    def _setup_client(self) -> None:
        """Set up the DeepSeek client."""
        try:
            os.environ["FIREWORKS_API_KEY"] = self.config.api_key
            logger.info("Successfully initialized DeepSeek client")
        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek client: {str(e)}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(RateLimitError)
    )
    def generate_response(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Generate a response using DeepSeek's API via litellm."""
        start_time = time.time()
        try:
            response = completion(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                timeout=self.config.timeout
            )
            
            # Calculate metrics
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            latency = time.time() - start_time
            
            # Log metrics
            self._log_metrics(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                latency=latency,
                success=True
            )
            
            return response.choices[0].message.content
            
        except litellm.RateLimitError as e:
            self._log_metrics(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                latency=time.time() - start_time,
                success=False,
                error=str(e)
            )
            raise RateLimitError(str(e))
        except Exception as e:
            self._log_metrics(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                latency=time.time() - start_time,
                success=False,
                error=str(e)
            )
            raise
    
    def count_tokens(self, text: str) -> int:
        """Count tokens using litellm's tokenizer."""
        try:
            return litellm.token_counter(model=self.config.model, text=text)
        except Exception as e:
            logger.error(f"Error counting tokens: {str(e)}")
            raise
    
    def _log_metrics(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        latency: float,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """Log request metrics."""
        metrics = RequestMetrics(
            provider="deepseek",
            model=self.config.model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost=self._calculate_cost(prompt_tokens, completion_tokens),
            latency=latency,
            timestamp=datetime.now(),
            success=success,
            error=error
        )
        logger.info(f"Request metrics: {metrics}")

    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate the cost of the request."""
        # DeepSeek's pricing per 1K tokens (as of 2024)
        PRICING = {
            "fireworks_ai/accounts/fireworks/models/deepseek-r1-basic": {"prompt": 0.0005, "completion": 0.001}
        }
        
        model = self.config.model
        if model not in PRICING:
            return 0.0
            
        prompt_cost = (prompt_tokens / 1000) * PRICING[model]["prompt"]
        completion_cost = (completion_tokens / 1000) * PRICING[model]["completion"]
        return prompt_cost + completion_cost

class LLMServiceManager:
    """Manager class for handling multiple LLM providers with fallback support."""
    
    def __init__(self):
        self._load_config()
        self._initialize_providers()
    
    def _load_config(self) -> None:
        """Load configuration from Streamlit secrets or environment variables."""
        try:
            # Try to load from Streamlit secrets first
            secrets = st.secrets
            def resolve_model(key, default):
                model_name = secrets.get("models", {}).get(key, default)
                return MODEL_MAPPINGS.get(model_name, model_name)
            self.config = {
                ProviderType.OPENAI: ProviderConfig(
                    api_key=secrets["api_keys"]["openai"],
                    model=resolve_model("openai", "gpt-4-turbo-preview")
                ),
                ProviderType.ANTHROPIC: ProviderConfig(
                    api_key=secrets["api_keys"]["anthropic"],
                    model=resolve_model("anthropic", "anthropic/claude-3-sonnet-20240229")
                ),
                ProviderType.DEEPSEEK: ProviderConfig(
                    api_key=secrets["api_keys"]["fireworks"],
                    model=resolve_model("deepseek", "fireworks_ai/accounts/fireworks/models/deepseek-r1-basic")
                )
            }
        except Exception as e:
            logger.error(f"Error loading Streamlit secrets: {str(e)}")
            # Fallback to environment variables
            def resolve_env_model(env_key, default):
                model_name = os.getenv(env_key, default)
                return MODEL_MAPPINGS.get(model_name, model_name)
            self.config = {
                ProviderType.OPENAI: ProviderConfig(
                    api_key=os.getenv("OPENAI_API_KEY", ""),
                    model=resolve_env_model("OPENAI_MODEL", "gpt-4-turbo-preview")
                ),
                ProviderType.ANTHROPIC: ProviderConfig(
                    api_key=os.getenv("ANTHROPIC_API_KEY", ""),
                    model=resolve_env_model("ANTHROPIC_MODEL", "anthropic/claude-3-sonnet-20240229")
                ),
                ProviderType.DEEPSEEK: ProviderConfig(
                    api_key=os.getenv("FIREWORKS_API_KEY", ""),
                    model=resolve_env_model("DEEPSEEK_MODEL", "fireworks_ai/accounts/fireworks/models/deepseek-r1-basic")
                )
            }
    
    def _initialize_providers(self) -> None:
        """Initialize provider instances."""
        self.providers = {
            ProviderType.OPENAI: OpenAIService(self.config[ProviderType.OPENAI]),
            ProviderType.ANTHROPIC: AnthropicService(self.config[ProviderType.ANTHROPIC]),
            ProviderType.DEEPSEEK: DeepSeekService(self.config[ProviderType.DEEPSEEK])
        }
    
    def generate_response(
        self,
        prompt: str,
        primary_provider: ProviderType = ProviderType.OPENAI,
        fallback_providers: Optional[List[ProviderType]] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate a response using the specified provider with fallback support.
        
        Args:
            prompt: The prompt to send to the LLM
            primary_provider: The primary provider to use
            fallback_providers: List of providers to try if primary fails
            max_tokens: Maximum tokens in the response
            temperature: Temperature for generation
            
        Returns:
            The generated response
            
        Raises:
            ProviderError: If all providers fail
        """
        if fallback_providers is None:
            fallback_providers = [
                ProviderType.ANTHROPIC,
                ProviderType.DEEPSEEK
            ]
        
        # Try primary provider first
        try:
            return self.providers[primary_provider].generate_response(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
        except ProviderError as e:
            logger.warning(f"Primary provider {primary_provider} failed: {str(e)}")
            
            # Try fallback providers
            for provider in fallback_providers:
                try:
                    return self.providers[provider].generate_response(
                        prompt,
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                except ProviderError as e:
                    logger.warning(f"Fallback provider {provider} failed: {str(e)}")
                    continue
            
            # If all providers fail
            raise ProviderError("All providers failed to generate a response")

# Create a singleton instance for Streamlit
def get_llm_manager() -> LLMServiceManager:
    """Get the singleton LLM service manager instance."""
    return LLMServiceManager() 