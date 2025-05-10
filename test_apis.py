"""
Test script to verify LLM API connections.
"""

import os
from dotenv import load_dotenv
from engine.llm_service import get_llm_manager, ProviderType
from loguru import logger
import litellm

def load_secrets():
    """Load secrets from both .env and .streamlit/secrets.toml."""
    # Load from .env
    load_dotenv()
    
    # Load from Streamlit secrets
    try:
        with open(".streamlit/secrets.toml", "r") as f:
            secrets = f.read()
            # Set environment variables for each API key
            if "openai" in secrets:
                os.environ["OPENAI_API_KEY"] = secrets.split('openai = "')[1].split('"')[0]
            if "anthropic" in secrets:
                os.environ["ANTHROPIC_API_KEY"] = secrets.split('anthropic = "')[1].split('"')[0]
            if "fireworks" in secrets:
                os.environ["FIREWORKS_API_KEY"] = secrets.split('fireworks = "')[1].split('"')[0]
    except Exception as e:
        logger.warning(f"Could not load Streamlit secrets: {str(e)}")

def test_api(provider: str, model: str) -> bool:
    """Test a specific LLM API connection."""
    try:
        # Get LLM manager
        llm_manager = get_llm_manager()
        
        # Map provider string to ProviderType
        provider_type = ProviderType(provider.lower())
        
        # Test prompt
        test_prompt = "Please provide a brief ESG analysis for a solar energy company in Kenya."
        
        # Generate response
        logger.info(f"Sending test request to {provider} API...")
        response = llm_manager.generate_response(
            prompt=test_prompt,
            primary_provider=provider_type,
            max_tokens=500
        )
        
        # Check response
        if response and len(response) > 0:
            logger.success(f"Successfully received response from {provider} API")
            logger.info(f"Response length: {len(response)} characters")
            logger.info("First 200 characters of response:")
            logger.info(response[:200])
            return True
        else:
            logger.error(f"Received empty response from {provider} API")
            return False
            
    except Exception as e:
        logger.error(f"Error testing {provider} API: {str(e)}")
        return False

def main():
    """Run tests for all LLM APIs."""
    # Load secrets
    load_secrets()
    
    # Test configurations
    test_configs = [
        ("openai", "gpt-4-turbo-preview"),
        ("anthropic", "claude-3-opus-20240229"),
        ("deepseek", "deepseek-chat")
    ]
    
    # Run tests
    results = []
    for provider, model in test_configs:
        success = test_api(provider, model)
        results.append((provider, success))
    
    # Print summary
    print("\nTest Summary:")
    print("-" * 50)
    for provider, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{provider}: {status}")
    print("-" * 50)

if __name__ == "__main__":
    litellm.set_verbose = True
    main() 