#!/usr/bin/env python3
"""
Startup script for Hugging Face Spaces deployment.
This script automatically sets up the ChromeDriver before starting the main application.
"""

import os
import sys
import subprocess
import logging
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_system_packages():
    """Install system packages from packages.txt"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        packages_file = os.path.join(current_dir, 'packages.txt')
        
        if os.path.exists(packages_file):
            logger.info("Installing system packages from packages.txt...")
            
            # Update package list
            subprocess.run(['sudo', 'apt-get', 'update'], check=True)
            
            # Read packages from file
            with open(packages_file, 'r') as f:
                packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            # Install packages
            if packages:
                cmd = ['sudo', 'apt-get', 'install', '-y'] + packages
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info("System packages installed successfully")
                else:
                    logger.warning(f"Some packages may have failed to install: {result.stderr}")
            
        return True
    except Exception as e:
        logger.error(f"Failed to install system packages: {e}")
        return False

def setup_google_chrome():
    """Ensure Google Chrome is properly installed"""
    try:
        # Check if google-chrome is available
        if shutil.which('google-chrome') or os.path.exists('/usr/bin/google-chrome'):
            logger.info("Google Chrome found")
            return True
        
        logger.info("Google Chrome not found, attempting to install...")
        
        # Install Google Chrome
        try:
            # Add Google's official APT repository
            subprocess.run(['wget', '-q', '-O', '-', 'https://dl.google.com/linux/linux_signing_key.pub'], 
                         stdout=subprocess.PIPE, check=True)
            subprocess.run(['sudo', 'apt-key', 'add', '-'], input='', text=True, check=True)
            
            # Add repository
            with open('/tmp/google-chrome.list', 'w') as f:
                f.write('deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main\n')
            subprocess.run(['sudo', 'mv', '/tmp/google-chrome.list', '/etc/apt/sources.list.d/'], check=True)
            
            # Update and install
            subprocess.run(['sudo', 'apt-get', 'update'], check=True)
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'google-chrome-stable'], check=True)
            
            logger.info("Google Chrome installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install Google Chrome: {e}")
            return False
        
    except Exception as e:
        logger.error(f"Chrome setup failed: {e}")
        return False

def setup_environment():
    """Setup the environment for Pinterest automation"""
    try:
        # Check if Google Chrome is available
        if not (shutil.which('google-chrome') or os.path.exists('/usr/bin/google-chrome')):
            logger.error("Google Chrome not found. Please install Google Chrome.")
            return False
        else:
            logger.info("Google Chrome is available")
        
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
