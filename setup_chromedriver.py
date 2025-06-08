#!/usr/bin/env python3
"""
Setup script to download and configure ChromeDriver with hardcoded version
matching the Chrome version for maximum compatibility.
"""

import os
import subprocess
import requests
import zipfile
import tempfile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hardcoded versions for maximum compatibility
CHROME_VERSION = "131.0.6778.87"
CHROMEDRIVER_VERSION = "131.0.6778.87"

def get_chromedriver_url():
    """Get the download URL for the hardcoded ChromeDriver version"""
    # Use Chrome for Testing API with hardcoded version
    chromedriver_url = f"https://storage.googleapis.com/chrome-for-testing-public/{CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip"
    logger.info(f"Using hardcoded ChromeDriver version {CHROMEDRIVER_VERSION}")
    return chromedriver_url

def download_and_install_chromedriver(url, install_dir):
    """Download and install ChromeDriver"""
    try:
        logger.info(f"Downloading ChromeDriver from: {url}")
        
        # Create drivers directory if it doesn't exist
        os.makedirs(install_dir, exist_ok=True)
        
        # Download ChromeDriver
        response = requests.get(url)
        response.raise_for_status()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
            temp_file.write(response.content)
            temp_zip_path = temp_file.name
        
        # Extract ChromeDriver
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            # Handle the new Chrome for Testing archive structure
            files = zip_ref.namelist()
            chromedriver_file = None
            
            # Look for chromedriver-linux64/chromedriver
            for file in files:
                if file == 'chromedriver-linux64/chromedriver':
                    chromedriver_file = file
                    break
            
            if not chromedriver_file:
                logger.error("chromedriver executable not found in archive")
                logger.error(f"Available files: {files}")
                return False
            
            # Extract the chromedriver file
            zip_ref.extract(chromedriver_file, install_dir)
            
            # Move to the correct location
            extracted_path = os.path.join(install_dir, chromedriver_file)
            target_path = os.path.join(install_dir, 'chromedriver')
            
            # Remove existing target if it exists
            if os.path.exists(target_path):
                os.remove(target_path)
            
            # Move the extracted binary to the target location
            os.rename(extracted_path, target_path)
            
            # Make executable
            os.chmod(target_path, 0o755)
            
            # Clean up temp file
            os.unlink(temp_zip_path)
            
            # Clean up extracted directory
            chromedriver_dir = os.path.join(install_dir, 'chromedriver-linux64')
            if os.path.exists(chromedriver_dir):
                import shutil
                shutil.rmtree(chromedriver_dir)
            
            logger.info(f"✅ ChromeDriver installed to: {target_path}")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to download and install ChromeDriver: {e}")
        return False

def main():
    """Main setup function"""
    logger.info(f"Setting up ChromeDriver version {CHROMEDRIVER_VERSION} to match Chrome {CHROME_VERSION}")
    
    # Get current directory and set up paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    drivers_dir = os.path.join(current_dir, 'drivers')
    
    # Get ChromeDriver download URL
    chromedriver_url = get_chromedriver_url()
    if not chromedriver_url:
        logger.error("Cannot determine ChromeDriver download URL")
        return False
    
    # Download and install ChromeDriver
    success = download_and_install_chromedriver(chromedriver_url, drivers_dir)
    
    if success:
        # Verify installation
        chromedriver_path = os.path.join(drivers_dir, 'chromedriver')
        try:
            result = subprocess.run([chromedriver_path, '--version'], 
                                  capture_output=True, text=True, check=True)
            logger.info(f"ChromeDriver verification: {result.stdout.strip()}")
            logger.info("✅ Setup completed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ ChromeDriver verification failed: {e}")
            return False
    else:
        logger.error("❌ Setup failed")
        return False

if __name__ == '__main__':
    main()
