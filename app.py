"""
Pinterest Automation Bot - Fixed Version
"""

import gradio as gr
import os
import logging
import tempfile
import shutil
import stat
from pathlib import Path
import datetime
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_executable_permissions():
    """Ensure Chrome binary and ChromeDriver have executable permissions"""
    try:
        # Define paths to executables
        chrome_binary = Path("chrome_portable/chrome")
        chromedriver_binary = Path("drivers/chromedriver")
        
        # Set executable permissions if files exist
        if chrome_binary.exists():
            current_permissions = chrome_binary.stat().st_mode
            chrome_binary.chmod(current_permissions | stat.S_IEXEC | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            logger.info(f"Set executable permission for: {chrome_binary}")
        else:
            logger.warning(f"Chrome binary not found: {chrome_binary}")
            
        if chromedriver_binary.exists():
            current_permissions = chromedriver_binary.stat().st_mode
            chromedriver_binary.chmod(current_permissions | stat.S_IEXEC | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            logger.info(f"Set executable permission for: {chromedriver_binary}")
        else:
            logger.warning(f"ChromeDriver not found: {chromedriver_binary}")
            
    except Exception as e:
        logger.error(f"Failed to set executable permissions: {str(e)}")

def upload_pin(email, password, image, title, description, board_name, link_url, headless):
    """Main function to upload a pin to Pinterest"""
    
    # Input validation
    if not email or not password:
        return "❌ Please enter your Pinterest email and password"
    
    if not image:
        return "❌ Please upload an image"
    
    if not title or not description or not board_name:
        return "❌ Please fill in title, description, and board name"
    
    # Validate URL format if provided
    if link_url:
        # Simple URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(link_url):
            return "❌ Please enter a valid URL (starting with http:// or https://)"
    
    # Create uploads directory if it doesn't exist
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    
    # Generate unique filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    image_extension = Path(image).suffix or '.jpg'
    stored_image_name = f"upload_{timestamp}{image_extension}"
    stored_image_path = uploads_dir / stored_image_name
    
    try:
        # Test if our modules can be imported
        logger.info("Importing Pinterest automation module...")
        from pinterest_automation_portable import PortablePinterestAutomation
        
        logger.info("Starting Pinterest automation...")
        
        # Initialize automation
        pinterest = PortablePinterestAutomation(headless=headless, fast_typing=True)
        
        # Setup driver
        logger.info("Setting up Chrome driver...")
        if not pinterest._setup_driver():
            return "❌ Failed to setup Chrome driver. Please try again."
        
        try:
            # Ensure Chrome and ChromeDriver have executable permissions
            ensure_executable_permissions()
            
            # Store image in uploads directory
            shutil.copy2(image, stored_image_path)
            logger.info(f"Image stored at: {stored_image_path}")
            
            # Login
            if not pinterest.login(email, password):
                return "❌ Login failed. Please check your credentials."
            
            # Create temp directory for processing
            temp_dir = tempfile.mkdtemp()
            temp_image_path = os.path.join(temp_dir, "uploaded_image.jpg")
            shutil.copy2(image, temp_image_path)
            
            # Upload image
            if not pinterest.upload_image(temp_image_path):
                return "❌ Failed to upload image."
            
            # Set pin details
            if not pinterest.set_title(title):
                return "❌ Failed to set title."
            
            if not pinterest.set_description(description):
                return "❌ Failed to set description."
            
            # Set optional link (only if valid URL provided)
            if link_url and link_url.strip():
                if not pinterest.set_link(link_url.strip()):
                    return "❌ Failed to set link. Please check the URL format."
            
            # Select board
            if not pinterest.select_board(board_name):
                return "❌ Failed to select board. Make sure it exists in your Pinterest."
            
            # Publish pin
            if not pinterest.publish_pin():
                return "❌ Failed to publish pin. Please check for validation errors."
            
            # Cleanup temp directory
            shutil.rmtree(temp_dir)
            
            # If successful, clean up stored image
            if stored_image_path.exists():
                stored_image_path.unlink()
                logger.info(f"Cleaned up stored image: {stored_image_path}")
            
            return f"✅ Success! Pin '{title}' uploaded to board '{board_name}'"
            
        except Exception as inner_e:
            # If there's an error, keep the stored image for debugging
            logger.error(f"Upload failed, keeping image for debugging: {stored_image_path}")
            return f"❌ Upload failed: {str(inner_e)}. Image saved at {stored_image_path} for debugging."
        finally:
            try:
                pinterest.driver.quit()
            except:
                pass
    
    except ImportError as e:
        return f"❌ Setup error: {str(e)}. Chrome setup is missing."
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return f"❌ Error: {str(e)}"

# Simple interface that should work with Gradio 4.40.0
with gr.Blocks(title="Pinterest Automation Bot") as app:
    
    gr.Markdown("# 📌 Pinterest Automation Bot")
    gr.Markdown("Upload pins to Pinterest automatically with advanced automation.")
    
    # Status indicator
    with gr.Row():
        status_text = gr.Markdown("🟢 **Status**: Ready to upload pins!")
    
    # Login section
    gr.Markdown("### 🔐 Pinterest Login")
    email = gr.Textbox(label="Email", placeholder="your-email@example.com")
    password = gr.Textbox(label="Password", type="password")
    
    # Pin details section
    gr.Markdown("### 📝 Pin Details")
    image = gr.File(label="Image")
    title = gr.Textbox(label="Title", placeholder="Enter pin title...")
    description = gr.Textbox(label="Description", lines=3, placeholder="Enter pin description...")
    board_name = gr.Textbox(label="Board Name", placeholder="Enter existing board name...")
    link_url = gr.Textbox(label="Link (Optional)", placeholder="https://example.com")
    
    # Options
    gr.Markdown("### ⚙️ Options")
    headless = gr.Checkbox(label="Run in headless mode (recommended)", value=True)
    
    # Submit button
    submit_btn = gr.Button("🚀 Upload Pin to Pinterest", variant="primary")
    
    # Output
    result = gr.Textbox(label="Result", lines=3, interactive=False)

    # Event handler
    submit_btn.click(
        upload_pin,
        inputs=[email, password, image, title, description, board_name, link_url, headless],
        outputs=result
    )
    
    gr.Markdown("""
    ### 📖 Instructions
    1. Enter your Pinterest credentials
    2. Upload an image (PNG, JPG, GIF, WebP)
    3. Fill in pin details (title, description, board name)
    4. Optionally add a destination link
    5. Click "Upload Pin to Pinterest"
    
    **Note**: Board must already exist in your Pinterest account.
    """)

if __name__ == "__main__":
    try:
        logger.info("=== Starting Pinterest Bot Application ===")
        
        # Ensure executable permissions are set
        logger.info("Setting executable permissions...")
        ensure_executable_permissions()
        logger.info("Executable permissions set successfully")
        
        # Check if running on Hugging Face Spaces
        is_spaces = os.getenv('SPACE_ID') is not None
        logger.info(f"Running on Hugging Face Spaces: {is_spaces}")
        
        # For HF Spaces, start the app quickly and do heavy initialization later
        if is_spaces:
            logger.info("Quick launch for HF Spaces...")
            app.queue()  # Enable queuing for better performance
            app.launch(
                server_name="0.0.0.0",
                server_port=7860,
                share=False,
                show_error=True,
                quiet=False,
                favicon_path=None,
                enable_monitoring=False
            )
        else:
            # For local development, do full initialization
            logger.info("Full initialization for local development...")
            
            # Test imports to make sure everything is working
            logger.info("Testing module imports...")
            try:
                from pinterest_automation_portable import PortablePinterestAutomation
                logger.info("✅ Pinterest automation module imported successfully")
            except Exception as e:
                logger.error(f"❌ Failed to import Pinterest automation module: {e}")
            
            try:
                from chrome_wrapper import get_chrome_manager
                logger.info("✅ Chrome wrapper imported successfully")
                
                # Test chrome manager creation (but don't start browser)
                chrome_manager = get_chrome_manager()
                config_info = chrome_manager.get_config_info()
                logger.info(f"✅ Chrome setup verified: {config_info['chrome_binary']}")
            except Exception as e:
                logger.error(f"❌ Failed to setup Chrome wrapper: {e}")
            
            logger.info("Launching Gradio app...")
            app.launch(
                server_name="0.0.0.0",
                server_port=7861,
                share=True,
                show_error=True,
                quiet=False
            )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
