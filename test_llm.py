#!/usr/bin/env python
"""
Test script to verify the TinyLlama LLM integration is working properly
by enhancing a sample prompt.
"""
import os
import logging
import sys
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
load_dotenv()

def main():
    """Test the prompt enhancement with TinyLlama."""
    
    print("Loading TinyLlama LLM integration...")
    from app.llm.prompt_enhancer import get_prompt_enhancer
    
    # Create a sample prompt
    sample_prompt = "A futuristic city skyline at sunset"
    print(f"\nOriginal prompt: {sample_prompt}")
    
    # Get the prompt enhancer
    print("\nInitializing prompt enhancer (this may take a few seconds to load the model)...")
    enhancer = get_prompt_enhancer()
    
    # Enhance the prompt
    print("\nEnhancing prompt with TinyLlama...")
    enhanced_prompt = enhancer.enhance_prompt(sample_prompt)
    
    print("\n--- Results ---")
    print(f"Original: {sample_prompt}")
    print(f"Enhanced: {enhanced_prompt}")
    print("\nLLM integration test completed!")

if __name__ == "__main__":
    main()
