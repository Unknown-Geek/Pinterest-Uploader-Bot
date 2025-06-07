import gradio as gr
import logging
import os
import tempfile
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

def upload_to_pinterest(email, password, image, title, description, board_name, link_url=""):
    """
    Upload a pin to Pinterest using the automation bot
    
    Args:
        email (str): Pinterest email
        password (str): Pinterest password
        image (PIL.Image): The image to upload
        title (str): Pin title
        description (str): Pin description
        board_name (str): Board name to save the pin to
        link_url (str): Optional destination link
    
    Returns:
        tuple: (success_message, log_output)
    """
    try:
        logger.info("Starting Pinterest upload process...")
        
        # Validate inputs
        if not email or not password:
            return "❌ Error: Email and password are required", "Missing credentials"
            
        if not image:
            return "❌ Error: Image is required", "No image provided"
            
        if not title or not description or not board_name:
            return "❌ Error: Title, description, and board name are required", "Missing required fields"
        
        # Save the uploaded image to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            image.save(temp_file.name, 'PNG')
            temp_image_path = temp_file.name
        
        logger.info(f"Image saved to temporary file: {temp_image_path}")
        
        # Create Pinterest automation instance
        pinterest_bot = PinterestAutomation(headless=True, fast_typing=True)
        
        # Upload the pin
        result = pinterest_bot.upload_pin(
            email=email,
            password=password,
            image_path=temp_image_path,
            title=title,
            description=description,
            board_name=board_name,
            link_url=link_url if link_url else None
        )
        
        # Clean up temporary file
        try:
            os.unlink(temp_image_path)
            logger.info("Temporary file cleaned up")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary file: {e}")
        
        # Format response
        if result['success']:
            success_msg = f"✅ {result['message']}"
            if result.get('pin_url'):
                success_msg += f"\n🔗 Pin URL: {result['pin_url']}"
            return success_msg, "Upload completed successfully"
        else:
            return f"❌ {result['message']}", "Upload failed"
            
    except Exception as e:
        logger.error(f"Error in upload_to_pinterest: {str(e)}")
        return f"❌ Unexpected error: {str(e)}", f"Exception: {str(e)}"

def upload_pin_api(email, password, image, title, description, board_name, link_url=None):
    # Save uploaded image to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_img:
        temp_img.write(image.read())
        temp_img_path = temp_img.name
    
    bot = PinterestAutomation(headless=True)
    result = bot.upload_pin(
        email=email,
        password=password,
        image_path=temp_img_path,
        title=title,
        description=description,
        board_name=board_name,
        link_url=link_url
    )
    os.remove(temp_img_path)
    return result

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
            <p>Automatically upload pins to Pinterest with AI-powered automation</p>
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
                    placeholder="Name of the board to save the pin to"
                )
                
                link_url = gr.Textbox(
                    label="Destination Link (Optional)",
                    placeholder="https://your-website.com",
                    type="url"
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
           - Board Name: Exact name of your Pinterest board
           - Link (Optional): URL where users should go when they click your pin
        4. **Click "Upload to Pinterest"** and wait for the process to complete
        
        **Note**: Make sure your board name matches exactly with your Pinterest board names.
        """)
        
        gr.Markdown("### ⚠️ Important Notes")
        gr.Markdown("""
        - This tool uses browser automation to upload pins
        - Keep your credentials secure - they are only used during the session
        - The process may take 30-60 seconds to complete
        - Make sure your Pinterest account has the specified board created
        - For best results, use high-quality images (recommended: 1000x1500px or 2:3 ratio)
        """)
    
    return interface

# Create the interface
iface = create_interface()

if __name__ == "__main__":
    # Launch the app
    iface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        debug=False,
        show_error=True,
        quiet=False
    )
