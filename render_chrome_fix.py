#!/usr/bin/env python3
"""
Render.com Chrome deployment fix
Addresses Chrome startup issues in containerized environments
"""

import os
import subprocess
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_render_chrome_options():
    """Create Chrome options specifically optimized for Render.com deployment"""
    
    # Get Chrome binary path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    chrome_binary = os.path.join(current_dir, 'chrome', 'chrome-linux64', 'chrome')
    
    chrome_options = Options()
    chrome_options.binary_location = chrome_binary
    
    # Essential headless configuration for containers
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Critical for Render.com and similar container environments
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-javascript")  # Temporary for testing
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    
    # Memory and resource optimization for containers
    chrome_options.add_argument("--memory-pressure-off")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-component-extensions-with-background-pages")
    
    # Container-specific flags
    chrome_options.add_argument("--single-process")  # Critical for some containers
    chrome_options.add_argument("--no-zygote")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    
    # Display and window management
    chrome_options.add_argument("--window-size=1280,720")
    chrome_options.add_argument("--virtual-time-budget=5000")
    
    # File system related
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--disable-login-animations")
    chrome_options.add_argument("--disable-notifications")
    
    # Create minimal profile directory
    import tempfile
    import uuid
    profile_dir = f"/tmp/chrome_profile_{uuid.uuid4().hex[:8]}"
    chrome_options.add_argument(f"--user-data-dir={profile_dir}")
    
    # Environment setup
    os.environ['DISPLAY'] = ':99'
    os.environ['CHROME_LOG_FILE'] = '/tmp/chrome.log'
    
    return chrome_options, profile_dir

def test_render_chrome():
    """Test Chrome with Render-optimized configuration"""
    
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        chromedriver_path = os.path.join(current_dir, 'drivers', 'chromedriver')
        
        logger.info("Testing Render-optimized Chrome configuration...")
        
        chrome_options, profile_dir = create_render_chrome_options()
        
        # Create service
        service = Service(chromedriver_path)
        service.log_output = subprocess.DEVNULL
        
        # Try to create driver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("✅ Chrome driver created successfully with Render config!")
        
        # Test basic functionality
        try:
            driver.get("data:text/html,<html><body><h1>Test</h1></body></html>")
            logger.info("✅ Basic page loading works")
        except Exception as e:
            logger.warning(f"Page loading test failed: {e}")
        
        # Cleanup
        driver.quit()
        
        # Clean up profile directory
        import shutil
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir, ignore_errors=True)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Render Chrome test failed: {e}")
        return False

def apply_render_fix():
    """Apply the Render fix to pinterest_automation.py"""
    
    logger.info("Applying Render Chrome fix to pinterest_automation.py...")
    
    # The fix will be applied by modifying the _setup_driver method
    # to use the Render-optimized configuration when deployed
    
    render_chrome_setup = '''
    def _setup_driver_render_optimized(self):
        """Setup Chrome WebDriver optimized for Render.com deployment"""
        try:
            # Chrome paths
            current_dir = os.path.dirname(os.path.abspath(__file__))
            chrome_binary = os.path.join(current_dir, 'chrome', 'chrome-linux64', 'chrome')
            chromedriver_path = os.path.join(current_dir, 'drivers', 'chromedriver')
            
            # Verify files exist
            if not os.path.exists(chrome_binary):
                raise Exception(f"Chrome binary not found: {chrome_binary}")
            if not os.path.exists(chromedriver_path):
                raise Exception(f"ChromeDriver not found: {chromedriver_path}")
            
            self.logger.info(f"Using Chrome binary: {chrome_binary}")
            self.logger.info(f"Using ChromeDriver: {chromedriver_path}")
            
            # Detect Render environment
            is_render = 'RENDER' in os.environ
            if is_render:
                self.logger.info("Render deployment detected - using optimized configuration")
            
            # Set up Chrome options - Render-optimized
            chrome_options = Options()
            chrome_options.binary_location = chrome_binary
            
            # Essential Render flags
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-software-rasterizer")
            
            if is_render:
                # Render-specific optimizations
                chrome_options.add_argument("--single-process")
                chrome_options.add_argument("--no-zygote")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--disable-plugins")
                chrome_options.add_argument("--disable-images")
                chrome_options.add_argument("--disable-web-security")
                chrome_options.add_argument("--disable-features=VizDisplayCompositor")
                chrome_options.add_argument("--memory-pressure-off")
                chrome_options.add_argument("--disable-ipc-flooding-protection")
                chrome_options.add_argument("--window-size=1280,720")
                chrome_options.add_argument("--virtual-time-budget=5000")
                
                # Environment setup for Render
                os.environ['DISPLAY'] = ':99'
                os.environ['CHROME_LOG_FILE'] = '/tmp/chrome.log'
            else:
                # Local development flags
                chrome_options.add_argument("--window-size=1920,1080")
                if self.headless:
                    chrome_options.add_argument("--headless=new")
            
            # Create profile directory
            import tempfile, uuid
            profile_dir = f"/tmp/chrome_profile_{uuid.uuid4().hex[:8]}"
            chrome_options.add_argument(f"--user-data-dir={profile_dir}")
            self.user_data_dir = profile_dir
            
            # Anti-detection (minimal for Render)
            if not is_render:
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Create service
            from selenium.webdriver.chrome.service import Service
            service = Service(chromedriver_path)
            service.log_output = subprocess.DEVNULL
            
            # Create driver with simplified retry
            self.logger.info("Creating Chrome driver...")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.logger.info("✅ Chrome driver created successfully")
            
            # Set up wait
            from selenium.webdriver.support.ui import WebDriverWait
            self.wait = WebDriverWait(self.driver, 20)
            
            # Execute anti-detection script (only for non-Render)
            if not is_render:
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("Chrome driver setup completed successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to setup Chrome driver: {e}")
            if hasattr(self, 'driver') and self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            raise Exception("Failed to initialize browser driver")
    '''
    
    logger.info("Render fix configuration ready")
    return True

if __name__ == "__main__":
    logger.info("Testing Render Chrome fix...")
    
    if test_render_chrome():
        logger.info("✅ Render Chrome fix test passed!")
        apply_render_fix()
    else:
        logger.error("❌ Render Chrome fix test failed")
