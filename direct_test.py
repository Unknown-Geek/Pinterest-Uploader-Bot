#!/usr/bin/env python3
"""
Direct test of Pinterest automation class
"""

import sys
import os
import logging

# Add the current directory to sys.path
sys.path.insert(0, '/workspaces/Pinterest-Uploader-Bot')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pinterest_automation():
    try:
        logger.info("Importing PinterestAutomation...")
        from pinterest_automation import PinterestAutomation
        
        logger.info("Creating PinterestAutomation instance...")
        bot = PinterestAutomation(headless=True)
        
        logger.info("Testing driver setup...")
        result = bot._setup_driver()
        
        if result:
            logger.info("✅ Pinterest automation driver setup SUCCESSFUL!")
            # Test navigation
            try:
                bot.driver.get("data:text/html,<html><body><h1>Test</h1></body></html>")
                logger.info("✅ Navigation test successful")
            except Exception as e:
                logger.warning(f"Navigation test failed: {e}")
            
            bot.cleanup()
            return True
        else:
            logger.error("❌ Pinterest automation driver setup FAILED!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pinterest_automation()
    exit(0 if success else 1)
