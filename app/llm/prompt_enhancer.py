"""
LLM integration module for enhancing user prompts.
Implements TinyLlama model for prompt enhancement using llama-cpp-python.
"""
import os
import logging
import time
from typing import Dict, Optional, List, Any, Union
from pathlib import Path

# Import the llama-cpp-python library for lightweight LLM inference
from llama_cpp import Llama


class PromptEnhancer:
    """Class for enhancing user prompts using a local LLM."""
    
    def __init__(
        self,
        model_name: str = None,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ):
        """Initialize the prompt enhancer.
        
        Args:
            model_name (str, optional): Name of the LLM model to use
            temperature (float, optional): Sampling temperature for text generation
            max_tokens (int, optional): Maximum tokens in generated output
        """
        self.model_name = model_name or os.environ.get("LLM_MODEL", "tinyllama")
        self.temperature = float(os.environ.get("LLM_TEMPERATURE", temperature))
        self.max_tokens = max_tokens
        
        # Model will be initialized on first use to save memory
        self.model = None
        
        logging.info(f"Initialized prompt enhancer with model: {self.model_name}")
    
    def _init_model(self):
        """Initialize the LLM model.
        
        Loads the TinyLlama model using llama-cpp-python.
        """
        logging.info(f"Initializing LLM model: {self.model_name}")
        
        # Set model path (use environment variable if set, or default to our downloaded model)
        model_dir = Path(os.environ.get("LLM_MODEL_DIR", "app/models"))
        
        if self.model_name == "tinyllama":
            model_path = model_dir / "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found: {model_path}. Please download it first.")
            
            logging.info(f"Loading TinyLlama model from {model_path}")
            
            start_time = time.time()
            try:
                # Initialize the model with conservative settings for memory usage
                self.model = Llama(
                    model_path=str(model_path),
                    n_ctx=2048,        # Smaller context window to save memory
                    n_batch=512,       # Reduced batch size
                    n_gpu_layers=0,    # No GPU layers by default to conserve memory
                    verbose=False      # Set to True for debugging
                )
                logging.info(f"TinyLlama model loaded successfully in {time.time() - start_time:.2f} seconds")
            except Exception as e:
                logging.error(f"Failed to load TinyLlama model: {e}")
                raise
        else:
            logging.warning(f"Model {self.model_name} not supported, falling back to TinyLlama")
            # Recursively call with tinyllama as model name
            self.model_name = "tinyllama"
            self._init_model()
    
    def enhance_prompt(self, prompt: str) -> str:
        """Enhance the user prompt for better 3D generation results.
        
        Args:
            prompt (str): Original user prompt
            
        Returns:
            str: Enhanced prompt with more details and specificity
        """
        logging.info(f"Enhancing prompt: {prompt}")
        
        # Initialize model if needed
        if self.model is None:
            self._init_model()
        
        # Create a system prompt that instructs the model on how to enhance 3D generation prompts
        system_prompt = """You are an expert 3D artist. Your task is to enhance text prompts 
        for 3D model generation. Add specific details about lighting, textures, materials, 
        perspective, and other relevant attributes that would make the 3D model more vivid and realistic. 
        Be specific but concise. Focus on visual details, not storytelling."""
        
        # Full prompt with instruction
        full_prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\nEnhance this prompt for 3D model generation: {prompt}<|im_end|>\n<|im_start|>assistant\n"
        
        try:
            # Generate response from the model
            start_time = time.time()
            response = self.model(
                full_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stop=["<|im_end|>", "</s>"],
                echo=False
            )
            generation_time = time.time() - start_time
            
            # Extract the enhanced prompt from the response
            enhanced = response["choices"][0]["text"].strip()
            logging.info(f"LLM response generated in {generation_time:.2f} seconds")
            
            # Fallback if model returns empty or too short response
            if len(enhanced) < 10:
                logging.warning("LLM returned very short or empty response, using fallback enhancement")
                enhanced = f"{prompt}, highly detailed, cinematic lighting, 8k resolution, photorealistic textures, PBR materials, accurate proportions"
        except Exception as e:
            logging.error(f"Error generating enhanced prompt: {e}")
            # Fallback enhancement in case of errors
            enhanced = f"{prompt}, highly detailed, cinematic lighting, 8k resolution, photorealistic textures, PBR materials, accurate proportions"
        
        logging.info(f"Enhanced prompt: {enhanced}")
        return enhanced


# Singleton instance
_prompt_enhancer = None

def get_prompt_enhancer(
    model_name: str = None,
    temperature: float = None,
) -> PromptEnhancer:
    """Get or create a singleton instance of the prompt enhancer.
    
    Args:
        model_name (str, optional): Name of the LLM model to use
        temperature (float, optional): Sampling temperature
        
    Returns:
        PromptEnhancer: Singleton prompt enhancer instance
    """
    global _prompt_enhancer
    if _prompt_enhancer is None:
        _prompt_enhancer = PromptEnhancer(
            model_name=model_name,
            temperature=temperature,
        )
    return _prompt_enhancer
