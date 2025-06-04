import sys
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add the project root to the Python path
sys.path.append('/Users/aayushjain/Desktop/ai-test')

# Import our classes for the ontology
from onto.dc8f06af066e4a7880a5938933236037.config import ConfigClass
from onto.dc8f06af066e4a7880a5938933236037.input import InputClass
from onto.dc8f06af066e4a7880a5938933236037.output import OutputClass

# Import Stub class
from app.core.stub import Stub

def main():
    try:
        # Create a test input
        input_obj = InputClass()
        input_obj.prompt = "Make me a glowing dragon standing on a cliff at sunset."
        
        # Create a test output
        output_obj = OutputClass()
        
        # Create config with app IDs
        config = ConfigClass()
        config.app_ids = [
            'f0997a01-d6d3-a5fe-53d8-561300318557',  # Text to Image app
            '69543f29-4d41-4afc-7f29-3d51591f11eb'   # Image to 3D app
        ]
        
        logging.info("Initializing Openfabric Stub with app IDs...")
        stub = Stub(config.app_ids)
        
        # Skip calling the apps for now, just test the setup
        logging.info("Test initialization successful")
        logging.info(f"App IDs loaded: {config.app_ids}")
        
        # In a real implementation, you would call the text-to-image API followed by image-to-3D API
        # Example (commented out for now):
        # response = stub.call('f0997a01-d6d3-a5fe-53d8-561300318557', {'prompt': input_obj.prompt}, 'super-user')
        
        output_obj.message = f"Echo: {input_obj.prompt}"
        logging.info(f"Response message: {output_obj.message}")
        
    except Exception as e:
        logging.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
