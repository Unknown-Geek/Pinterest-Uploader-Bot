#!/usr/bin/env python3
"""
Quick test script for Pinterest Auto-Publisher
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import flask
        print("✅ Flask imported successfully")
        
        import selenium
        print("✅ Selenium imported successfully")
        
        from selenium import webdriver
        print("✅ WebDriver imported successfully")
        
        from pinterest_automation import PinterestAutomation
        print("✅ PinterestAutomation imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_chromedriver():
    """Test if ChromeDriver is available"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Try to create driver instance
        driver = webdriver.Chrome(options=options)
        driver.quit()
        
        print("✅ ChromeDriver is working properly")
        return True
    except Exception as e:
        print(f"❌ ChromeDriver error: {e}")
        print("Try running: python setup_chromedriver.py")
        return False

def test_pinterest_automation():
    """Test Pinterest automation class"""
    try:
        from pinterest_automation import PinterestAutomation
        
        # Test initialization
        bot = PinterestAutomation(headless=True)
        print("✅ PinterestAutomation initialization successful")
        
        return True
    except Exception as e:
        print(f"❌ PinterestAutomation error: {e}")
        return False

def main():
    """Run all tests"""
    print("Pinterest Auto-Publisher - System Test")
    print("=" * 40)
    
    all_passed = True
    
    print("\n1. Testing imports...")
    if not test_imports():
        all_passed = False
    
    print("\n2. Testing ChromeDriver...")
    if not test_chromedriver():
        all_passed = False
    
    print("\n3. Testing Pinterest automation...")
    if not test_pinterest_automation():
        all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All tests passed! Your system is ready.")
        print("\nTo start the application:")
        print("python app.py")
        print("\nThen open: http://localhost:5000")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
