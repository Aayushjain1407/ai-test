#!/usr/bin/env python
"""
Test script to validate the Text-to-3D pipeline workflow using mock responses
for the Openfabric API calls.
"""
import os
import sys
import logging
import uuid
import json
import base64
from dotenv import load_dotenv
from unittest.mock import patch, MagicMock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
load_dotenv()

# Import our modules
from app.llm.prompt_enhancer import get_prompt_enhancer
from app.database.memory import get_memory_db
from onto.dc8f06af066e4a7880a5938933236037.config import ConfigClass
from onto.dc8f06af066e4a7880a5938933236037.input import InputClass
from onto.dc8f06af066e4a7880a5938933236037.output import OutputClass
from openfabric_pysdk.context import AppModel, State

# Import our main execution function
from app.main import execute, config


class MockAppModel:
    """Mock AppModel class to simulate the Openfabric SDK's AppModel."""
    def __init__(self, prompt):
        self.request = InputClass()
        self.request.prompt = prompt
        self.response = OutputClass()


def mock_stub_call(endpoint, params, user):
    """Mock function to simulate Stub.call responses."""
    print(f"Mock Stub call to {endpoint} with params: {params}")
    
    # For Text-to-Image endpoint, return a simple test image
    if "text-to-image" in endpoint or "f0997a01" in endpoint:
        # Use a simple 1x1 pixel PNG as a mock response
        mock_image = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
        return {'result': mock_image}
    
    # For Image-to-3D endpoint, return a simple mock 3D model (in this case, just a dummy byte string)
    elif "image-to-3d" in endpoint or "69543f29" in endpoint:
        # Mock 3D model data as bytes
        mock_3d_model = b'MOCK_3D_MODEL_DATA'
        return {'result': mock_3d_model}
    
    return {'result': None}


def main():
    """Test the full Text-to-3D pipeline with mocked Openfabric service calls."""
    
    # Set up mock config with app IDs
    user_config = ConfigClass()
    user_config.app_ids = [
        "f0997a01-d6d3-a5fe-53d8-561300318557",  # Text-to-Image
        "69543f29-4d41-4afc-7f29-3d51591f11eb",   # Image-to-3D
    ]
    config('super-user', user_config)
    
    # Create test prompt
    test_prompt = "A glowing dragon standing on a cliff at sunset"
    print(f"\n[TEST] Using test prompt: '{test_prompt}'")
    
    # Create a mock AppModel
    model = MockAppModel(test_prompt)
    
    # Mock the Stub.call method
    with patch('app.core.stub.Stub.call', side_effect=mock_stub_call):
        print("\n[TEST] Running pipeline with mocked Openfabric services...")
        # Execute the pipeline
        execute(model)
        
        # Check the response
        response_data = json.loads(model.response.message)
        print("\n[TEST] Pipeline execution completed!")
        print(f"[TEST] Response status: {response_data.get('status', 'unknown')}")
        
        if response_data.get('status') == 'success':
            print("\n[TEST] Pipeline execution successful!")
            print(f"[TEST] Generation ID: {response_data.get('generation_id')}")
            print(f"[TEST] Original prompt: {response_data.get('prompt')}")
            print(f"[TEST] Enhanced prompt: {response_data.get('enhanced_prompt')[:100]}...")
            print(f"[TEST] Image URL: {response_data.get('image_url')}")
            print(f"[TEST] Model URL: {response_data.get('model_url')}")
            
            # Check if files were created
            image_path = "app/" + response_data.get('image_url').lstrip('/')
            model_path = "app/" + response_data.get('model_url').lstrip('/')
            
            if os.path.exists(image_path):
                print(f"[TEST] ✅ Image file created: {image_path}")
            else:
                print(f"[TEST] ❌ Image file not found: {image_path}")
                
            if os.path.exists(model_path):
                print(f"[TEST] ✅ 3D model file created: {model_path}")
            else:
                print(f"[TEST] ❌ 3D model file not found: {model_path}")
                
            # Check if generation was stored in memory
            memory_db = get_memory_db()
            # Use get_user_generations with the system user ID we used
            generations = memory_db.get_user_generations('system')
            if generations and len(generations) > 0:
                print(f"[TEST] ✅ Generation stored in memory database")
                print(f"[TEST] Memory database has {len(generations)} generations for system user")
            else:
                print(f"[TEST] ❌ Generation not stored in memory database")
        else:
            print("\n[TEST] Pipeline execution failed!")
            print(f"[TEST] Error: {response_data.get('error')}")


if __name__ == "__main__":
    main()
