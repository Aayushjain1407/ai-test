"""
Configuration file for the AI-Powered Text-to-3D Generation System.
"""

# Openfabric App IDs
TEXT_TO_IMAGE_APP_ID = "f0997a01-d6d3-a5fe-53d8-561300318557"
IMAGE_TO_3D_APP_ID = "69543f29-4d41-4afc-7f29-3d51591f11eb"

# Openfabric API endpoints
OPENFABRIC_BASE_DOMAIN = "node3.openfabric.network"
TEXT_TO_IMAGE_ENDPOINT = f"{TEXT_TO_IMAGE_APP_ID}.{OPENFABRIC_BASE_DOMAIN}"
IMAGE_TO_3D_ENDPOINT = f"{IMAGE_TO_3D_APP_ID}.{OPENFABRIC_BASE_DOMAIN}"

# LLM Settings
LLM_MODEL = "tinyllama"
LLM_TEMPERATURE = 0.7
LLM_MODEL_DIR = "app/models"

# Memory storage path
MEMORY_DB_PATH = "memory.db"
