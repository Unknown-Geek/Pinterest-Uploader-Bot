#!/usr/bin/env python3
"""
Quick test to verify Chrome initialization works
"""

import logging
from pinterest_automation import PinterestAutomation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_chrome_init():
    """Test Chrome initialization"""
    try:
        logger.info("Testing Chrome initialization...")
        bot = PinterestAutomation(headless=True)
        
        # Test driver setup
        if bot._setup_driver():
            logger.info("✅ Chrome initialization SUCCESSFUL!")
            logger.info(f"Chrome version: {bot.driver.capabilities.get('browserVersion', 'Unknown')}")
            logger.info(f"ChromeDriver version: {bot.driver.capabilities.get('chrome', {}).get('chromedriverVersion', 'Unknown')}")
            
            # Test basic navigation
            try:
                bot.driver.get("https://www.google.com")
                title = bot.driver.title
                logger.info(f"✅ Basic navigation test successful. Page title: {title}")
            except Exception as e:
                logger.warning(f"⚠️ Navigation test failed: {e}")
            
            bot.cleanup()
            return True
        else:
            logger.error("❌ Chrome initialization FAILED!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = test_chrome_init()
    exit(0 if success else 1)
