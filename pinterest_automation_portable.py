"""
Pinterest Automation with Portable Chrome
A wrapper around the original pinterest_automation.py that uses portable Chrome setup
"""

import logging
from pinterest_automation import PinterestAutomation
from chrome_wrapper import get_chrome_manager

class PortablePinterestAutomation(PinterestAutomation):
    """
    Extended Pinterest automation that uses portable Chrome setup
    """
    
    def _setup_driver(self):
        """Setup Chrome WebDriver using portable Chrome"""
        try:
            self.logger.info("Setting up portable Chrome driver...")
            
            # Get chrome manager instance
            chrome_manager = get_chrome_manager()
            
            # Get config info for logging
            config_info = chrome_manager.get_config_info()
            self.logger.info(f"Using Chrome: {config_info['chrome_binary']}")
            self.logger.info(f"Using ChromeDriver: {config_info['chromedriver_path']}")
            
            # Create driver using portable Chrome
            self.driver = chrome_manager.create_driver(headless=self.headless)
            
            # Set up wait
            from selenium.webdriver.support.ui import WebDriverWait
            self.wait = WebDriverWait(self.driver, 20)
            
            self.logger.info("Portable Chrome driver setup successful!")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup portable Chrome driver: {str(e)}")
            self.logger.error("Chrome setup appears to be missing or corrupted.")
            return False
