#!/usr/bin/env python3
"""
Test script for optimized Pinterest automation
This version removes failing methods and keeps only what works
"""

import logging
import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pinterest_automation_optimized import PinterestAutomationOptimized

def setup_logging():
    """Setup logging with detailed formatting"""
    log_filename = f"pinterest_optimized_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    return log_filename

def test_optimized_automation():
    """Test the optimized Pinterest automation"""
    
    log_file = setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=== STARTING OPTIMIZED PINTEREST AUTOMATION TEST ===")
    logger.info(f"Log file: {log_file}")
      # Test configuration
    test_config = {
        'email': 'mojomaniac2005@gmail.com',
        'password': 'Mojo@2005',
        'image_path': r'E:\Projects\Pinterest Bot\uploads\20250602_201756_37fbf9505acf5e19970630115c3cbad0.jpg',
        'title': 'Optimized Test',
        'description': 'Testing optimized automation with only working methods',
        'link_url': 'https://www.shravanpandala.design',
        'board_name': 'Wallpapers'
    }
    
    # Verify image exists
    if not os.path.exists(test_config['image_path']):
        logger.error(f"Image file not found: {test_config['image_path']}")
        return False
    
    # Initialize automation
    try:
        logger.info("Initializing optimized Pinterest automation...")
        automation = PinterestAutomationOptimized(headless=False)
        
        # Start browser
        logger.info("Starting browser...")
        if not automation.start_browser():
            logger.error("Failed to start browser")
            return False
        
        # Login
        logger.info("Attempting login...")
        if not automation.login(test_config['email'], test_config['password']):
            logger.error("Login failed")
            return False
        
        # Create pin with optimized methods
        logger.info("Creating pin with optimized methods...")
        success = automation.create_pin(
            image_path=test_config['image_path'],
            title=test_config['title'],
            description=test_config['description'],
            link_url=test_config['link_url'],
            board_name=test_config['board_name']
        )
        
        if success:
            logger.info("✅ OPTIMIZED PIN CREATION SUCCESSFUL!")
        else:
            logger.error("❌ OPTIMIZED PIN CREATION FAILED")
        
        # Keep browser open for manual verification
        input("Press Enter to close browser and finish test...")
        
        # Close browser
        automation.close_browser()
        
        return success
        
    except Exception as e:
        logger.error(f"Test error: {str(e)}")
        return False

def analyze_method_efficiency():
    """Analyze which methods are working vs failing"""
    
    logger = logging.getLogger(__name__)
    
    logger.info("=== METHOD EFFICIENCY ANALYSIS ===")
    
    # Based on the logs provided
    working_methods = {
        'Image Upload': 'Standard file input selector',
        'Title Setting': 'textarea[placeholder*="title" i]',
        'Description Setting': 'Draft.js editor method',
        'Board Selection': 'JavaScript method',
        'Pin Publishing': 'Button click methods'
    }
    
    failing_methods = {
        'Link Field (Dynamic ID)': 'input[id^="pin-draft-link-"]',
        'Link Field (Placeholder)': 'input[placeholder="Add a destination link"]',
        'Description (Pinterest-specific)': 'Pinterest-specific selector'
    }
    
    optimization_recommendations = {
        'Remove': failing_methods,
        'Keep and Prioritize': working_methods,
        'Enhance': {
            'Link Field Detection': 'Use enhanced JavaScript scanning for any input that might be a link field',
            'Error Handling': 'Continue process even if link field fails',
            'Timing': 'Optimize delays based on successful operations'
        }
    }
    
    logger.info("WORKING METHODS (Keep These):")
    for method, details in working_methods.items():
        logger.info(f"  ✅ {method}: {details}")
    
    logger.info("\nFAILING METHODS (Remove These):")
    for method, details in failing_methods.items():
        logger.info(f"  ❌ {method}: {details}")
    
    logger.info("\nOPTIMIZATION RECOMMENDATIONS:")
    for category, items in optimization_recommendations.items():
        logger.info(f"  {category.upper()}:")
        if isinstance(items, dict):
            for item, detail in items.items():
                logger.info(f"    - {item}: {detail}")

if __name__ == "__main__":
    print("Pinterest Automation Optimization Test")
    print("=====================================")
    
    # First analyze the methods
    analyze_method_efficiency()
    
    print("\nStarting optimized automation test...")
    
    # Run the optimized test
    result = test_optimized_automation()
    
    if result:
        print("\n✅ OPTIMIZATION TEST COMPLETED SUCCESSFULLY!")
        print("The optimized version removes failing methods and focuses on proven working approaches.")
    else:
        print("\n❌ OPTIMIZATION TEST FAILED")
        print("Check the logs for details on what went wrong.")
