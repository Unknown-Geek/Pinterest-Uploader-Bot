#!/usr/bin/env python3
"""
Simple Chrome test with timeout handling
"""

import os
import signal
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Chrome initialization timed out")

def test_chrome_simple():
    """Simple Chrome test with timeout"""
    try:
        # Set up timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)  # 30 second timeout
        
        logger.info("Starting simple Chrome test...")
        
        # Chrome paths
        chrome_binary = "/workspaces/Pinterest-Uploader-Bot/chrome/chrome-linux64/chrome"
        chromedriver_path = "/workspaces/Pinterest-Uploader-Bot/drivers/chromedriver"
        
        # Verify files exist
        if not os.path.exists(chrome_binary):
            logger.error(f"Chrome binary not found: {chrome_binary}")
            return False
            
        if not os.path.exists(chromedriver_path):
            logger.error(f"ChromeDriver not found: {chromedriver_path}")
            return False
        
        logger.info(f"Chrome binary: {chrome_binary}")
        logger.info(f"ChromeDriver: {chromedriver_path}")
        
        # Set up Chrome options - minimal set
        chrome_options = Options()
        chrome_options.binary_location = chrome_binary
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--user-data-dir=/tmp/simple_chrome_test")
        chrome_options.add_argument("--remote-debugging-port=0")  # Let Chrome choose port
        
        # Create service
        service = Service(executable_path=chromedriver_path)
        
        logger.info("Creating WebDriver...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        logger.info("✅ Chrome WebDriver created successfully!")
        
        # Test basic functionality
        logger.info("Testing navigation...")
        driver.get("data:text/html,<html><body><h1>Test Page</h1></body></html>")
        
        title = driver.title
        logger.info(f"Page title: {title}")
        
        # Get version info
        capabilities = driver.capabilities
        browser_version = capabilities.get('browserVersion', 'Unknown')
        chromedriver_version = capabilities.get('chrome', {}).get('chromedriverVersion', 'Unknown')
        
        logger.info(f"Browser version: {browser_version}")
        logger.info(f"ChromeDriver version: {chromedriver_version}")
        
        driver.quit()
        signal.alarm(0)  # Cancel timeout
        
        logger.info("✅ Simple Chrome test PASSED!")
        return True
        
    except TimeoutError:
        logger.error("❌ Chrome initialization timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Chrome test failed: {e}")
        signal.alarm(0)  # Cancel timeout
        return False
    finally:
        # Cleanup any remaining processes
        os.system("pkill -f chrome > /dev/null 2>&1")
        os.system("pkill -f chromedriver > /dev/null 2>&1")

if __name__ == "__main__":
    success = test_chrome_simple()
    exit(0 if success else 1)
