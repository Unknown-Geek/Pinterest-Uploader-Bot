# Optimized Pinterest Automation - Keeping Only Working Methods
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import os
import logging
import random

class PinterestAutomationOptimized:
    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None
        self.wait = None
        self.logger = logging.getLogger(__name__)
        
    def _setup_driver(self):
        """Setup Chrome WebDriver with optimized options"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        # Essential options for reliability
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        
        # Anti-detection measures
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Performance optimizations
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')  # Faster loading
        
        try:
            # Try local ChromeDriver first
            local_driver_path = os.path.join(os.path.dirname(__file__), 'drivers', 'chromedriver.exe')
            if os.path.exists(local_driver_path):
                self.driver = webdriver.Chrome(executable_path=local_driver_path, options=chrome_options)
            else:
                # Fallback to system PATH ChromeDriver
                self.driver = webdriver.Chrome(options=chrome_options)
                
            self.wait = WebDriverWait(self.driver, 20)
            
            # Execute script to hide automation indicators
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
        except Exception as e:
            self.logger.error(f"Failed to setup driver: {str(e)}")
            raise
    
    def _human_delay(self, min_delay=1, max_delay=3):
        """Add human-like delay"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
        
    def start_browser(self):
        """Start browser session"""
        try:
            self._setup_driver()
            self.logger.info("Browser started successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start browser: {str(e)}")
            return False
    
    def login(self, email, password):
        """Login to Pinterest"""
        try:
            self.logger.info("Navigating to Pinterest login page...")
            self.driver.get("https://www.pinterest.com/login/")
            self._human_delay(2, 4)
            
            # Enter email
            self.logger.info("Entering email...")
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
            email_field.clear()
            email_field.send_keys(email)
            self._human_delay(1, 2)
            
            # Enter password
            self.logger.info("Entering password...")
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(password)
            self._human_delay(1, 2)
            
            # Click login button
            self.logger.info("Clicking login button...")
            login_button = self.driver.find_element(By.CSS_SELECTOR, "[data-test-id='registerFormSubmitButton']")
            login_button.click()
            
            # Wait for successful login
            self._human_delay(5, 8)
            
            # Check if login was successful by looking for home page elements
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='header-profile']")))
                self.logger.info("Login successful!")
                return True
            except TimeoutException:
                self.logger.error("Login failed - could not find profile element")
                return False
                
        except Exception as e:
            self.logger.error(f"Login error: {str(e)}")
            return False
    
    def navigate_to_pin_creation(self):
        """Navigate to pin creation page"""
        try:
            self.logger.info("Navigating to pin creation page...")
            self.driver.get("https://www.pinterest.com/pin-creation-tool/")
            self._human_delay(3, 5)
            return True
        except Exception as e:
            self.logger.error(f"Navigation error: {str(e)}")
            return False
    
    def upload_image(self, image_path):
        """Upload image - WORKING METHOD"""
        try:
            self.logger.info(f"Uploading image: {image_path}")
            
            # Find file input
            file_input = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[type='file']")))
            
            # Upload file
            file_input.send_keys(image_path)
            
            # Wait for upload to complete
            self._human_delay(3, 6)
            
            # Verify upload success by checking for image preview or upload success indicators
            try:
                self.wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[data-test-id='pin-draft-image'], img[src*='blob:'], .uploaded-image")))
                self.logger.info("Image uploaded successfully!")
                return True
            except TimeoutException:
                self.logger.warning("Could not verify image upload, but proceeding...")
                return True
                
        except Exception as e:
            self.logger.error(f"Upload image error: {str(e)}")
            return False
    
    def set_title(self, title):
        """Set pin title - WORKING METHOD"""
        try:
            self.logger.info(f"Setting title: {title}")
            self._human_delay(1, 2)
            
            # Use the working selector from logs
            title_field = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "textarea[placeholder*='title' i]")))
            
            title_field.click()
            self._human_delay(0.5, 1)
            title_field.clear()
            
            # Character by character typing for React compatibility
            for char in title:
                title_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.1))
            
            self.logger.info("Title set using working selector")
            return True
            
        except Exception as e:
            self.logger.error(f"Set title error: {str(e)}")
            return False
    
    def set_description(self, description):
        """Set pin description - OPTIMIZED TO USE ONLY WORKING METHOD"""
        try:
            self.logger.info(f"Setting description: {description}")
            self._human_delay(2, 3)
            
            # Skip the failing Pinterest-specific selector, go straight to Draft.js method
            self.logger.info("Using Draft.js editor method (proven working)...")
            
            result = self.driver.execute_script("""
                function setDescriptionDraftJS(description) {
                    // Find Draft.js editor container
                    const draftContainers = document.querySelectorAll('[data-test-id="pin-draft-description-container"] .public-DraftEditor-content, .notranslate.public-DraftEditor-content');
                    
                    for (const container of draftContainers) {
                        if (container.isContentEditable) {
                            try {
                                // Focus on the container
                                container.focus();
                                
                                // Clear existing content
                                container.innerHTML = '';
                                
                                // Set new content
                                container.textContent = description;
                                
                                // Fire comprehensive events for Draft.js
                                const events = ['focus', 'input', 'change', 'blur'];
                                events.forEach(eventType => {
                                    const event = new Event(eventType, { bubbles: true, cancelable: true });
                                    container.dispatchEvent(event);
                                });
                                
                                return true;
                            } catch (e) {
                                continue;
                            }
                        }
                    }
                    return false;
                }
                return setDescriptionDraftJS(arguments[0]);
            """, description)
            
            if result:
                self.logger.info("Description set using Draft.js editor")
                return True
            else:
                self.logger.warning("Could not set description")
                return False
            
        except Exception as e:
            self.logger.error(f"Set description error: {str(e)}")
            return False
    
    def set_link(self, link_url):
        """Set destination link - ENHANCED FOR BETTER DETECTION"""
        if not link_url:
            return True
            
        try:
            self.logger.info(f"Setting link: {link_url}")
            self._human_delay(1, 2)
            
            # Enhanced JavaScript approach to find link field more reliably
            result = self.driver.execute_script("""
                function findAndSetLinkField(url) {
                    // Helper function for React input simulation
                    function simulateReactInput(element, text) {
                        element.focus();
                        element.value = '';
                        element.value = text;
                        
                        // Comprehensive event firing for React
                        const events = ['focus', 'keydown', 'keypress', 'input', 'keyup', 'change', 'blur'];
                        events.forEach(eventType => {
                            const event = new Event(eventType, { bubbles: true, cancelable: true });
                            element.dispatchEvent(event);
                        });
                        
                        // React-specific value tracker
                        if (element._valueTracker) {
                            element._valueTracker.setValue('');
                        }
                        
                        return true;
                    }
                    
                    // First, look for any input fields that might be link fields
                    const allInputs = document.querySelectorAll('input');
                    console.log('Found', allInputs.length, 'input elements');
                    
                    for (const input of allInputs) {
                        // Get all context about this input
                        const inputId = input.id || '';
                        const inputPlaceholder = input.placeholder || '';
                        const inputAriaLabel = input.getAttribute('aria-label') || '';
                        const inputName = input.name || '';
                        const inputType = input.type || '';
                        
                        const context = (inputId + ' ' + inputPlaceholder + ' ' + inputAriaLabel + ' ' + inputName).toLowerCase();
                        
                        console.log('Checking input:', {
                            id: inputId,
                            placeholder: inputPlaceholder,
                            ariaLabel: inputAriaLabel,
                            type: inputType,
                            visible: input.offsetParent !== null
                        });
                        
                        // Check if this looks like a link field
                        if ((context.includes('link') || 
                             context.includes('url') || 
                             context.includes('website') || 
                             context.includes('destination') ||
                             inputId.includes('pin-draft-link') ||
                             inputPlaceholder.includes('destination')) &&
                            input.offsetParent !== null) {
                            
                            try {
                                console.log('Attempting to set link on:', inputId || inputPlaceholder || 'unnamed input');
                                return simulateReactInput(input, url);
                            } catch (e) {
                                console.log('Failed to set on this input:', e);
                                continue;
                            }
                        }
                    }
                    
                    return false;
                }
                return findAndSetLinkField(arguments[0]);
            """, link_url)
            
            if result:
                self.logger.info("Link set using enhanced JavaScript method")
                return True
            else:
                self.logger.warning("Could not find link field - may not be available on this Pinterest layout")
                return True  # Don't fail the entire process
                
        except Exception as e:
            self.logger.error(f"Set link error: {str(e)}")
            return True  # Don't fail the entire process
    
    def select_board(self, board_name):
        """Select board - USING WORKING JAVASCRIPT METHOD"""
        try:
            self.logger.info(f"Selecting board: {board_name}")
            self._human_delay(1, 2)
            
            # Use the working JavaScript method from logs
            result = self.driver.execute_script("""
                function selectBoardAdvanced(boardName) {
                    // First try to find and click the board dropdown
                    const dropdownSelectors = [
                        '[data-test-id="board-dropdown-select-button"]',
                        '[data-test-id="board-dropdown"]',
                        'button[aria-label*="board" i]',
                        'div[role="button"]:has-text("Board")',
                        '.board-dropdown, .board-selector'
                    ];
                    
                    for (const selector of dropdownSelectors) {
                        const dropdown = document.querySelector(selector);
                        if (dropdown && dropdown.offsetParent !== null) {
                            dropdown.click();
                            // Wait a moment for dropdown to open
                            setTimeout(() => {
                                // Now find the specific board
                                const boardOptions = document.querySelectorAll('[role="option"], .board-option, div[data-test-id*="board"]');
                                for (const option of boardOptions) {
                                    if (option.textContent.trim() === boardName) {
                                        option.click();
                                        return true;
                                    }
                                }
                            }, 1000);
                            return true;
                        }
                    }
                    return false;
                }
                return selectBoardAdvanced(arguments[0]);
            """, board_name)
            
            if result:
                self.logger.info("Board selection attempted using JavaScript method")
                return True
            else:
                self.logger.warning(f"Could not select board: {board_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Select board error: {str(e)}")
            return False
    
    def publish_pin(self):
        """Publish the pin"""
        try:
            self.logger.info("Publishing pin...")
            self._human_delay(2, 3)
            
            # Try multiple selectors for publish button
            publish_selectors = [
                "[data-test-id='board-dropdown-save-button']",
                "button[data-test-id*='publish']",
                "button[data-test-id*='save']",
                "button:contains('Publish')",
                "button:contains('Save')"
            ]
            
            for selector in publish_selectors:
                try:
                    publish_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if publish_button.is_displayed():
                        publish_button.click()
                        self.logger.info("Pin published successfully!")
                        return True
                except:
                    continue
            
            # JavaScript fallback
            result = self.driver.execute_script("""
                const buttons = document.querySelectorAll('button');
                for (const button of buttons) {
                    const text = button.textContent.toLowerCase();
                    if (text.includes('publish') || text.includes('save') || text.includes('post')) {
                        button.click();
                        return true;
                    }
                }
                return false;
            """)
            
            if result:
                self.logger.info("Pin published using JavaScript method!")
                return True
            else:
                self.logger.warning("Could not find publish button")
                return False
                
        except Exception as e:
            self.logger.error(f"Publish pin error: {str(e)}")
            return False
    
    def create_pin(self, image_path, title, description, link_url=None, board_name="Wallpapers"):
        """Create a complete pin using only working methods"""
        try:
            self.logger.info("=== STARTING OPTIMIZED PIN CREATION ===")
            
            # Navigate to pin creation
            if not self.navigate_to_pin_creation():
                return False
            
            # Upload image (WORKING)
            if not self.upload_image(image_path):
                return False
            
            # Set title (WORKING)
            if not self.set_title(title):
                return False
            
            # Set description (WORKING - Draft.js method)
            if not self.set_description(description):
                return False
            
            # Set link (ENHANCED)
            if link_url:
                self.set_link(link_url)  # Don't fail if this doesn't work
            
            # Select board (WORKING - JavaScript method)
            if not self.select_board(board_name):
                return False
            
            # Publish pin
            if not self.publish_pin():
                return False
            
            self.logger.info("=== PIN CREATION COMPLETED SUCCESSFULLY ===")
            return True
            
        except Exception as e:
            self.logger.error(f"Create pin error: {str(e)}")
            return False
    
    def close_browser(self):
        """Close browser session"""
        try:
            if self.driver:
                self.driver.quit()
                self.logger.info("Browser closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing browser: {str(e)}")
