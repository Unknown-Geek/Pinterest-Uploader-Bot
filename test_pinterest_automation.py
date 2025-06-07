#!/usr/bin/env python3

import sys
import os
sys.path.append('/workspaces/Pinterest-Uploader-Bot')

from pinterest_automation import PinterestAutomation
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pinterest_automation():
    """Test the Pinterest automation setup"""
    try:
        logger.info("Testing Pinterest automation setup...")
        
        # Create automation instance
        bot = PinterestAutomation(headless=True)
        
        # Test driver setup
        success = bot._setup_driver()
        
        if success:
            logger.info("✅ Driver setup successful!")
            logger.info(f"Driver session: {bot.driver.session_id}")
            
            # Test navigation
            bot.driver.get("https://www.google.com")
            logger.info(f"✅ Navigation test successful! Current URL: {bot.driver.current_url}")
            
            # Clean up
            bot.driver.quit()
            logger.info("✅ Test completed successfully!")
            return True
        else:
            logger.error("❌ Driver setup failed!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        return False

if __name__ == '__main__':
    success = test_pinterest_automation()
    sys.exit(0 if success else 1)
