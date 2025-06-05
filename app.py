import streamlit as st
import requests
import os
import json
import uuid
import time
import base64
from PIL import Image
from io import BytesIO
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import our local services
from app.llm.prompt_enhancer import get_prompt_enhancer
from app.database.memory import get_memory_db
from app.core.stub import Stub
from app.config import TEXT_TO_IMAGE_APP_ID, IMAGE_TO_3D_APP_ID

# Set page configuration
st.set_page_config(
    page_title="Text to 3D Generation",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to ensure directories exist
def ensure_directories():
    os.makedirs("app/static/images", exist_ok=True)
    os.makedirs("app/static/models", exist_ok=True)

# Function to process the generation pipeline
def generate_3d_model(prompt, negative_prompt="blurry, distorted, low quality", steps=25, 
                     width=768, height=768, model_format="glb"):
    try:
        # Generate a unique ID for this generation
        generation_id = str(uuid.uuid4())
        st.session_state['generation_id'] = generation_id
        logger.info(f"Starting generation pipeline with ID: {generation_id}")
        
        # Step 1: Enhance prompt with LLM
        with status_container.info("Enhancing prompt with LLM..."):
            prompt_enhancer = get_prompt_enhancer()
            enhanced_prompt = prompt_enhancer.enhance_prompt(prompt)
            logger.info(f"Enhanced prompt: {enhanced_prompt}")
            st.session_state['enhanced_prompt'] = enhanced_prompt
        
        # Step 2: Generate image from enhanced prompt
        with status_container.info("Generating image from prompt..."):
            text_to_image_params = {
                'prompt': enhanced_prompt,
                'negative_prompt': negative_prompt,
                'steps': steps,
                'width': width,
                'height': height,
            }
            
            # Call the Text-to-Image app
            image_result = Stub.call(
                app_id=TEXT_TO_IMAGE_APP_ID,
                parameters=text_to_image_params
            )
            
            # Extract image from response
            image_data = image_result.get('result', None)
            if not image_data:
                raise ValueError("Text-to-Image service didn't return an image")
                
            # Save the intermediate image
            image_filename = f"output_{generation_id}.png"
            image_path = os.path.join("app/static/images", image_filename)
            with open(image_path, 'wb') as f:
                f.write(image_data)
            logger.info(f"Saved intermediate image to {image_path}")
            st.session_state['image_path'] = image_path
        
        # Step 3: Generate 3D model from image
        with status_container.info("Generating 3D model from image..."):
            image_to_3d_params = {
                'image': image_data,  # Pass the binary image data
                'format': model_format,
            }
            
            # Call the Image-to-3D app
            model_3d_result = Stub.call(
                app_id=IMAGE_TO_3D_APP_ID,
                parameters=image_to_3d_params
            )
            
            # Extract 3D model from response
            model_3d_data = model_3d_result.get('result', None)
            if not model_3d_data:
                raise ValueError("Image-to-3D service didn't return a model")
                
            # Save the 3D model
            model_filename = f"model_{generation_id}.{model_format}"
            model_path = os.path.join("app/static/models", model_filename)
            with open(model_path, 'wb') as f:
                f.write(model_3d_data)
            logger.info(f"Saved 3D model to {model_path}")
            st.session_state['model_path'] = model_path
        
        # Step 4: Store generation metadata in memory
        with status_container.info("Storing generation metadata..."):
            memory_db = get_memory_db()
            metadata = {
                'text_to_image_params': {
                    'prompt': enhanced_prompt,
                    'negative_prompt': negative_prompt,
                    'steps': steps,
                    'width': width,
                    'height': height,
                },
                'image_to_3d_params': {
                    'format': model_format,
                }
            }
            
            # Call the save_generation method
            memory_db.save_generation(
                generation_id=generation_id,
                user_id='streamlit_user',
                prompt=prompt,
                enhanced_prompt=enhanced_prompt,
                image_path=image_path,
                model_3d_path=model_path,
                metadata=metadata
            )
            logger.info(f"Stored generation data in memory database")
        
        return {
            'status': 'success',
            'generation_id': generation_id,
            'prompt': prompt,
            'enhanced_prompt': enhanced_prompt,
            'image_path': image_path,
            'model_path': model_path,
        }
        
    except Exception as e:
        logger.error(f"Error in generation pipeline: {str(e)}")
        status_container.error(f"Error: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
        }

# Function to get previous generations
def get_previous_generations():
    try:
        memory_db = get_memory_db()
        generations = memory_db.list_generations()
        return generations
    except Exception as e:
        logger.error(f"Error retrieving generations: {str(e)}")
        return []

# Function to display image
def display_image(image_path):
    if os.path.exists(image_path):
        image = Image.open(image_path)
        st.image(image, caption="Generated Image", use_column_width=True)
    else:
        st.error(f"Image file not found: {image_path}")

# Function to display 3D model
def display_3d_model(model_path):
    if os.path.exists(model_path):
        with open(model_path, 'rb') as file:
            model_content = file.read()
            
        # Getting file extension
        _, file_extension = os.path.splitext(model_path)
        file_extension = file_extension.lower().replace('.', '')
        
        # Display using appropriate viewer
        if file_extension == 'glb':
            st.write("3D GLB Model:")
            st.markdown(f"""
            <div style="height: 400px; border: 1px solid #ccc; padding: 10px;">
                <model-viewer 
                    src="/app/static/models/{os.path.basename(model_path)}" 
                    alt="3D model"
                    auto-rotate 
                    camera-controls 
                    style="width: 100%; height: 100%;">
                </model-viewer>
            </div>
            <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.1.1/model-viewer.min.js"></script>
            """, unsafe_allow_html=True)
            
            # Download button for model
            st.download_button(
                label="Download 3D Model",
                data=model_content,
                file_name=os.path.basename(model_path),
                mime="application/octet-stream"
            )
        else:
            st.write(f"3D Model ({file_extension.upper()}):")
            st.info("Preview not available for this file type. You can download the file below.")
            st.download_button(
                label="Download 3D Model",
                data=model_content,
                file_name=os.path.basename(model_path),
                mime="application/octet-stream"
            )
    else:
        st.error(f"Model file not found: {model_path}")

# Ensure directories exist
ensure_directories()

# Initialize session state
if 'generation_id' not in st.session_state:
    st.session_state['generation_id'] = None
if 'image_path' not in st.session_state:
    st.session_state['image_path'] = None
if 'model_path' not in st.session_state:
    st.session_state['model_path'] = None
if 'enhanced_prompt' not in st.session_state:
    st.session_state['enhanced_prompt'] = None
if 'mock_mode' not in st.session_state:
    st.session_state['mock_mode'] = os.environ.get('USE_MOCK_OPENFABRIC', 'false').lower() == 'true'

# Title and description
st.title("Text to 3D Generation Pipeline")
st.markdown("""
This application generates 3D models from text descriptions using a pipeline:
1. Enhance your text prompt using a local LLM
2. Generate an image from the enhanced prompt
3. Create a 3D model from the image
""")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    # Toggle mock mode
    mock_mode = st.checkbox("Use mock mode", value=st.session_state['mock_mode'])
    if mock_mode != st.session_state['mock_mode']:
        st.session_state['mock_mode'] = mock_mode
        os.environ['USE_MOCK_OPENFABRIC'] = str(mock_mode).lower()
    
    st.markdown("---")
    
    # Advanced settings
    st.subheader("Advanced Settings")
    negative_prompt = st.text_area("Negative prompt", "blurry, distorted, low quality", help="Characteristics to avoid in the image")
    
    col1, col2 = st.columns(2)
    with col1:
        steps = st.slider("Diffusion steps", 10, 50, 25, help="More steps = higher quality but slower")
    with col2:
        model_format = st.selectbox("3D Model format", ["glb", "obj", "stl"], help="Format of the 3D model output")
    
    col3, col4 = st.columns(2)
    with col3:
        width = st.slider("Image width", 256, 1024, 768, 64, help="Width of generated image")
    with col4:
        height = st.slider("Image height", 256, 1024, 768, 64, help="Height of generated image")

# Main content area
col_input, col_result = st.columns([1, 2])

with col_input:
    st.header("Text Input")
    
    # Text input for prompt
    prompt = st.text_area("Enter your prompt", "A futuristic space station orbiting Earth", 
                         help="Describe what you want to generate as a 3D model", height=150)
    
    # Generation button
    status_container = st.container()
    if st.button("Generate 3D Model", type="primary", use_container_width=True):
        with status_container:
            with st.spinner("Processing your request..."):
                result = generate_3d_model(
                    prompt=prompt, 
                    negative_prompt=negative_prompt,
                    steps=steps,
                    width=width,
                    height=height,
                    model_format=model_format
                )
                
                if result['status'] == 'success':
                    st.success("Generation completed successfully!")
                else:
                    st.error(f"Generation failed: {result.get('error', 'Unknown error')}")
    
    # Show history
    st.header("Previous Generations")
    generations = get_previous_generations()
    
    if not generations:
        st.info("No previous generations found")
    else:
        for gen in generations[:5]:  # Show last 5 generations
            with st.expander(f"{gen['prompt'][:50]}..."):
                st.write(f"**ID:** {gen['generation_id']}")
                st.write(f"**Generated:** {gen['timestamp']}")
                if st.button("Load", key=f"load_{gen['generation_id']}"):
                    st.session_state['generation_id'] = gen['generation_id']
                    st.session_state['image_path'] = gen['image_path']
                    st.session_state['model_path'] = gen['model_3d_path']
                    st.session_state['enhanced_prompt'] = gen['enhanced_prompt']
                    st.experimental_rerun()

with col_result:
    st.header("Results")
    
    if st.session_state['generation_id']:
        st.subheader("Generated Content")
        
        # Display original and enhanced prompts
        if st.session_state['enhanced_prompt']:
            with st.expander("View Prompts"):
                st.write("**Original Prompt:**")
                st.info(prompt if 'prompt' in locals() else "N/A")
                st.write("**Enhanced Prompt:**")
                st.info(st.session_state['enhanced_prompt'])
        
        # Create tabs for image and 3D model
        tab_image, tab_model = st.tabs(["Generated Image", "3D Model"])
        
        with tab_image:
            if st.session_state['image_path']:
                display_image(st.session_state['image_path'])
            else:
                st.info("No image generated yet")
        
        with tab_model:
            if st.session_state['model_path']:
                display_3d_model(st.session_state['model_path'])
            else:
                st.info("No 3D model generated yet")
    else:
        st.info("Enter a prompt and click 'Generate 3D Model' to get started")

# Footer
st.markdown("---")
st.caption("Powered by Openfabric AI and TinyLlama")
