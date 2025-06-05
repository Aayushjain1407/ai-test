import json
import logging
import os
from typing import Any, Dict, List, Optional

import requests
from openfabric_pysdk.loader import OutputSchemaInst

from openfabric_pysdk.helper import has_resource_fields, json_schema_to_marshmallow, resolve_resources

# Configure logging
logging.basicConfig(
    level=logging.INFO if os.environ.get("DEBUG") else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Type aliases for clarity
Manifests = Dict[str, dict]
Schemas = Dict[str, tuple[dict, dict]]

class Stub:
    """
    Stub for interacting with Openfabric apps
    """
    
    def __init__(self, app_ids: List[str]):
        """
        Initialize the Stub with a list of Openfabric app IDs
        
        Args:
            app_ids: List of Openfabric app IDs to connect to
        """
        self._schema: Schemas = {}
        self._manifest: Manifests = {}
        self._connections: Dict[str, Any] = {}
        
        # Default app IDs if none provided
        if not app_ids:
            app_ids = [
                "f0997a01-d6d3-a5fe-53d8-561300318557",  # Text-to-Image
                "69543f29-4d41-4afc-7f29-3d51591f11eb"   # Image-to-3D
            ]
        
        for app_id in app_ids:
            try:
                base_url = f"https://{app_id}.node3.openfabric.network"
                
                # Fetch manifest
                manifest = requests.get(f"{base_url}/manifest", timeout=10).json()
                logger.info(f"[{app_id}] Manifest loaded")
                self._manifest[app_id] = manifest
                
                # Fetch schemas
                input_schema = requests.get(f"{base_url}/schema?type=input", timeout=10).json()
                output_schema = requests.get(f"{base_url}/schema?type=output", timeout=10).json()
                self._schema[app_id] = (input_schema, output_schema)
                
                logger.info(f"[{app_id}] Initialized successfully")
                
            except Exception as e:
                logger.error(f"[{app_id}] Initialization failed: {str(e)}")
                raise
    
    @classmethod
    def call(cls, app_id: str, parameters: dict = None, uid: str = 'super-user') -> dict:
        """
        Call an Openfabric app with the given parameters
        
        Args:
            app_id: The Openfabric app ID to call
            parameters: Parameters for the app
            uid: User ID for the request
            
        Returns:
            dict: The response from the app
        """
        try:
            if parameters is None:
                parameters = {}
                
            base_url = f"https://{app_id}.node3.openfabric.network"
            
            # Prepare the request data
            request_data = {
                "request": parameters,
                "uid": uid
            }
            
            # Make the API call
            response = requests.post(
                f"{base_url}/execute",
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Handle binary data in the response
            if isinstance(result, dict) and 'result' in result and isinstance(result['result'], dict):
                if 'resource' in result['result']:
                    # Fetch the binary resource
                    resource_url = f"{base_url}/resource?reid={result['result']['resource']}"
                    resource_response = requests.get(resource_url)
                    resource_response.raise_for_status()
                    return {'result': resource_response.content}
            
            return result
            
        except Exception as e:
            logger.error(f"Error calling Openfabric app {app_id}: {str(e)}")
            raise