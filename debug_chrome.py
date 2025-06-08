#!/usr/bin/env python3
import os
import sys
import subprocess

print("=== Testing Chrome Binary Directly ===")
chrome_binary = "/workspaces/Pinterest-Uploader-Bot/chrome/chrome-linux64/chrome"
print(f"Chrome binary exists: {os.path.exists(chrome_binary)}")

try:
    result = subprocess.run([chrome_binary, '--version'], capture_output=True, text=True, timeout=5)
    print(f"Chrome version: {result.stdout.strip()}")
    print(f"Chrome stderr: {result.stderr.strip()}")
except Exception as e:
    print(f"Chrome test failed: {e}")

print("\n=== Testing Chrome with minimal flags ===")
try:
    result = subprocess.run([
        chrome_binary, 
        '--headless=new',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--version'
    ], capture_output=True, text=True, timeout=10)
    print(f"Chrome with flags: {result.stdout.strip()}")
    print(f"Chrome with flags stderr: {result.stderr.strip()}")
except Exception as e:
    print(f"Chrome with flags test failed: {e}")

print("\n=== Testing WebDriver Import ===")
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    print("✅ Selenium imports successful")
except Exception as e:
    print(f"❌ Selenium import failed: {e}")
    sys.exit(1)

print("\n=== Testing ChromeDriver Binary ===")
chromedriver_path = "/workspaces/Pinterest-Uploader-Bot/drivers/chromedriver"
print(f"ChromeDriver exists: {os.path.exists(chromedriver_path)}")

try:
    result = subprocess.run([chromedriver_path, '--version'], capture_output=True, text=True, timeout=5)
    print(f"ChromeDriver version: {result.stdout.strip()}")
except Exception as e:
    print(f"ChromeDriver test failed: {e}")

print("\n=== Done ===")
