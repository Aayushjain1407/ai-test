"""
Text to 3D Generation Service

This module provides functionality to generate 3D models from text prompts
using Openfabric's AI services.
"""
import logging
import base64
from typing import Dict, Any, Optional

from app.core.stub import Stub
from app.config import TEXT_TO_IMAGE_APP_ID, IMAGE_TO_3D_APP_ID

logger = logging.getLogger(__name__)

class Text3DService:
    """Service for generating 3D models from text prompts."""
    
    def __init__(self):
        """Initialize the service with required stubs."""
        self.text_to_image_app_id = TEXT_TO_IMAGE_APP_ID
        self.image_to_3d_app_id = IMAGE_TO_3D_APP_ID
    
    def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        image_steps: int = 25,
        image_width: int = 512,
        image_height: int = 512,
        model_format: str = "glb"
    ) -> Dict[str, Any]:
        """
        Generate a 3D model from a text prompt.
        
        Args:
            prompt: The text prompt to generate from
            negative_prompt: Negative prompt for image generation
            image_steps: Number of steps for image generation
            image_width: Width of generated image
            image_height: Height of generated image
            model_format: Output format (glb, obj, stl)
            
        Returns:
            Dict containing generation results or error information
        """
        try:
            logger.info(f"Starting 3D generation for prompt: {prompt}")
            
            # Step 1: Generate image from text
            logger.info("Generating image from text...")
            image_params = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "steps": image_steps,
                "width": image_width,
                "height": image_height
            }
            
            image_result = Stub.call(
                app_id=self.text_to_image_app_id,
                parameters=image_params
            )
            
            if not image_result or 'result' not in image_result:
                raise ValueError("Failed to generate image from text")
                
            # Get the generated image data
            image_data = image_result['result']
            
            # Step 2: Generate 3D model from image
            logger.info("Generating 3D model from image...")
            model_params = {
                "image": self._encode_image(image_data),
                "format": model_format
            }
            
            model_result = Stub.call(
                app_id=self.image_to_3d_app_id,
                parameters=model_params
            )
            
            if not model_result or 'result' not in model_result:
                raise ValueError("Failed to generate 3D model from image")
            
            return {
                "status": "success",
                "image_data": image_data,
                "model_data": model_result['result'],
                "format": model_format
            }
            
        except Exception as e:
            error_msg = f"Error in text-to-3D generation: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "status": "error",
                "message": error_msg
            }
    
    @staticmethod
    def _encode_image(image_data: bytes) -> str:
        """Encode binary image data to base64 string."""
        return base64.b64encode(image_data).decode('utf-8')