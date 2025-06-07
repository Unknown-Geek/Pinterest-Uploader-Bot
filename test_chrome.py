#!/usr/bin/env python3

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Set display environment
os.environ['DISPLAY'] = ':99'

print("Testing Chrome in non-headless mode...")

chrome_options = Options()
# Do NOT add --headless to test non-headless mode
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1920,1080')

try:
    print("Starting Chrome browser...")
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
