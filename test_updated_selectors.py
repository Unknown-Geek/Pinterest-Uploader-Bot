#!/usr/bin/env python3
"""
Test script to verify the updated Pinterest selectors work correctly
"""

import sys
import os
import time
from pinterest_automation import PinterestAutomation

def test_field_detection():
    """Test if we can find the description and link fields"""
    print("Testing updated Pinterest selectors...")
    
    bot = PinterestAutomation()
    
    try:
        print("1. Starting browser...")
        driver = bot.driver
        
        print("2. Going to Pinterest create page...")
        driver.get("https://www.pinterest.com/pin-builder/")
        time.sleep(5)
        
        print("3. Testing description field detection...")
        # Try to find description field with new selector
        try:
            desc_field = driver.find_element_by_css_selector("textarea[placeholder='Tell everyone what your Pin is about']")
            print("✓ Description field found with new selector!")
            print(f"  Field visible: {desc_field.is_displayed()}")
            print(f"  Field enabled: {desc_field.is_enabled()}")
        except Exception as e:
            print(f"✗ Description field not found: {e}")
            
            # Try alternative selectors
            print("  Trying alternative selectors...")
            selectors = [
                "textarea[placeholder*='Tell everyone']",
                "textarea[placeholder*='Pin is about']",
                ".public-DraftEditor-content",
                "div[contenteditable='true']"
            ]
            
            for selector in selectors:
                try:
                    field = driver.find_element_by_css_selector(selector)
                    if field.is_displayed():
                        print(f"  ✓ Found with: {selector}")
                        break
                except:
                    continue
        
        print("4. Testing link field detection...")
        # Try to find link field with new selector
        try:
            link_field = driver.find_element_by_css_selector("input[placeholder='Add a destination link']")
            print("✓ Link field found with new selector!")
            print(f"  Field visible: {link_field.is_displayed()}")
            print(f"  Field enabled: {link_field.is_enabled()}")
        except Exception as e:
            print(f"✗ Link field not found: {e}")
            
            # Try alternative selectors
            print("  Trying alternative selectors...")
            selectors = [
                "input[placeholder*='destination']",
                "input[placeholder*='link']",
                "input[aria-label*='link']",
                "input[aria-label*='website']"
            ]
            
            for selector in selectors:
                try:
                    field = driver.find_element_by_css_selector(selector)
                    if field.is_displayed():
                        print(f"  ✓ Found with: {selector}")
                        break
                except:
                    continue
        
        print("5. Testing all form fields...")
        # Get all input and textarea elements
        inputs = driver.find_elements_by_css_selector("input, textarea")
        print(f"Found {len(inputs)} input/textarea elements:")
        
        for i, inp in enumerate(inputs):
            if inp.is_displayed():
                placeholder = inp.get_attribute("placeholder") or ""
                aria_label = inp.get_attribute("aria-label") or ""
                tag = inp.tag_name
                input_type = inp.get_attribute("type") or ""
                
                if placeholder or aria_label:
                    print(f"  [{i}] {tag}[type='{input_type}'] placeholder='{placeholder}' aria-label='{aria_label}'")
        
        print("\nTest completed! Check the output above to verify selectors.")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            bot.close()
        except:
            pass

if __name__ == "__main__":
    test_field_detection()
