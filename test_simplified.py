#!/usr/bin/env python3
import logging
import os
import sys
logging.basicConfig(level=logging.INFO)

def test_chrome():
    try:
        from pinterest_automation import PinterestAutomation
        print("✅ Import successful")
        
        bot = PinterestAutomation(headless=True)
        print("✅ Bot creation successful")
        
        success = bot._setup_driver()
        if success:
            print("✅ Chrome driver setup successful")
            bot.cleanup()
            return True
        else:
            print("❌ Chrome driver setup failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_chrome()
