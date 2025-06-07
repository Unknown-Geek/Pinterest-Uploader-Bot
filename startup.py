#!/usr/bin/env python3
"""
Startup script for Render deployment.
This script automatically sets up the environment before starting the main application.
"""

import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_system_packages():
    """Install required system packages on Render"""
    try:
        # Check if we're on a system with apt-get (like Render)
        if os.path.exists('/usr/bin/apt-get'):
            logger.info("Installing system packages...")
            
            # Update package list
            subprocess.run(['apt-get', 'update'], check=False, capture_output=True)
            
            # Install required packages
            packages = [
                'chromium-browser',
                'chromium-chromedriver', 
                'fonts-liberation',
                'libappindicator3-1',
                'libasound2',
                'libatk-bridge2.0-0',
                'libatspi2.0-0',
                'libdrm2',
                'libgtk-3-0',
                'libnspr4',
                'libnss3',
                'libxcomposite1',
                'libxdamage1',
                'libxrandr2',
                'libgbm1',
                'libxss1',
                'xvfb'
            ]
            
            # Install packages individually to avoid failures
            for package in packages:
                try:
                    result = subprocess.run(['apt-get', 'install', '-y', package], 
                                          check=False, capture_output=True, text=True)
                    if result.returncode == 0:
                        logger.info(f"Installed {package}")
                    else:
                        logger.warning(f"Failed to install {package}: {result.stderr}")
                except Exception as e:
                    logger.warning(f"Error installing {package}: {e}")
            
            logger.info("System packages installation completed")
            
    except Exception as e:
        logger.warning(f"Could not install system packages: {e}")

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
        
        # Launch the Gradio interface
        app.iface.launch(
            server_name="0.0.0.0",
            server_port=int(os.environ.get("PORT", 7860)),
            share=True,
            debug=False,
            show_error=True,
            quiet=False
        )
        
    except ImportError as e:
        logger.error(f"Failed to import main application: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
