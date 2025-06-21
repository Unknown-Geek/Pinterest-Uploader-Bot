"""
Chrome Wrapper for Pinterest Automation
Provides easy access to portable Chrome setup for the automation script
"""

import json
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

class PortableChromeManager:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.config_path = self.root_dir / "chrome_config.json"
        self.config = self._load_config()
    
    def _load_config(self):
        """Load Chrome configuration"""
        if not self.config_path.exists():
            raise FileNotFoundError(
                "Chrome configuration not found. Chrome setup is missing."
            )
        
        with open(self.config_path) as f:
            config = json.load(f)
        
        # Convert relative paths to absolute paths
        chrome_binary = self.root_dir / config["chrome_binary"]
        chromedriver_path = self.root_dir / config["chromedriver_path"]
        
        if not chrome_binary.exists():
            raise FileNotFoundError(f"Chrome binary not found: {chrome_binary}")
        
        if not chromedriver_path.exists():
            raise FileNotFoundError(f"ChromeDriver not found: {chromedriver_path}")
        
        # Update config with absolute paths
        config["chrome_binary"] = str(chrome_binary)
        config["chromedriver_path"] = str(chromedriver_path)
        
        return config
    
    def get_chrome_options(self, headless=False, additional_options=None):
        """Get Chrome options configured for portable Chrome"""
        options = Options()
        
        # Set the binary location
        options.binary_location = self.config["chrome_binary"]
        
        # Essential options for reliability
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        
        # Additional options for containerized environments
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-features=TranslateUI')
        options.add_argument('--disable-ipc-flooding-protection')
        options.add_argument('--no-first-run')
        options.add_argument('--no-default-browser-check')
        options.add_argument('--disable-default-apps')
        options.add_argument('--remote-debugging-port=9222')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        
        # Headless mode
        if headless:
            options.add_argument('--headless')
        
        # Anti-detection measures
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Performance optimizations
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')  # Faster loading
        
        # Additional options for cloud deployment
        options.add_argument('--disable-logging')
        options.add_argument('--disable-dev-tools')
        
        # Add any additional options
        if additional_options:
            for option in additional_options:
                options.add_argument(option)
        
        return options
    
    def get_chrome_service(self):
        """Get Chrome service configured for portable ChromeDriver"""
        return Service(executable_path=self.config["chromedriver_path"])
    
    def create_driver(self, headless=False, additional_options=None):
        """Create and return a configured Chrome WebDriver"""
        options = self.get_chrome_options(headless=headless, additional_options=additional_options)
        service = self.get_chrome_service()
        
        driver = webdriver.Chrome(service=service, options=options)
        
        # Remove automation indicators
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def get_config_info(self):
        """Get information about the current Chrome setup"""
        return {
            "chrome_binary": self.config["chrome_binary"],
            "chromedriver_path": self.config["chromedriver_path"],
            "version": self.config["version"],
            "platform": self.config["platform"]
        }

# Global instance for easy import - use lazy initialization
chrome_manager = None

def get_chrome_manager():
    """Get or create the global chrome manager instance"""
    global chrome_manager
    if chrome_manager is None:
        chrome_manager = PortableChromeManager()
    return chrome_manager
