#!/usr/bin/env python3
"""
Deployment validation script for Pinterest Auto-Publisher
Tests Chrome initialization and basic functionality before full deployment
"""

import os
import sys
import subprocess
import logging
import tempfile
import uuid
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_chrome_binary():
    """Validate Chrome binary exists and is executable"""
    current_dir = Path(__file__).parent
    chrome_binary = current_dir / 'chrome' / 'chrome-linux64' / 'chrome'
    
    if not chrome_binary.exists():
        logger.error(f"Chrome binary not found: {chrome_binary}")
        return False
    
    if not os.access(chrome_binary, os.X_OK):
        logger.error(f"Chrome binary not executable: {chrome_binary}")
        return False
    
    # Test Chrome version
    try:
        result = subprocess.run([str(chrome_binary), '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info(f"Chrome version: {result.stdout.strip()}")
            return True
        else:
            logger.error(f"Chrome version check failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Chrome version test failed: {e}")
        return False

def validate_chromedriver():
    """Validate ChromeDriver exists and is executable"""
    current_dir = Path(__file__).parent
    chromedriver_path = current_dir / 'drivers' / 'chromedriver'
    
    if not chromedriver_path.exists():
        logger.error(f"ChromeDriver not found: {chromedriver_path}")
        return False
    
    if not os.access(chromedriver_path, os.X_OK):
        logger.error(f"ChromeDriver not executable: {chromedriver_path}")
        return False
    
    # Test ChromeDriver version
    try:
        result = subprocess.run([str(chromedriver_path), '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info(f"ChromeDriver version: {result.stdout.strip()}")
            return True
        else:
            logger.error(f"ChromeDriver version check failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"ChromeDriver version test failed: {e}")
        return False

def validate_chrome_initialization():
    """Test Chrome WebDriver initialization"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        
        current_dir = Path(__file__).parent
        chrome_binary = current_dir / 'chrome' / 'chrome-linux64' / 'chrome'
        chromedriver_path = current_dir / 'drivers' / 'chromedriver'
        
        # Detect production environment
        is_production = any(key in os.environ for key in ['RENDER', 'HEROKU', 'DYNO', 'RAILWAY_ENVIRONMENT', 'SPACE_ID'])
        logger.info(f"Production environment detected: {is_production}")
        
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.binary_location = str(chrome_binary)
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        if is_production:
            # Production-specific flags
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--disable-background-networking")
            chrome_options.add_argument("--remote-debugging-port=9222")
            chrome_options.add_argument("--remote-debugging-address=0.0.0.0")
            os.environ['DISPLAY'] = ':99'
        
        # Create unique profile directory
        profile_dir = f"/tmp/validation_chrome_profile_{uuid.uuid4().hex}"
        chrome_options.add_argument(f"--user-data-dir={profile_dir}")
        
        # Create service
        service = Service(str(chromedriver_path))
        
        # Try to create driver
        logger.info("Testing Chrome WebDriver initialization...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Test basic functionality
        driver.get("https://httpbin.org/get")
        logger.info(f"Page title: {driver.title}")
        
        # Clean up
        driver.quit()
        
        # Clean up profile directory
        import shutil
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir, ignore_errors=True)
        
        logger.info("✅ Chrome WebDriver initialization successful")
        return True
        
    except Exception as e:
        logger.error(f"Chrome WebDriver initialization failed: {e}")
        return False

def validate_environment():
    """Validate environment variables and dependencies"""
    logger.info("Validating environment...")
    
    # Check Python version
    logger.info(f"Python version: {sys.version}")
    
    # Check environment variables
    env_vars = ['RENDER', 'HEROKU', 'DYNO', 'RAILWAY_ENVIRONMENT', 'SPACE_ID']
    for var in env_vars:
        if var in os.environ:
            logger.info(f"Environment variable {var} detected")
    
    # Check required packages
    required_packages = ['selenium', 'gradio']
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"Package {package} is available")
        except ImportError:
            logger.error(f"Required package {package} not available")
            return False
    
    return True

def main():
    """Run all validation tests"""
    logger.info("Starting Pinterest Auto-Publisher deployment validation...")
    
    tests = [
        ("Environment validation", validate_environment),
        ("Chrome binary validation", validate_chrome_binary),
        ("ChromeDriver validation", validate_chromedriver),
        ("Chrome WebDriver initialization", validate_chrome_initialization),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} ---")
        try:
            if test_func():
                logger.info(f"✅ {test_name} PASSED")
                passed += 1
            else:
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} FAILED with exception: {e}")
    
    logger.info(f"\n--- Validation Summary ---")
    logger.info(f"Passed: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All validation tests passed! Deployment should work.")
        return 0
    else:
        logger.error("⚠️  Some validation tests failed. Check logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
