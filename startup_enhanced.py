#!/usr/bin/env python3
"""
Enhanced Pinterest Auto-Publisher Startup Script
Includes deployment validation and robust Chrome setup
"""

import os
import sys
import subprocess
import logging
import time
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_validation():
    """Run deployment validation"""
    logger.info("Running deployment validation...")
    try:
        result = subprocess.run([sys.executable, 'validate_deployment.py'], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            logger.info("✅ Deployment validation passed")
            return True
        else:
            logger.error(f"❌ Deployment validation failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Validation failed with exception: {e}")
        return False

def setup_chrome():
    """Set up Chrome if needed"""
    current_dir = Path(__file__).parent
    chrome_binary = current_dir / 'chrome' / 'chrome-linux64' / 'chrome'
    
    if not chrome_binary.exists():
        logger.info("Chrome not found, setting up...")
        try:
            result = subprocess.run([sys.executable, 'setup_portable_chrome.py'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info("✅ Chrome setup completed")
            else:
                logger.error(f"Chrome setup failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Chrome setup failed: {e}")
            return False
    else:
        logger.info("Chrome binary found")
    
    return True

def setup_chromedriver():
    """Set up ChromeDriver if needed"""
    current_dir = Path(__file__).parent
    chromedriver_path = current_dir / 'drivers' / 'chromedriver'
    
    if not chromedriver_path.exists():
        logger.info("ChromeDriver not found, setting up...")
        try:
            result = subprocess.run([sys.executable, 'setup_chromedriver.py'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info("✅ ChromeDriver setup completed")
            else:
                logger.error(f"ChromeDriver setup failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"ChromeDriver setup failed: {e}")
            return False
    else:
        logger.info("ChromeDriver binary found")
    
    return True

def launch_app():
    """Launch the main application"""
    logger.info("Launching Pinterest Auto-Publisher...")
    try:
        # Import here to ensure all dependencies are ready
        import app
        logger.info("✅ Application launched successfully")
    except Exception as e:
        logger.error(f"Failed to launch application: {e}")
        return False
    
    return True

def main():
    """Main startup sequence"""
    logger.info("🎯 Starting Pinterest Auto-Publisher (Enhanced Version)...")
    
    # Detect production environment
    is_production = any(key in os.environ for key in ['RENDER', 'HEROKU', 'DYNO', 'RAILWAY_ENVIRONMENT', 'SPACE_ID'])
    if is_production:
        logger.info("Production environment detected")
    else:
        logger.info("Development environment detected")
    
    # Setup sequence
    steps = [
        ("Chrome setup", setup_chrome),
        ("ChromeDriver setup", setup_chromedriver),
        ("Deployment validation", run_validation),
        ("Application launch", launch_app),
    ]
    
    for step_name, step_func in steps:
        logger.info(f"\n--- {step_name} ---")
        try:
            if not step_func():
                logger.error(f"❌ {step_name} failed - stopping startup")
                return 1
        except Exception as e:
            logger.error(f"❌ {step_name} failed with exception: {e}")
            return 1
    
    logger.info("🎉 Pinterest Auto-Publisher startup completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
