import os
import sys
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add the project root to the Python path
sys.path.append('/Users/aayushjain/Desktop/ai-test')

try:
    from openfabric_pysdk.starter import Starter
    
    # Get the port from environment variables or use default
    port = int(os.environ.get('PORT', 8888))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logging.info(f"Starting Openfabric app on port {port} with debug={debug}")
    
    # Start the application
    # Work around the SDK bug: convert debug boolean to string to prevent concatenation issues
    Starter.ignite(debug="false", host="0.0.0.0", port=port)
    
except Exception as e:
    logging.error(f"Failed to start the application: {e}")
    logging.error(traceback.format_exc())
    sys.exit(1)
