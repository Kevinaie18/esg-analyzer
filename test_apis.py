"""
Test script to verify LLM API connections.
"""

import os
from dotenv import load_dotenv
from engine.llm_service import get_llm_service
from loguru import logger
import toml

def load_secrets():
    """Load secrets from both .env and .streamlit/secrets.toml."""
    # Load from .env
    load_dotenv()
    
    # Load from Streamlit secrets
    try:
        secrets = toml.load(".streamlit/secrets.toml")
        for key, value in secrets.items():
            if key.endswith("_API_KEY") and value and value != "your_openai_api_key_here":
                os.environ[key] = value
    except Exception as e:
        logger.warning(f"Could not load Streamlit secrets: {str(e)}")

def test_api(provider: str, model: str) -> bool:
    """Test a specific LLM API."""
    try:
        logger.info(f"Testing {provider} API with model {model}...")
        service = get_llm_service(provider, model)
        response = service.generate_response("Hello, this is a test message. Please respond with 'API test successful'.")
        logger.success(f"{provider} API test successful!")
        logger.info(f"Response: {response}")
        return True
    except Exception as e:
        logger.error(f"{provider} API test failed: {str(e)}")
        return False

def main():
    """Run tests for all LLM APIs."""
    # Load secrets
    load_secrets()
    
    # Test configurations
    test_configs = [
        ("openai", "gpt-3.5-turbo"),
        ("anthropic", "claude-3-opus-20240229"),
        ("deepseek", "accounts/fireworks/models/deepseek-r1-basic")
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
    main() 