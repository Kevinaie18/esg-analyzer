"""
Test script for Anthropic API functionality.
"""

import os
from loguru import logger
from engine.llm_service import get_llm_manager, ProviderType

def test_anthropic_api():
    """Test Anthropic API connection and response generation."""
    try:
        # Get LLM manager
        llm_manager = get_llm_manager()
        
        # Test prompt
        test_prompt = "Please provide a brief ESG analysis for a solar energy company in Kenya."
        
        # Generate response
        logger.info("Sending test request to Anthropic API...")
        response = llm_manager.generate_response(
            prompt=test_prompt,
            primary_provider=ProviderType.ANTHROPIC,
            max_tokens=500
        )
        
        # Check response
        if response and len(response) > 0:
            logger.success("Successfully received response from Anthropic API")
            logger.info(f"Response length: {len(response)} characters")
            logger.info("First 200 characters of response:")
            logger.info(response[:200])
            return True
        else:
            logger.error("Received empty response from Anthropic API")
            return False
            
    except Exception as e:
        logger.error(f"Error testing Anthropic API: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_anthropic_api()
    if not success:
        logger.error("Anthropic API test failed")
        exit(1)
    else:
        logger.success("Anthropic API test passed") 