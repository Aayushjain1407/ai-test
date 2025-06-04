import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add the project directory to the Python path
sys.path.append('/Users/aayushjain/Desktop/ai-test')

# Try to import the necessary components
try:
    from app.main import execute, config
    from openfabric_pysdk.context import AppModel
    from onto.dc8f06af066e4a7880a5938933236037.input import InputClass
    from onto.dc8f06af066e4a7880a5938933236037.output import OutputClass
    
    # Create a simple test model
    model = AppModel()
    model.request = InputClass()
    model.request.prompt = "Test prompt"
    model.response = OutputClass()
    
    # Execute the model
    logging.info("Executing the model...")
    execute(model)
    
    # Print the response
    logging.info(f"Response: {model.response.message}")
    
except Exception as e:
    logging.error(f"Error: {e}")
    import traceback
    traceback.print_exc()
