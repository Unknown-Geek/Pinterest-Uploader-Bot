#!/usr/bin/env python3

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Set display environment
os.environ['DISPLAY'] = ':99'

print("Testing Chrome in headless mode...")

chrome_options = Options()
chrome_options.add_argument('--headless')  # Enable headless mode for this environment
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--user-data-dir=/tmp/chrome_user_data')  # Add unique user data directory
chrome_options.add_argument('--remote-debugging-port=9222')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-plugins')
chrome_options.add_argument('--disable-images')
chrome_options.add_argument('--disable-background-timer-throttling')
chrome_options.add_argument('--disable-backgrounding-occluded-windows')
chrome_options.add_argument('--disable-renderer-backgrounding')
chrome_options.add_argument('--disable-features=TranslateUI')
chrome_options.add_argument('--disable-ipc-flooding-protection')

# Set the Chrome binary location to use Google Chrome instead of Chromium
chrome_options.binary_location = '/usr/bin/google-chrome'

try:
    print("Starting Chrome browser...")
    
    # Use local ChromeDriver
    current_dir = os.path.dirname(os.path.abspath(__file__))
    chromedriver_path = os.path.join(current_dir, 'drivers', 'chromedriver')
    
    if os.path.exists(chromedriver_path):
        print(f"Using local ChromeDriver: {chromedriver_path}")
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        print("Using system ChromeDriver")
        driver = webdriver.Chrome(options=chrome_options)
    
    print("Chrome started successfully!")
    
    print("Navigating to Google...")
    driver.get("https://www.google.com")
    
    print("Taking screenshot...")
    driver.save_screenshot("/workspaces/Pinterest-Uploader-Bot/test_screenshot.png")
    print("Screenshot saved!")
    
    print("Keeping browser open for 10 seconds...")
    time.sleep(10)
    
    print("Closing browser...")
    driver.quit()
    print("Test completed successfully!")
    
except Exception as e:
    print(f"Error: {e}")
