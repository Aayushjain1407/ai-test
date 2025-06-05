import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_connection(app_id):
    """Test connection to Openfabric node."""
    base_url = f"https://{app_id}.node3.openfabric.network"
    
    try:
        # Test manifest endpoint
        manifest_url = f"{base_url}/manifest"
        logger.info(f"Testing connection to {manifest_url}")
        response = requests.get(manifest_url, timeout=10)
        response.raise_for_status()
        logger.info(f"Manifest response: {response.json()}")
        
        # Test schema endpoint
        schema_url = f"{base_url}/schema?type=input"
        logger.info(f"Testing connection to {schema_url}")
        response = requests.get(schema_url, timeout=10)
        response.raise_for_status()
        logger.info("Schema endpoint is accessible")
        
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Connection test failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Status code: {e.response.status_code}")
            logger.error(f"Response: {e.response.text}")
        return False

if __name__ == "__main__":
    # Test with the text-to-image app ID
    app_id = "f0997a01-d6d3-a5fe-53d8-561300318557"
    logger.info(f"Testing connection to Openfabric app: {app_id}")
    success = test_connection(app_id)
    logger.info(f"Connection test {'succeeded' if success else 'failed'}")
