#!/usr/bin/env python3
"""
Setup script to download and configure portable Chrome and ChromeDriver
This creates a self-contained setup that doesn't require system installations
"""

import os
import sys
import subprocess
import urllib.request
import shutil
import zipfile
import tarfile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_file(url, filename):
    """Download a file with progress indication"""
    logger.info(f"Downloading {filename}...")
    try:
        urllib.request.urlretrieve(url, filename)
        logger.info(f"✅ Downloaded {filename}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to download {filename}: {e}")
        return False

def extract_tar_xz(tar_path, extract_to):
    """Extract .tar.xz file"""
    try:
        with tarfile.open(tar_path, 'r:xz') as tar:
            tar.extractall(extract_to)
        return True
    except Exception as e:
        logger.error(f"Failed to extract {tar_path}: {e}")
        return False

def setup_portable_chrome():
    """Download and setup portable Chrome"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    chrome_dir = os.path.join(current_dir, 'chrome')
    
    # Create chrome directory
    os.makedirs(chrome_dir, exist_ok=True)
    
    # Chrome download URL (latest stable for Linux x64)
    chrome_url = "https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.87/linux64/chrome-linux64.zip"
    chrome_zip = os.path.join(chrome_dir, 'chrome-linux64.zip')
    
    # Download Chrome
    if not download_file(chrome_url, chrome_zip):
        return False
    
    # Extract Chrome
    logger.info("Extracting Chrome...")
    try:
        with zipfile.ZipFile(chrome_zip, 'r') as zip_ref:
            zip_ref.extractall(chrome_dir)
        
        # Remove the zip file
        os.remove(chrome_zip)
        
        # Make chrome executable
        chrome_binary = os.path.join(chrome_dir, 'chrome-linux64', 'chrome')
        os.chmod(chrome_binary, 0o755)
        
        logger.info(f"✅ Chrome installed at: {chrome_binary}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to extract Chrome: {e}")
        return False

def setup_chromedriver():
    """Download and setup ChromeDriver"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    drivers_dir = os.path.join(current_dir, 'drivers')
    
    # Create drivers directory
    os.makedirs(drivers_dir, exist_ok=True)
    
    # ChromeDriver download URL (matching Chrome version)
    chromedriver_url = "https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.87/linux64/chromedriver-linux64.zip"
    chromedriver_zip = os.path.join(drivers_dir, 'chromedriver-linux64.zip')
    
    # Check if chromedriver already exists
    chromedriver_path = os.path.join(drivers_dir, 'chromedriver')
    if os.path.exists(chromedriver_path):
        logger.info("ChromeDriver already exists, skipping download")
        return True
    
    # Download ChromeDriver
    if not download_file(chromedriver_url, chromedriver_zip):
        return False
    
    # Extract ChromeDriver
    logger.info("Extracting ChromeDriver...")
    try:
        with zipfile.ZipFile(chromedriver_zip, 'r') as zip_ref:
            zip_ref.extractall(drivers_dir)
        
        # Move chromedriver to the correct location
        extracted_chromedriver = os.path.join(drivers_dir, 'chromedriver-linux64', 'chromedriver')
        if os.path.exists(extracted_chromedriver):
            shutil.move(extracted_chromedriver, chromedriver_path)
            # Clean up extracted directory
            shutil.rmtree(os.path.join(drivers_dir, 'chromedriver-linux64'))
        
        # Remove the zip file
        os.remove(chromedriver_zip)
        
        # Make chromedriver executable
        os.chmod(chromedriver_path, 0o755)
        
        logger.info(f"✅ ChromeDriver installed at: {chromedriver_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to extract ChromeDriver: {e}")
        return False

def create_chrome_wrapper():
    """Create a wrapper script for Chrome"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    chrome_binary = os.path.join(current_dir, 'chrome', 'chrome-linux64', 'chrome')
    wrapper_path = os.path.join(current_dir, 'chrome', 'google-chrome')
    
    wrapper_content = f'''#!/bin/bash
# Chrome wrapper script
export CHROME_DEVEL_SANDBOX=/usr/lib/chromium-browser/chrome-sandbox
"{chrome_binary}" "$@"
'''
    
    try:
        with open(wrapper_path, 'w') as f:
            f.write(wrapper_content)
        os.chmod(wrapper_path, 0o755)
        logger.info(f"✅ Chrome wrapper created at: {wrapper_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create Chrome wrapper: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("🚀 Setting up portable Chrome and ChromeDriver...")
    
    # Setup Chrome
    if not setup_portable_chrome():
        logger.error("❌ Failed to setup Chrome")
        return False
    
    # Setup ChromeDriver
    if not setup_chromedriver():
        logger.error("❌ Failed to setup ChromeDriver")
        return False
    
    # Create Chrome wrapper
    if not create_chrome_wrapper():
        logger.error("❌ Failed to create Chrome wrapper")
        return False
    
    logger.info("✅ Portable Chrome setup completed successfully!")
    logger.info("📁 Chrome installed in: ./chrome/chrome-linux64/chrome")
    logger.info("📁 ChromeDriver installed in: ./drivers/chromedriver")
    
    return True

if __name__ == '__main__':
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
