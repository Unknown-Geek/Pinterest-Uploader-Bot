#!/usr/bin/env python3
"""
Minimal Gradio test to debug the TypeError issue
"""

import gradio as gr
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_function(text_input):
    """Simple test function"""
    return f"You entered: {text_input}"

def create_minimal_interface():
    """Create a minimal interface to test Gradio functionality"""
    
    try:
        logger.info("Creating minimal Gradio interface...")
        
        with gr.Blocks(title="Test Interface") as interface:
            gr.HTML("<h1>Test Interface</h1>")
            
            with gr.Row():
                text_input = gr.Textbox(
                    label="Test Input",
                    placeholder="Enter some text"
                )
                
            with gr.Row():
                submit_btn = gr.Button("Submit", variant="primary")
                
            with gr.Row():
                output = gr.Textbox(
                    label="Output",
                    interactive=False
                )
            
            # Button event
            submit_btn.click(
                fn=test_function,
                inputs=[text_input],
                outputs=[output]
            )
        
        logger.info("✅ Minimal interface created successfully")
        return interface
        
    except Exception as e:
        logger.error(f"❌ Error creating interface: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    try:
        logger.info(f"Testing Gradio version: {gr.__version__}")
        iface = create_minimal_interface()
        
        logger.info("Launching interface...")
        iface.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=False,
            debug=True,
            show_error=True
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to launch: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
