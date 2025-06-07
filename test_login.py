#!/usr/bin/env python3

import os
import logging
from pinterest_automation import PinterestAutomation

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_login():
    """Test the Pinterest login functionality"""
    
    # Set up virtual display for headless environment
    os.environ['DISPLAY'] = ':99'
    
    # Initialize automation with visible browser
    automation = PinterestAutomation(headless=False, fast_typing=True)
    
    try:
        logger.info("Setting up browser driver...")
        if not automation._setup_driver():
            logger.error("Failed to setup driver")
            return False
        
        logger.info("Testing Pinterest login...")
        
        # Test credentials (you can replace these with real ones to test)
        email = "test@example.com"  # Replace with real email for testing
        password = "testpassword"   # Replace with real password for testing
        
        # Try login
        login_success = automation.login(email, password)
        
        if login_success:
            logger.info("✅ Login test PASSED!")
            return True
        else:
            logger.error("❌ Login test FAILED")
            return False
            
    except Exception as e:
        logger.error(f"Test error: {str(e)}")
        return False
    finally:
        # Keep browser open for 5 seconds to see result
        automation._human_delay(5, 5)
        automation.quit()

if __name__ == "__main__":
    test_login()
