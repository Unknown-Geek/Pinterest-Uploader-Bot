#!/usr/bin/env python3
"""
Startup script for Hugging Face Spaces deployment.
This script automatically sets up the ChromeDriver before starting the main application.
"""

import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup the environment for Pinterest automation"""
    try:
        # Add current directory to Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        # Check if ChromeDriver exists
        chromedriver_path = os.path.join(current_dir, 'drivers', 'chromedriver')
        
        if not os.path.exists(chromedriver_path):
            logger.info("ChromeDriver not found, setting up...")
            
            # Run setup script
            setup_script = os.path.join(current_dir, 'setup_chromedriver.py')
            if os.path.exists(setup_script):
                result = subprocess.run([sys.executable, setup_script], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info("ChromeDriver setup completed successfully")
                else:
                    logger.error(f"ChromeDriver setup failed: {result.stderr}")
                    return False
            else:
                logger.error("ChromeDriver setup script not found")
                return False
        else:
            logger.info("ChromeDriver already exists")
        
        # Verify ChromeDriver is working
        try:
            result = subprocess.run([chromedriver_path, '--version'], 
                                  capture_output=True, text=True, check=True)
            logger.info(f"ChromeDriver ready: {result.stdout.strip()}")
        except subprocess.CalledProcessError:
            logger.error("ChromeDriver verification failed")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Environment setup failed: {e}")
        return False

def main():
    """Main startup function"""
    logger.info("Starting Pinterest Uploader Bot...")
    
    # Setup environment
    if not setup_environment():
        logger.error("Environment setup failed, exiting...")
        sys.exit(1)
    
    # Import and run the main application
    try:
        import app
        logger.info("Starting Gradio application...")
        # The app.py file should contain the Gradio interface
    except ImportError as e:
        logger.error(f"Failed to import main application: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
