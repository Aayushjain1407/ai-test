import logging
import sys
import os
import uuid
import json
import time
from typing import Dict, List, Optional, Any

# Add the project root to the Python path
sys.path.append('/Users/aayushjain/Desktop/ai-test')

# Import from the 'onto' directory
from onto.dc8f06af066e4a7880a5938933236037.config import ConfigClass
from onto.dc8f06af066e4a7880a5938933236037.input import InputClass
from onto.dc8f06af066e4a7880a5938933236037.output import OutputClass
from openfabric_pysdk.context import AppModel, State
from app.core.stub import Stub
from app.api.services.text_to_3d_service import Text3DService

# Import our custom modules
from app.llm.prompt_enhancer import get_prompt_enhancer

# Configure logging
logging.basicConfig(
    level=logging.INFO if os.environ.get("DEBUG") else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurations for the app
configurations: Dict[str, ConfigClass] = {}

def config(name: str, value: ConfigClass) -> None:
    """
    Callback function for storing user configurations.

    Args:
        name: user identifier
        value: configuration value
    """
    if not isinstance(value, ConfigClass):
        raise ValueError("Configuration value must be an instance of ConfigClass")
    configurations[name] = value

# Initialize default configuration
default_config = ConfigClass()
default_config.app_ids = "f0997a01-d6d3-a5fe-53d8-561300318557,69543f29-4d41-4afc-7f29-3d51591f11eb"  # Default app IDs from README
config("super-user", default_config)





############################################################
# Execution callback function
############################################################
def execute(model: AppModel) -> None:
    """
    Main execution entry point for handling a model pass.

    Args:
        model (AppModel): The model object containing request and response structures.
    """
    # Generate a unique ID for this generation
    generation_id = str(uuid.uuid4())
    logger.info(f"Starting generation pipeline with ID: {generation_id}")

    # Retrieve input
    request: InputClass = model.request
    user_prompt = request.prompt
    logger.info(f"User prompt: {user_prompt}")

    # Retrieve user config
    user_config: ConfigClass = configurations.get('super-user')
    if not user_config:
        logger.error("No configuration found for 'super-user'")
        model.response.message = "Error: Configuration not found"
        return

    try:
        # Initialize the Text3DService
        text_3d_service = Text3DService()
        
        try:
            # Step 1: Enhance prompt with LLM if needed
            enhanced_prompt = user_prompt
            if not user_prompt.startswith("A 3D model of"):
                logger.info("Enhancing prompt with LLM...")
                prompt_enhancer = get_prompt_enhancer()
                enhanced_prompt = prompt_enhancer.enhance_prompt(user_prompt)
                logger.info(f"Enhanced prompt: {enhanced_prompt}")
            
            # Step 2: Generate 3D model using Text3DService
            logger.info("Starting 3D model generation pipeline...")
            result = text_3d_service.generate(
                prompt=enhanced_prompt,
                negative_prompt=user_config.negative_prompt if hasattr(user_config, 'negative_prompt') else "",
                image_steps=user_config.image_steps if hasattr(user_config, 'image_steps') else 25,
                image_width=user_config.image_width if hasattr(user_config, 'image_width') else 512,
                image_height=user_config.image_height if hasattr(user_config, 'image_height') else 512,
                model_format=user_config.model_format if hasattr(user_config, 'model_format') else "glb"
            )
            
            # Check if generation was successful
            if result.get('status') == 'success':
                model.response.message = "3D model generated successfully"
                # Add any additional response data needed
                if 'model_data' in result:
                    model.response.model_data = result['model_data']
                if 'image_data' in result:
                    model.response.image_data = result['image_data']
            else:
                model.response.message = f"Failed to generate 3D model: {result.get('message', 'Unknown error')}"
                
        except Exception as e:
            error_msg = f"Error in 3D generation pipeline: {str(e)}"
            logger.error(error_msg, exc_info=True)
            model.response.message = error_msg
            
    except Exception as e:
        error_msg = f"Failed to initialize services: {str(e)}"
        logger.error(error_msg, exc_info=True)
        model.response.message = error_msg
    
    # Prepare the final response
    try:
        response: OutputClass = model.response
        if not hasattr(response, 'message'):
            response.message = "Processing completed"
    except Exception as e:
        logger.error(f"Error preparing response: {str(e)}")
        model.response.message = f"Error preparing response: {str(e)}"

if __name__ == "__main__":
    # Test configuration
    print("Testing configuration...")
    print("Configurations:", configurations)
    if 'super-user' in configurations:
        print("Super-user config found!")
        print("App IDs:", configurations['super-user'].app_ids)
    else:
        print("No super-user config found.")