import gradio as gr
import logging
import os
import tempfile
import atexit
from PIL import Image
from pinterest_automation import PinterestAutomation

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pinterest_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Global Pinterest bot instance for persistent session
global_pinterest_bot = None
current_credentials = {"email": None, "password": None}

def get_or_create_pinterest_bot(email, password):
    """Get existing Pinterest bot or create a new one with login"""
    global global_pinterest_bot, current_credentials
    
    try:
        # Check if we need to create a new bot or login with different credentials
        need_new_bot = (
            global_pinterest_bot is None or 
            current_credentials["email"] != email or 
            current_credentials["password"] != password or
            not hasattr(global_pinterest_bot, 'driver') or
            global_pinterest_bot.driver is None
        )
        
        if need_new_bot:
            logger.info("Creating new Pinterest bot session...")
            
            # Clean up existing bot if any
            if global_pinterest_bot:
                try:
                    global_pinterest_bot.quit()
                except:
                    pass
            
            # Create new bot and login
            global_pinterest_bot = PinterestAutomation(headless=True, fast_typing=True)
            
            # Initialize driver
            if not global_pinterest_bot._setup_driver():
                raise Exception("Failed to initialize browser driver")
            
            # Login to Pinterest
            if not global_pinterest_bot.login(email, password):
                raise Exception("Failed to login to Pinterest. Please check your credentials.")
            
            # Store current credentials
            current_credentials["email"] = email
            current_credentials["password"] = password
            
            logger.info("✅ Pinterest bot session created and logged in successfully!")
        else:
            logger.info("♻️ Reusing existing Pinterest bot session")
        
        return global_pinterest_bot
        
    except Exception as e:
        logger.error(f"Error creating/getting Pinterest bot: {str(e)}")
        # Clean up on error
        if global_pinterest_bot:
            try:
                global_pinterest_bot.quit()
            except:
                pass
            global_pinterest_bot = None
        current_credentials = {"email": None, "password": None}
        raise

def cleanup_pinterest_bot():
    """Clean up the global Pinterest bot"""
    global global_pinterest_bot, current_credentials
    
    if global_pinterest_bot:
        try:
            logger.info("🧹 Cleaning up Pinterest bot session...")
            global_pinterest_bot.quit()
        except Exception as e:
            logger.warning(f"Error during cleanup: {str(e)}")
        finally:
            global_pinterest_bot = None
            current_credentials = {"email": None, "password": None}

# Register cleanup function to run on app shutdown
atexit.register(cleanup_pinterest_bot)

def upload_to_pinterest(email, password, image, title, description, board_name, link_url=""):
    """
    Upload a pin to Pinterest using the automation bot
    
    Args:
        email (str): Pinterest email
        password (str): Pinterest password
        image (PIL.Image): The image to upload
        title (str): Pin title
        description (str): Pin description
        link_url (str): Optional destination link
    
    Returns:
        tuple: (success_message, log_output)
    """
    temp_image_path = None
    
    try:
        logger.info("Starting Pinterest upload process...")
        
        # Validate inputs
        if not email or not password:
            return "❌ Error: Email and password are required", "Missing credentials"
            
        if not image:
            return "❌ Error: Image is required", "No image provided"
            
        if not title or not description:
            return "❌ Error: Title and description are required", "Missing required fields"

        # Save the uploaded image to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            image.save(temp_file.name, 'PNG')
            temp_image_path = temp_file.name
        
        logger.info(f"Image saved to temporary file: {temp_image_path}")
        
        # Get or create Pinterest automation instance (with persistent session)
        pinterest_bot = get_or_create_pinterest_bot(email, password)
        
        # Use the upload_pin_with_session method for already logged-in sessions
        result = pinterest_bot.upload_pin_with_session(
            image_path=temp_image_path,
            title=title,
            description=description,
            board_name=board_name or "My Pins",  # Use provided board name or default
            link_url=link_url if link_url and link_url.strip() else None
        )
        
        if result['success']:
            message = f"✅ {result['message']}"
            if result.get('pin_url'):
                message += f"\n🔗 Pin URL: {result['pin_url']}"
            return message, "Upload completed successfully"
        else:
            return f"❌ {result['message']}", f"Upload failed: {result['message']}"
            
    except Exception as e:
        logger.error(f"Error in upload_to_pinterest: {str(e)}")
        return f"❌ Unexpected error: {str(e)}", f"Exception: {str(e)}"
    
    finally:
        # Clean up temporary image file
        if temp_image_path and os.path.exists(temp_image_path):
            try:
                os.unlink(temp_image_path)
                logger.info("Temporary file cleaned up")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file: {e}")
        
        # Note: We don't quit the Pinterest bot here anymore - it stays persistent

def create_interface():
    """Create and configure the Gradio interface"""
    
    # Custom CSS for better styling
    css = """
    .container {
        max-width: 800px;
        margin: 0 auto;
    }
    .header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .success {
        color: #28a745;
        font-weight: bold;
    }
    .error {
        color: #dc3545;
        font-weight: bold;
    }
    """
    
    with gr.Blocks(css=css, title="Pinterest Auto-Publisher") as interface:
        gr.HTML("""
        <div class="header">
            <h1>🎯 Pinterest Auto-Publisher</h1>
            <p>Automatically upload pins to Pinterest with browser automation</p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 📝 Pinterest Credentials")
                email = gr.Textbox(
                    label="Pinterest Email",
                    placeholder="your-email@example.com",
                    type="email"
                )
                password = gr.Textbox(
                    label="Pinterest Password",
                    placeholder="Your Pinterest password",
                    type="password"
                )
                
                gr.Markdown("### 🖼️ Pin Content")
                image = gr.Image(
                    label="Upload Image",
                    type="pil",
                    height=300
                )
                
                title = gr.Textbox(
                    label="Pin Title",
                    placeholder="Enter a catchy title for your pin",
                    max_lines=2
                )
                
                description = gr.Textbox(
                    label="Pin Description",
                    placeholder="Describe your pin in detail...",
                    lines=4
                )
                
                board_name = gr.Textbox(
                    label="Board Name",
                    placeholder="My Pins",
                    value="My Pins"
                )
                
                link_url = gr.Textbox(
                    label="Destination Link (Optional)",
                    placeholder="https://your-website.com",
                    type="text"
                )
        
        with gr.Row():
            upload_btn = gr.Button(
                "🚀 Upload to Pinterest",
                variant="primary",
                size="lg"
            )
            clear_btn = gr.Button(
                "🗑️ Clear Form",
                variant="secondary"
            )
        
        with gr.Row():
            output = gr.Textbox(
                label="Upload Status",
                lines=3,
                interactive=False
            )
            logs = gr.Textbox(
                label="Process Logs",
                lines=2,
                interactive=False,
                visible=False  # Hidden by default
            )
        
        # Button event handlers
        upload_btn.click(
            fn=upload_to_pinterest,
            inputs=[email, password, image, title, description, board_name, link_url],
            outputs=[output, logs],
            show_progress=True
        )
        
        clear_btn.click(
            fn=lambda: ("", "", None, "", "", "", "", "", ""),
            outputs=[email, password, image, title, description, board_name, link_url, output, logs]
        )
        
        # Add examples section
        gr.Markdown("### 📖 Usage Instructions")
        gr.Markdown("""
        1. **Enter your Pinterest credentials** (email and password)
        2. **Upload an image** for your pin (PNG, JPG, etc.)
        3. **Fill in the pin details**:
           - Title: A catchy, descriptive title
           - Description: Detailed description with relevant keywords
           - Link (Optional): URL where users should go when they click your pin
        4. **Click "Upload to Pinterest"** and wait for the process to complete
        
        **Note**: The automation will handle saving to a board automatically.
        """)
        
        gr.Markdown("### ⚠️ Important Notes")
        gr.Markdown("""
        - This tool uses browser automation to upload pins
        - Keep your credentials secure - they are only used during the session
        - The process may take 30-60 seconds to complete
        - A browser window will open during the upload process
        - For best results, use high-quality images (recommended: 1000x1500px or 2:3 ratio)
        """)
    
    return interface

# Create the interface
iface = create_interface()

if __name__ == "__main__":
    # Launch the app
    iface.launch(
        server_name="0.0.0.0",
        share=True,
        debug=False,
        show_error=True,
        quiet=False
    )
