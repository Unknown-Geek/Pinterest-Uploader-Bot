#!/usr/bin/env python3
"""
Pinterest Element Diagnostic Tool
This script will inspect the actual Pinterest page to see what elements are available
"""

import logging
import os
import sys
from datetime import datetime
import time

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pinterest_automation_optimized import PinterestAutomationOptimized

def setup_logging():
    """Setup logging with detailed formatting"""
    log_filename = f"pinterest_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    return log_filename

def diagnose_pinterest_page():
    """Diagnose what elements are actually available on Pinterest"""
    
    log_file = setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=== PINTEREST PAGE DIAGNOSTIC ===")
    logger.info(f"Log file: {log_file}")
    
    # Test configuration
    test_config = {
        'email': 'mojomaniac2005@gmail.com',
        'password': 'Mojo@2005',
        'image_path': r'E:\Projects\Pinterest Bot\uploads\20250602_201756_37fbf9505acf5e19970630115c3cbad0.jpg'
    }
    
    # Initialize automation
    try:
        logger.info("Initializing Pinterest automation for diagnosis...")
        automation = PinterestAutomationOptimized(headless=False)
        
        # Start browser
        if not automation.start_browser():
            logger.error("Failed to start browser")
            return False
        
        # Login
        if not automation.login(test_config['email'], test_config['password']):
            logger.error("Login failed")
            return False
        
        # Navigate to pin creation
        if not automation.navigate_to_pin_creation():
            logger.error("Failed to navigate to pin creation")
            return False
        
        # Upload image to get to the form
        if not automation.upload_image(test_config['image_path']):
            logger.error("Failed to upload image")
            return False
        
        # Wait for form to load
        time.sleep(5)
        
        logger.info("=== DIAGNOSING PAGE ELEMENTS ===")
        
        # Get all form elements
        form_elements = automation.driver.execute_script("""
            const results = {
                allInputs: [],
                allTextareas: [],
                allButtons: [],
                allSelects: [],
                linkLikeElements: [],
                publishLikeElements: []
            };
            
            // Get all inputs
            document.querySelectorAll('input').forEach((input, index) => {
                results.allInputs.push({
                    index: index,
                    id: input.id || '',
                    placeholder: input.placeholder || '',
                    type: input.type || '',
                    name: input.name || '',
                    ariaLabel: input.getAttribute('aria-label') || '',
                    visible: input.offsetParent !== null,
                    value: input.value || '',
                    className: input.className || ''
                });
                
                // Check if this might be a link field
                const context = (input.id + ' ' + input.placeholder + ' ' + 
                               (input.getAttribute('aria-label') || '') + ' ' + 
                               input.name + ' ' + input.className).toLowerCase();
                if (context.includes('link') || context.includes('url') || 
                    context.includes('website') || context.includes('destination')) {
                    results.linkLikeElements.push({
                        type: 'input',
                        index: index,
                        element: input.outerHTML.substring(0, 200),
                        context: context
                    });
                }
            });
            
            // Get all textareas
            document.querySelectorAll('textarea').forEach((textarea, index) => {
                results.allTextareas.push({
                    index: index,
                    id: textarea.id || '',
                    placeholder: textarea.placeholder || '',
                    name: textarea.name || '',
                    ariaLabel: textarea.getAttribute('aria-label') || '',
                    visible: textarea.offsetParent !== null,
                    value: textarea.value || '',
                    className: textarea.className || ''
                });
            });
            
            // Get all buttons
            document.querySelectorAll('button').forEach((button, index) => {
                const buttonInfo = {
                    index: index,
                    id: button.id || '',
                    textContent: button.textContent.trim(),
                    type: button.type || '',
                    ariaLabel: button.getAttribute('aria-label') || '',
                    visible: button.offsetParent !== null,
                    className: button.className || '',
                    dataTestId: button.getAttribute('data-test-id') || ''
                };
                results.allButtons.push(buttonInfo);
                
                // Check if this might be a publish button
                const context = (button.textContent + ' ' + (button.getAttribute('aria-label') || '') + ' ' + 
                               button.id + ' ' + (button.getAttribute('data-test-id') || '')).toLowerCase();
                if (context.includes('publish') || context.includes('save') || 
                    context.includes('post') || context.includes('create')) {
                    results.publishLikeElements.push({
                        type: 'button',
                        index: index,
                        element: button.outerHTML.substring(0, 200),
                        context: context
                    });
                }
            });
            
            // Get all selects
            document.querySelectorAll('select').forEach((select, index) => {
                results.allSelects.push({
                    index: index,
                    id: select.id || '',
                    name: select.name || '',
                    ariaLabel: select.getAttribute('aria-label') || '',
                    visible: select.offsetParent !== null,
                    className: select.className || ''
                });
            });
            
            return results;
        """)
        
        # Log findings
        logger.info(f"=== FORM ELEMENTS FOUND ===")
        logger.info(f"Total inputs: {len(form_elements['allInputs'])}")
        logger.info(f"Total textareas: {len(form_elements['allTextareas'])}")
        logger.info(f"Total buttons: {len(form_elements['allButtons'])}")
        logger.info(f"Total selects: {len(form_elements['allSelects'])}")
        logger.info(f"Link-like elements: {len(form_elements['linkLikeElements'])}")
        logger.info(f"Publish-like elements: {len(form_elements['publishLikeElements'])}")
        
        logger.info("\n=== VISIBLE INPUT ELEMENTS ===")
        for i, input_elem in enumerate(form_elements['allInputs']):
            if input_elem['visible']:
                logger.info(f"Input {i}: ID='{input_elem['id']}', Placeholder='{input_elem['placeholder']}', Type='{input_elem['type']}', Class='{input_elem['className'][:50]}...'")
        
        logger.info("\n=== VISIBLE TEXTAREA ELEMENTS ===")
        for i, textarea in enumerate(form_elements['allTextareas']):
            if textarea['visible']:
                logger.info(f"Textarea {i}: ID='{textarea['id']}', Placeholder='{textarea['placeholder']}', Class='{textarea['className'][:50]}...'")
        
        logger.info("\n=== VISIBLE BUTTON ELEMENTS ===")
        for i, button in enumerate(form_elements['allButtons']):
            if button['visible']:
                logger.info(f"Button {i}: Text='{button['textContent']}', ID='{button['id']}', DataTestId='{button['dataTestId']}', Class='{button['className'][:50]}...'")
        
        logger.info("\n=== POTENTIAL LINK FIELDS ===")
        for i, link_elem in enumerate(form_elements['linkLikeElements']):
            logger.info(f"Link Element {i}: {link_elem['element']}")
        
        logger.info("\n=== POTENTIAL PUBLISH BUTTONS ===")
        for i, publish_elem in enumerate(form_elements['publishLikeElements']):
            logger.info(f"Publish Element {i}: {publish_elem['element']}")
        
        # Get page source excerpt around forms
        logger.info("\n=== PAGE STRUCTURE ANALYSIS ===")
        page_structure = automation.driver.execute_script("""
            // Find form-like containers
            const formContainers = document.querySelectorAll('form, [data-test-id*="pin"], [data-test-id*="draft"], .pin-creation, .pin-draft');
            const results = [];
            
            formContainers.forEach((container, index) => {
                results.push({
                    index: index,
                    tagName: container.tagName,
                    id: container.id || '',
                    className: container.className || '',
                    dataTestId: container.getAttribute('data-test-id') || '',
                    innerHTML: container.innerHTML.substring(0, 500) + '...'
                });
            });
            
            return results;
        """)
        
        for i, container in enumerate(page_structure):
            logger.info(f"Form Container {i}: Tag={container['tagName']}, ID='{container['id']}', DataTestId='{container['dataTestId']}'")
        
        # Wait for manual inspection
        logger.info("\n=== MANUAL INSPECTION TIME ===")
        logger.info("Browser is open for manual inspection. Check the pin creation form.")
        logger.info("Look for:")
        logger.info("1. Any link/URL input fields")
        logger.info("2. Publish/Save buttons")
        logger.info("3. Form structure and data-test-ids")
        
        input("Press Enter when you've finished inspecting the page...")
        
        # Close browser
        automation.close_browser()
        
        return True
        
    except Exception as e:
        logger.error(f"Diagnostic error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Pinterest Page Element Diagnostic Tool")
    print("======================================")
    print("This will login to Pinterest, navigate to pin creation,")
    print("upload an image, and then analyze all form elements.")
    print()
    
    result = diagnose_pinterest_page()
    
    if result:
        print("\n✅ DIAGNOSTIC COMPLETED!")
        print("Check the log file for detailed element information.")
    else:
        print("\n❌ DIAGNOSTIC FAILED")
        print("Check the log file for error details.")
