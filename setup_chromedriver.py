#!/usr/bin/env python3
"""
Setup script to download and configure the correct ChromeDriver version
for the installed Google Chrome browser.
"""

import os
import subprocess
import requests
import zipfile
import tempfile
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_chrome_version():
    """Get the installed Chrome version"""
    try:
        # Try Google Chrome first
        result = subprocess.run(['google-chrome', '--version'], 
                              capture_output=True, text=True, check=True)
        version = result.stdout.strip().split()[-1]
        logger.info(f"Found Google Chrome version: {version}")
        return version
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # Fallback to Chromium
            result = subprocess.run(['chromium-browser', '--version'], 
                                  capture_output=True, text=True, check=True)
            version = result.stdout.strip().split()[-1]
            logger.info(f"Found Chromium version: {version}")
            return version
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Neither Google Chrome nor Chromium found")
            return None

def get_chromedriver_url(chrome_version):
    """Get the download URL for the matching ChromeDriver version"""
    try:
        # For Chrome/ChromeDriver 115 and above, use the new Chrome for Testing API
        major_version = int(chrome_version.split('.')[0])
        
        if major_version >= 115:
            # Use Chrome for Testing API
            api_url = f"https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
            
            # Find exact version match
            for version_info in data['versions']:
                if version_info['version'] == chrome_version:
                    for download in version_info['downloads'].get('chromedriver', []):
                        if download['platform'] == 'linux64':
                            return download['url']
            
            # If exact version not found, try the closest version
            logger.warning(f"Exact version {chrome_version} not found, trying latest stable")
            latest_url = f"https://storage.googleapis.com/chrome-for-testing-public/LATEST_RELEASE_{major_version}"
            response = requests.get(latest_url)
            if response.status_code == 200:
                latest_version = response.text.strip()
                return f"https://storage.googleapis.com/chrome-for-testing-public/{latest_version}/linux64/chromedriver-linux64.zip"
        else:
            # For older versions, use the old ChromeDriver storage
            return f"https://chromedriver.storage.googleapis.com/{chrome_version}/chromedriver_linux64.zip"
            
    except Exception as e:
        logger.error(f"Error getting ChromeDriver URL: {e}")
        return None

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
            # Handle both old and new archive structures
            files = zip_ref.namelist()
            chromedriver_file = None
            
            for file in files:
                if file.endswith('chromedriver') and not file.endswith('/'):
                    chromedriver_file = file
                    break
            
            if chromedriver_file:
                # Extract the ChromeDriver binary
                zip_ref.extract(chromedriver_file, install_dir)
                
                # Move to final location if it's in a subdirectory
                extracted_path = os.path.join(install_dir, chromedriver_file)
                final_path = os.path.join(install_dir, 'chromedriver')
                
                if extracted_path != final_path:
                    os.rename(extracted_path, final_path)
                    # Clean up any empty directories
                    dir_path = os.path.dirname(extracted_path)
                    if dir_path != install_dir and os.path.exists(dir_path):
                        try:
                            os.rmdir(dir_path)
                        except OSError:
                            pass
                
                # Make executable
                os.chmod(final_path, 0o755)
                logger.info(f"ChromeDriver installed successfully at: {final_path}")
            else:
                raise Exception("ChromeDriver binary not found in archive")
        
        # Clean up temporary file
        os.unlink(temp_zip_path)
        return True
        
    except Exception as e:
        logger.error(f"Error downloading/installing ChromeDriver: {e}")
        return False

def main():
    """Main setup function"""
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    drivers_dir = os.path.join(current_dir, 'drivers')
    
    # Get Chrome version
    chrome_version = get_chrome_version()
    if not chrome_version:
        logger.error("Cannot determine Chrome version. Please install Google Chrome or Chromium.")
        return False
    
    # Get ChromeDriver download URL
    chromedriver_url = get_chromedriver_url(chrome_version)
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
            logger.info("Setup completed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"ChromeDriver verification failed: {e}")
            return False
    else:
        logger.error("Setup failed")
        return False

if __name__ == '__main__':
    main()
