import streamlit as st
import os
import uuid
from PIL import Image
import logging

# Set mock mode for development
os.environ['USE_MOCK_OPENFABRIC'] = 'true'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Import our local modules
from app.config import TEXT_TO_IMAGE_APP_ID, IMAGE_TO_3D_APP_ID
from app.core.stub import Stub
from app.llm.prompt_enhancer import get_prompt_enhancer
from app.database.memory import get_memory_db

# Set page configuration
st.set_page_config(
    page_title="Text to 3D Generation",
    page_icon="🧊",
    layout="wide"
)

# Create necessary directories
os.makedirs("app/static/images", exist_ok=True)
os.makedirs("app/static/models", exist_ok=True)