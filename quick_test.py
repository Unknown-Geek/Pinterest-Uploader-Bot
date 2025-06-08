#!/usr/bin/env python3
import logging
logging.basicConfig(level=logging.INFO)

from pinterest_automation import PinterestAutomation

def test():
    try:
        bot = PinterestAutomation(headless=True)
        if bot._setup_driver():
            print("✅ SUCCESS: Chrome setup works")
            bot.cleanup()
            return True
        else:
            print("❌ FAILED: Chrome setup failed")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    test()
