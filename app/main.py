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

# Import our custom modules
from app.llm.prompt_enhancer import get_prompt_enhancer
from app.database.memory import get_memory_db
from app.config import (
    TEXT_TO_IMAGE_ENDPOINT,
    IMAGE_TO_3D_ENDPOINT,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO if os.environ.get("DEBUG") else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurations for the app
configurations: Dict[str, ConfigClass] = dict()


def config(name: str, value: ConfigClass) -> None:
    """
    Callback function for storing user configurations.

    Args:
        name: user identifier
        value: configuration value
    """
    configurations[name] = value


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
    user_config: ConfigClass = configurations.get('super-user', None)
    logger.info(f"User config: {configurations}")

    # Initialize the Stub with app IDs
    app_ids = user_config.app_ids if user_config else []
    stub = Stub(app_ids)

    try:
        # Step 1: Enhance prompt with LLM
        logger.info("Enhancing prompt with LLM...")
        prompt_enhancer = get_prompt_enhancer()
        enhanced_prompt = prompt_enhancer.enhance_prompt(user_prompt)
        logger.info(f"Enhanced prompt: {enhanced_prompt}")
        
        # Step 2: Generate image from enhanced prompt using Text-to-Image API
        logger.info("Calling Text-to-Image service...")
        text_to_image_params = {
            'prompt': enhanced_prompt,
            'negative_prompt': 'blurry, distorted, low quality',
            'steps': 25,
            'width': 768,
            'height': 768,
        }
        
        # Call the Text-to-Image app
        image_result = stub.call(
            TEXT_TO_IMAGE_ENDPOINT,
            text_to_image_params,
            'super-user'
        )
        
        # Extract image from response
        image_data = image_result.get('result', None)
        if not image_data:
            raise ValueError("Text-to-Image service didn't return an image")
            
        # Save the intermediate image in the static/images directory
        images_dir = "app/static/images"
        os.makedirs(images_dir, exist_ok=True)  # Ensure directory exists
        
        image_filename = f"output_{generation_id}.png"
        image_path = os.path.join(images_dir, image_filename)
        with open(image_path, 'wb') as f:
            f.write(image_data)
        logger.info(f"Saved intermediate image to {image_path}")
        
        # Step 3: Generate 3D model from image using Image-to-3D API
        logger.info("Calling Image-to-3D service...")
        image_to_3d_params = {
            'image': image_data,  # Pass the binary image data
            'format': 'glb',     # Request GLB format for the 3D model
        }
        
        # Call the Image-to-3D app
        model_3d_result = stub.call(
            IMAGE_TO_3D_ENDPOINT,
            image_to_3d_params,
            'super-user'
        )
        
        # Extract 3D model from response
        model_3d_data = model_3d_result.get('result', None)
        if not model_3d_data:
            raise ValueError("Image-to-3D service didn't return a model")
            
        # Save the 3D model in the static/models directory
        models_dir = "app/static/models"
        os.makedirs(models_dir, exist_ok=True)  # Ensure directory exists
        
        model_filename = f"model_{generation_id}.glb"
        model_path = os.path.join(models_dir, model_filename)
        with open(model_path, 'wb') as f:
            f.write(model_3d_data)
        logger.info(f"Saved 3D model to {model_path}")
        
        # Step 4: Store generation metadata in memory
        memory_db = get_memory_db()
        metadata = {
            'text_to_image_params': {
                'prompt': enhanced_prompt,
                'negative_prompt': text_to_image_params.get('negative_prompt', ''),
                'steps': text_to_image_params.get('steps', 25),
                'width': text_to_image_params.get('width', 768),
                'height': text_to_image_params.get('height', 768),
            },
            'image_to_3d_params': {
                'format': image_to_3d_params.get('format', 'glb'),
            }
        }
        
        # Call the save_generation method with the correct parameters
        memory_db.save_generation(
            generation_id=generation_id,
            user_id='system',  # Default user since we don't have user management yet
            prompt=user_prompt,
            enhanced_prompt=enhanced_prompt,
            image_path=image_path,
            model_3d_path=model_path,
            metadata=metadata
        )
        logger.info(f"Stored generation data in memory database")
        
        # Step 5: Prepare success response
        response: OutputClass = model.response
        response.message = json.dumps({
            'status': 'success',
            'generation_id': generation_id,
            'prompt': user_prompt,
            'enhanced_prompt': enhanced_prompt,
            'image_url': f"/static/images/{image_filename}", 
            'model_url': f"/static/models/{model_filename}",
        })
        
    except Exception as e:
        # Handle errors gracefully
        logger.error(f"Error in generation pipeline: {str(e)}")
        response: OutputClass = model.response
        response.message = json.dumps({
            'status': 'error',
            'error': str(e),
        })