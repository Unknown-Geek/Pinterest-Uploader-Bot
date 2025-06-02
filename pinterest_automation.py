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

class PinterestAutomation:    
    def __init__(self, headless=False, fast_typing=True):
        self.headless = headless
        self.driver = None
        self.wait = None
        self.logger = logging.getLogger(__name__)
        self.fast_typing = fast_typing  # New configuration option
        
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
                # Fall back to system PATH
                self.driver = webdriver.Chrome(options=chrome_options)
                
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 20)
            return True
        except Exception as e:
            self.logger.error(f"Failed to setup driver: {str(e)}")
            self.logger.error("Make sure ChromeDriver is installed. Run 'python setup_chromedriver.py' to auto-install.")
            return False
    
    def _human_delay(self, min_delay=1, max_delay=3):
        """Add human-like delay"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    def _type_like_human(self, element, text, delay_range=(0.05, 0.15), fast_mode=True):
        """Type text with human-like delays and enhanced React compatibility
        
        Args:
            element: The WebElement to type into
            text: The text to type
            delay_range: Range for character delays (used only when fast_mode=False)
            fast_mode: If True, use optimized typing for speed while maintaining React compatibility
        """
        # Clear the field first
        element.clear()
        
        if fast_mode:
            # OPTIMIZED APPROACH: Type text in chunks for speed while maintaining React compatibility
            self.logger.debug(f"Using optimized typing for: {text[:20]}...")
            
            # First, try direct value setting with comprehensive React event firing
            try:
                self.driver.execute_script("""
                    const element = arguments[0];
                    const text = arguments[1];
                    
                    // Focus the element
                    element.focus();
                    
                    // Clear any existing content
                    element.value = '';
                    
                    // Set the new value
                    element.value = text;
                    
                    // Fire comprehensive React event sequence
                    const events = [
                        'focus',
                        'keydown', 
                        'keypress', 
                        'input', 
                        'keyup', 
                        'change', 
                        'blur'
                    ];
                    
                    events.forEach(eventType => {
                        const event = new Event(eventType, { 
                            bubbles: true, 
                            cancelable: true 
                        });
                        element.dispatchEvent(event);
                    });
                    
                    // React-specific value tracker manipulation
                    if (element._valueTracker) {
                        element._valueTracker.setValue('');
                        element._valueTracker.setValue(text);
                    }
                    
                    // Additional React state triggers
                    if (element.__reactInternalInstance) {
                        element.__reactInternalInstance.memoizedProps.onChange &&
                        element.__reactInternalInstance.memoizedProps.onChange({
                            target: element,
                            currentTarget: element
                        });
                    }
                    
                    return true;
                """, element, text)
                
                # Small delay to let React process
                time.sleep(random.uniform(0.3, 0.6))
                
                # Validate the input was set correctly
                if element.get_attribute('value') == text or element.text == text:
                    self.logger.debug("Optimized typing successful")
                    return
                else:
                    self.logger.debug("Optimized typing validation failed, falling back to chunk typing")
                    
            except Exception as e:
                self.logger.debug(f"Direct value setting failed: {e}, falling back to chunk typing")
            
            # FALLBACK: Type in small chunks (faster than character-by-character)
            chunk_size = max(3, len(text) // 8)  # Adaptive chunk size
            chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
            
            for i, chunk in enumerate(chunks):
                element.send_keys(chunk)
                # Only add delays between chunks, not characters
                if i < len(chunks) - 1:  # Don't delay after the last chunk
                    time.sleep(random.uniform(0.15, 0.25))
        else:
            # ORIGINAL APPROACH: Character-by-character with delays (for compatibility)
            self.logger.debug(f"Using character-by-character typing for: {text[:20]}...")
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(*delay_range))
        
        # Final React compatibility events (always executed)
        try:
            # Space + backspace trick for additional React triggering
            element.send_keys(Keys.SPACE)
            element.send_keys(Keys.BACKSPACE)
            
            # Fire final events to ensure React sees the changes
            self.driver.execute_script("""
                const element = arguments[0];
                const events = ['input', 'change', 'blur'];
                events.forEach(eventType => {
                    const event = new Event(eventType, { bubbles: true });
                    element.dispatchEvent(event);
                });
            """, element)
        except:
            pass
    
    def login(self, email, password):
        """Login to Pinterest with enhanced reliability"""
        try:
            self.logger.info("Navigating to Pinterest login page...")
            self.driver.get("https://www.pinterest.com/login/")
            self._human_delay(3, 5)
            
            # Wait for and fill email
            self.logger.info("Entering email...")
            email_field = self.wait.until(EC.element_to_be_clickable((By.ID, "email")))
            self._type_like_human(email_field, email)
            self._human_delay()
            
            # Fill password
            self.logger.info("Entering password...")
            password_field = self.driver.find_element(By.ID, "password")
            self._type_like_human(password_field, password)
            self._human_delay()
            
            # Click login button
            self.logger.info("Clicking login button...")
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for login to complete
            self._human_delay(5, 8)
            
            # Check if login was successful
            if "/login/" not in self.driver.current_url:
                self.logger.info("Login successful!")
                return True
            else:
                self.logger.error("Login failed - still on login page")
                return False
                
        except Exception as e:
            self.logger.error(f"Login error: {str(e)}")
            return False
    
    def upload_image(self, image_path):
        """Upload image with multiple fallback methods"""
        try:
            self.logger.info("Navigating to pin creation page...")
            self.driver.get("https://www.pinterest.com/pin-builder/")
            self._human_delay(3, 5)
            
            # Method 1: Try direct file input
            try:
                file_input = self.wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[type='file'][accept*='image']")))
                
                # Make input visible
                self.driver.execute_script("""
                    arguments[0].style.opacity = '1';
                    arguments[0].style.display = 'block';
                    arguments[0].style.visibility = 'visible';
                    arguments[0].style.height = 'auto';
                    arguments[0].style.width = 'auto';
                """, file_input)
                
                self.logger.info(f"Uploading image: {os.path.abspath(image_path)}")
                file_input.send_keys(os.path.abspath(image_path))
                
                # Wait for upload to complete
                self._human_delay(5, 10)
                
                # Check if upload was successful
                upload_success = self.wait.until(EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id*='title']")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder*='title' i]")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='title' i]"))
                ))
                
                if upload_success:
                    self.logger.info("Image uploaded successfully!")
                    return True
                    
            except Exception as e:
                self.logger.warning(f"Direct upload method failed: {str(e)}")
                return False
                
        except Exception as e:
            self.logger.error(f"Image upload error: {str(e)}")
            return False
    
    def set_title(self, title):
        """Set pin title with multiple fallback methods"""
        try:
            self.logger.info(f"Setting title: {title}")
            self._human_delay(2, 4)
            
            # Method 1: Try textarea with pin-draft-title
            selectors = [
                "textarea[aria-label*='title' i]",
                "textarea[placeholder*='title' i]",
                "input[aria-label*='title' i]",
                "input[placeholder*='title' i]",
                "[data-test-id*='title'] textarea",
                "[data-test-id*='title'] input"
            ]
            
            for selector in selectors:
                try:
                    title_field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    title_field.click()
                    self._type_like_human(title_field, title)
                    self.logger.info(f"Title set using selector: {selector}")
                    return True
                except:
                    continue
            
            # Method 2: JavaScript approach
            try:
                result = self.driver.execute_script("""
                    function setTitle(title) {
                        // Try multiple selectors
                        const selectors = [
                            'textarea[aria-label*="title" i]',
                            'textarea[placeholder*="title" i]',
                            'input[aria-label*="title" i]',
                            'input[placeholder*="title" i]',
                            '[data-test-id*="title"] textarea',
                            '[data-test-id*="title"] input'
                        ];
                        
                        for (const selector of selectors) {
                            const elements = document.querySelectorAll(selector);
                            for (const element of elements) {
                                if (element.offsetParent !== null) { // visible
                                    element.focus();
                                    element.value = '';
                                    element.value = title;
                                    element.dispatchEvent(new Event('input', {bubbles: true}));
                                    element.dispatchEvent(new Event('change', {bubbles: true}));
                                    return true;
                                }
                            }
                        }
                        return false;
                    }
                    return setTitle(arguments[0]);
                """, title)
                
                if result:
                    self.logger.info("Title set using JavaScript method")
                    return True
                    
            except Exception as e:
                self.logger.warning(f"JavaScript title method failed: {str(e)}")
            
            self.logger.warning("Could not set title with any method")
            return False
            
        except Exception as e:
            self.logger.error(f"Set title error: {str(e)}")
            return False
    
    def set_description(self, description):
        """Set pin description with enhanced methods for Pinterest's React forms"""
        try:
            self.logger.info(f"Setting description: {description}")
            self._human_delay(1, 2)
            
            # Method 1: Enhanced Pinterest-specific description field interaction
            try:
                desc_field = self.wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "textarea[placeholder='Tell everyone what your Pin is about']")))
                
                # Focus the field first
                desc_field.click()
                self._human_delay(0.8, 1.2)
                
                # Clear any existing content with multiple methods
                desc_field.send_keys(Keys.CONTROL + "a")
                self._human_delay(0.2, 0.3)
                desc_field.send_keys(Keys.DELETE)
                self._human_delay(0.5, 0.8)
                
                # Type description character by character with deliberate timing
                for char in description:
                    desc_field.send_keys(char)
                    time.sleep(random.uniform(0.08, 0.15))
                
                # Trigger React events to ensure Pinterest recognizes the input
                self.driver.execute_script("""
                    const element = arguments[0];
                    const text = arguments[1];
                    
                    // Set value programmatically as backup
                    element.value = text;
                    
                    // Trigger comprehensive event sequence for React
                    const events = [
                        'focus', 'keydown', 'keypress', 'input', 
                        'keyup', 'change', 'blur'
                    ];
                    
                    events.forEach(eventType => {
                        const event = new Event(eventType, { 
                            bubbles: true, 
                            cancelable: true 
                        });
                        element.dispatchEvent(event);
                    });
                    
                    // Additional React-specific triggers
                    if (element._valueTracker) {
                        element._valueTracker.setValue('');
                    }
                """, desc_field, description)
                
                # Additional validation steps
                desc_field.send_keys(Keys.TAB)
                desc_field.send_keys(Keys.SHIFT + Keys.TAB)
                
                self.logger.info("Description set using Pinterest-specific selector")
                return True
                
            except Exception as e:
                self.logger.warning(f"Pinterest-specific description selector failed: {str(e)}")
            
            # Method 2: Enhanced Draft.js editor interaction
            try:
                desc_area = self.wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, ".public-DraftEditor-content")))
                
                # Click and focus
                desc_area.click()
                self._human_delay(0.8, 1.2)
                
                # Clear content with multiple approaches
                ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
                self._human_delay(0.3, 0.5)
                desc_area.send_keys(Keys.DELETE)
                self._human_delay(0.5, 0.8)
                
                # Type with deliberate pace for Draft.js
                for char in description:
                    desc_area.send_keys(char)
                    time.sleep(random.uniform(0.08, 0.15))
                
                # Draft.js specific event firing
                self.driver.execute_script("""
                    const element = arguments[0];
                    const text = arguments[1];
                    
                    // Set Draft.js content structure
                    element.innerHTML = '<div data-contents="true">' +
                        '<div data-block="true" data-editor="desc" data-offset-key="0-0-0">' +
                            '<div data-offset-key="0-0-0" class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr">' +
                                '<span data-offset-key="0-0-0">' +
                                    '<span data-text="true">' + text + '</span>' +
                                '</span>' +
                            '</div>' +
                        '</div>' +
                    '</div>';
                    
                    // Fire Draft.js events
                    const events = ['input', 'textInput', 'keydown', 'keyup', 'change'];
                    events.forEach(eventType => {
                        const event = new Event(eventType, { bubbles: true });
                        element.dispatchEvent(event);
                    });
                """, desc_area, description)
                
                self.logger.info("Description set using Draft.js editor")
                return True
                
            except Exception as e:
                self.logger.warning(f"Draft.js editor method failed: {str(e)}")
            
            # Method 3: Comprehensive JavaScript approach
            try:
                result = self.driver.execute_script("""
                    function setDescriptionAdvanced(desc) {
                        // Helper function for comprehensive input simulation
                        function simulateReactInput(element, text) {
                            element.focus();
                            
                            // Clear existing content
                            element.value = '';
                            if (element.innerHTML !== undefined) {
                                element.innerHTML = '';
                            }
                            
                            // Set the value
                            element.value = text;
                            
                            // Comprehensive event firing for React
                            const events = [
                                'focus', 'keydown', 'keypress', 'input', 
                                'keyup', 'change', 'blur'
                            ];
                            
                            events.forEach(eventType => {
                                const event = new Event(eventType, { 
                                    bubbles: true, 
                                    cancelable: true 
                                });
                                element.dispatchEvent(event);
                            });
                            
                            // React-specific value tracker reset
                            if (element._valueTracker) {
                                element._valueTracker.setValue('');
                            }
                            
                            return true;
                        }
                        
                        // Try Pinterest-specific selector first
                        const pinterestDesc = document.querySelector('textarea[placeholder="Tell everyone what your Pin is about"]');
                        if (pinterestDesc && pinterestDesc.offsetParent !== null) {
                            return simulateReactInput(pinterestDesc, desc);
                        }
                        
                        // Try Draft.js editor with enhanced manipulation
                        const draftEditor = document.querySelector('.public-DraftEditor-content');
                        if (draftEditor && draftEditor.offsetParent !== null) {
                            draftEditor.focus();
                            
                            // Set proper Draft.js HTML structure
                            const draftHTML = '<div data-contents="true">' +
                                '<div data-block="true" data-editor="desc" data-offset-key="0-0-0">' +
                                    '<div data-offset-key="0-0-0" class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr">' +
                                        '<span data-offset-key="0-0-0">' +
                                            '<span data-text="true">' + desc + '</span>' +
                                        '</span>' +
                                    '</div>' +
                                '</div>' +
                            '</div>';
                            
                            draftEditor.innerHTML = draftHTML;
                            
                            // Fire Draft.js events
                            const draftEvents = ['input', 'textInput', 'keydown', 'keyup', 'change'];
                            draftEvents.forEach(eventType => {
                                const event = new Event(eventType, { bubbles: true });
                                draftEditor.dispatchEvent(event);
                            });
                            
                            return true;
                        }
                        
                        // Try other common selectors
                        const selectors = [
                            'textarea[aria-label*="description" i]',
                            'textarea[placeholder*="description" i]',
                            'textarea[placeholder*="Tell everyone" i]',
                            'textarea[placeholder*="Pin is about" i]',
                            '[data-test-id*="description"] textarea',
                            'div[contenteditable="true"]'
                        ];
                        
                        for (const selector of selectors) {
                            const elements = document.querySelectorAll(selector);
                            for (const element of elements) {
                                if (element.offsetParent !== null) {
                                    if (element.tagName === 'DIV') {
                                        element.innerHTML = desc;
                                        element.dispatchEvent(new Event('input', {bubbles: true}));
                                    } else {
                                        return simulateReactInput(element, desc);
                                    }
                                    return true;
                                }
                            }
                        }
                        return false;
                    }
                    return setDescriptionAdvanced(arguments[0]);
                """, description)
                
                if result:
                    self.logger.info("Description set using JavaScript method")
                    return True
                    
            except Exception as e:
                self.logger.warning(f"JavaScript description method failed: {str(e)}")
              # Method 4: Fallback with other textarea selectors
            selectors = [
                "textarea[aria-label*='description' i]",
                "textarea[placeholder*='description' i]",
                "textarea[placeholder*='Tell everyone' i]",
                "textarea[placeholder*='Pin is about' i]",
                "[data-test-id*='description'] textarea",
                "div[contenteditable='true']"
            ]
            
            for selector in selectors:
                try:
                    desc_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if desc_field.is_displayed():
                        desc_field.click()
                        self._human_delay(0.5, 0.8)
                        desc_field.clear()
                        self._type_like_human(desc_field, description, (0.08, 0.15))
                        self.logger.info(f"Description set using selector: {selector}")
                        return True
                except:
                    continue
            
            self.logger.warning("Could not set description with any method")
            return False
            
        except Exception as e:
            self.logger.error(f"Set description error: {str(e)}")
            return False
    
    def set_link(self, link_url):
        """Set destination link with enhanced methods for Pinterest's dynamic link fields"""
        if not link_url:
            return True
            
        try:
            self.logger.info(f"Setting link: {link_url}")
            self._human_delay(1, 2)
            
            # Method 1: Direct textarea approach from working implementation
            try:
                # Look for Pinterest's textarea link field using contains
                self.logger.info("Attempting to find link field using textarea contains method...")
                link_field = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, '//textarea[contains(@id, "pin-draft-link")]')))
                
                self.logger.info(f"Found link field with ID: {link_field.get_attribute('id')}")
                
                # Focus and clear the field
                link_field.click()
                self._human_delay(0.5, 1)
                link_field.clear()
                
                # Send the URL directly
                link_field.send_keys(link_url)
                
                self.logger.info("Link set using textarea contains method")
                return True
                
            except Exception as e:
                self.logger.warning(f"Textarea contains link selector failed: {str(e)}")
            
            # Method 2: Try dynamic Pinterest link field IDs (previous working method)
            try:
                # Look for Pinterest's dynamic link field IDs (pin-draft-link-*)
                self.logger.info("Attempting to find link field with dynamic Pinterest ID...")
                link_field = self.wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "input[id^='pin-draft-link-']")))
                
                self.logger.info(f"Found link field with ID: {link_field.get_attribute('id')}")
                
                # Focus and clear the field
                link_field.click()
                self._human_delay(0.5, 1)
                link_field.clear()
                
                # Character by character typing for React compatibility
                for char in link_url:
                    link_field.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.1))
                
                # Trigger comprehensive React events
                self.driver.execute_script("""
                    const element = arguments[0];
                    const url = arguments[1];
                    
                    // Set value programmatically as backup
                    element.value = url;
                    
                    // Trigger comprehensive event sequence for React
                    const events = [
                        'focus', 'keydown', 'keypress', 'input', 
                        'keyup', 'change', 'blur'
                    ];
                    
                    events.forEach(eventType => {
                        const event = new Event(eventType, { 
                            bubbles: true, 
                            cancelable: true 
                        });
                        element.dispatchEvent(event);
                    });
                    
                    // React-specific value tracker handling
                    if (element._valueTracker) {
                        element._valueTracker.setValue('');
                    }
                """, link_field, link_url)
                
                self.logger.info("Link set using dynamic Pinterest ID selector")
                return True
                
            except Exception as e:
                self.logger.warning(f"Dynamic Pinterest ID link selector failed: {str(e)}")
              # Method 3: Enhanced Pinterest-specific link field with placeholder
            try:
                # Try the specific placeholder
                self.logger.info("Attempting to find link field with placeholder...")
                link_field = self.wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "input[placeholder='Add a destination link']")))
                
                # Focus and clear the field
                link_field.click()
                self._human_delay(0.5, 1)
                link_field.clear()
                
                # Send the URL directly (simpler approach)
                link_field.send_keys(link_url)
                
                self.logger.info("Link set using Pinterest placeholder selector")
                return True
                
            except Exception as e:
                self.logger.warning(f"Pinterest placeholder link selector failed: {str(e)}")
              # Method 4: Try common link selectors with enhanced React events
            selectors = [
                "input[aria-label*='link' i]",
                "input[placeholder*='link' i]", 
                "input[placeholder*='destination' i]",
                "input[aria-label*='website' i]",
                "input[placeholder*='website' i]",
                "input[aria-label*='url' i]",
                "[data-test-id*='link'] input",
                "[data-test-id*='website'] input",
                "input[type='url']"
            ]
            
            for selector in selectors:
                try:
                    link_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if link_field.is_displayed():
                        link_field.click()
                        self._human_delay(0.5, 0.8)
                        link_field.clear()
                        
                        # Simple direct input (like the working implementation)
                        link_field.send_keys(link_url)
                        
                        self.logger.info(f"Link set using selector: {selector}")
                        return True
                except:
                    continue
            
            # Method 5: Comprehensive JavaScript approach
            try:
                result = self.driver.execute_script("""
                    function setLinkAdvanced(url) {
                        // Helper function for React input simulation
                        function simulateReactInput(element, text) {
                            element.focus();
                            element.value = '';
                            element.value = text;
                            
                            // Comprehensive event firing for React
                            const events = [
                                'focus', 'keydown', 'keypress', 'input', 
                                'keyup', 'change', 'blur'
                            ];
                            
                            events.forEach(eventType => {
                                const event = new Event(eventType, { 
                                    bubbles: true, 
                                    cancelable: true 
                                });
                                element.dispatchEvent(event);
                            });
                            
                            // React-specific value tracker
                            if (element._valueTracker) {
                                element._valueTracker.setValue('');
                            }
                            
                            return true;
                        }
                        
                        // Try Pinterest-specific selectors first
                        const selectors = [
                            'textarea[id*="pin-draft-link"]',
                            'input[placeholder="Add a destination link"]',
                            'input[id^="pin-draft-link-"]',
                            'input[aria-label*="link" i]',
                            'input[placeholder*="link" i]',
                            'input[placeholder*="destination" i]',
                            'input[type="url"]',
                            'input[aria-label*="website" i]',
                            'input[placeholder*="website" i]',
                            'input[aria-label*="url" i]',
                            '[data-test-id*="link"] input',
                            '[data-test-id*="website"] input'
                        ];
                        
                        for (const selector of selectors) {
                            const elements = document.querySelectorAll(selector);
                            for (const element of elements) {
                                if (element.offsetParent !== null && 
                                    (element.type === 'text' || element.type === 'url' || element.type === '' || element.tagName === 'TEXTAREA')) {
                                    try {
                                        return simulateReactInput(element, url);
                                    } catch (e) {
                                        continue;
                                    }
                                }
                            }
                        }
                        
                        // Also try to find any input that might be a link field by context
                        const allInputs = document.querySelectorAll('input, textarea');
                        for (const input of allInputs) {
                            const inputContext = (input.id + ' ' + input.placeholder + ' ' + 
                                               (input.getAttribute('aria-label') || '') + ' ' + 
                                               input.name).toLowerCase();
                            if ((inputContext.includes('link') || inputContext.includes('url') || 
                                 inputContext.includes('website') || inputContext.includes('destination')) &&
                                input.offsetParent !== null) {
                                try {
                                    return simulateReactInput(input, url);
                                } catch (e) {
                                    continue;
                                }
                            }
                        }
                          return false;
                    }
                    return setLinkAdvanced(arguments[0]);
                """, link_url)
                
                if result:
                    self.logger.info("Link set using JavaScript method")
                    return True
                    
            except Exception as e:
                self.logger.warning(f"JavaScript link method failed: {str(e)}")
            
            self.logger.warning("Could not set link - continuing without link")
            return True  # Don't fail the entire process for missing link
            
        except Exception as e:
            self.logger.error(f"Set link error: {str(e)}")
            return True  # Don't fail the entire process for missing link
    def select_board(self, board_name):
        """Select board with enhanced reliability using updated Pinterest board row structure"""
        try:
            self.logger.info(f"Selecting board: {board_name}")
            self._human_delay(1, 2)

            # Method 1: Use the new board-row data-test-id structure
            try:
                # Click on board dropdown button using exact data-test-id
                board_dropdown = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, '//button[@data-test-id="board-dropdown-select-button"]')))
                board_dropdown.click()
                self.logger.info("Board dropdown clicked successfully")
                self._human_delay(2, 3)

                # Try the new board-row structure first
                board_row_selector = f'div[data-test-id="board-row-{board_name}"]'
                self.logger.info(f"Looking for board row: {board_row_selector}")
                try:
                    board_row = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, board_row_selector)))
                    if board_row.is_displayed():
                        # Try clicking the Publish button within the board row
                        try:
                            publish_button = board_row.find_element(
                                By.CSS_SELECTOR, 'button[aria-label="Publish"]')
                            if publish_button.is_displayed() and publish_button.is_enabled():
                                publish_button.click()
                                self.logger.info(f"Board '{board_name}' selected using board-row structure (Publish button)")
                                return True
                        except Exception as e:
                            self.logger.debug(f"Publish button not found or not clickable: {str(e)}")
                        # Fallback: click the board row itself
                        try:
                            board_row.click()
                            self.logger.info(f"Board '{board_name}' selected by clicking board row")
                            return True
                        except Exception as e:
                            self.logger.debug(f"Board row not clickable: {str(e)}")
                except Exception as e:
                    self.logger.debug(f"Board-row structure method failed: {str(e)}")

                # Debug: Log all available board rows
                try:
                    available_boards = self.driver.execute_script("""
                        const boardRows = document.querySelectorAll('div[data-test-id*="board-row-"]');
                        const boards = Array.from(boardRows).map(row => {
                            const testId = row.getAttribute('data-test-id');
                            const boardName = testId ? testId.replace('board-row-', '') : 'unknown';
                            const titleElement = row.querySelector('div[title]');
                            const title = titleElement ? titleElement.getAttribute('title') : 'no title';
                            return {name: boardName, title: title, testId: testId};
                        });
                        return boards;
                    """)
                    self.logger.info(f"Available board rows: {available_boards}")
                    # Take a screenshot for debugging
                    try:
                        screenshot_path = f"board_dropdown_debug_{int(time.time())}.png"
                        self.driver.save_screenshot(screenshot_path)
                        self.logger.info(f"Debug screenshot saved: {screenshot_path}")
                    except Exception:
                        pass
                except Exception as debug_e:
                    self.logger.debug(f"Debug logging failed: {str(debug_e)}")

                # Method 2: Try alternative selectors for board-row structure
                alternative_selectors = [
                    f'//div[@data-test-id="board-row-{board_name}"]//button[@aria-label="Publish"]',
                    f'//div[@data-test-id="board-row-{board_name}"]',
                    f'//div[contains(@data-test-id, "board-row") and contains(@data-test-id, "{board_name}")]',
                    f'//div[@data-test-id="board-row-{board_name}"]//button[contains(text(), "Publish")]'
                ]
                for i, selector in enumerate(alternative_selectors):
                    try:
                        self.logger.info(f"Trying alternative selector {i+1}: {selector}")
                        board_element = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, selector)))
                        board_element.click()
                        self.logger.info(f"Board selected using alternative selector {i+1}")
                        return True
                    except Exception as e:
                        self.logger.debug(f"Alternative selector {i+1} failed: {str(e)}")
                        continue

                # Method 3: Fallback to original selectors if board-row structure fails
                self.logger.info("Falling back to original board selection methods")
                fallback_selectors = [
                    f'//div[@role="option"]//div[contains(text(), "{board_name}")]',
                    f'//div[@role="option" and contains(., "{board_name}")]',
                    f'//*[@role="option"]//*[contains(text(), "{board_name}")]',
                    f'//div[@role="option"]//span[contains(text(), "{board_name}")]',
                    f'//li[@role="option" and contains(., "{board_name}")]',
                    f'//div[contains(@class, "option") and contains(., "{board_name}")]',
                    f'//div[text()="{board_name}"]',
                    f'//span[text()="{board_name}"]',
                    f'//*[contains(text(), "{board_name}") and contains(@class, "board")]',
                    f'//*[text()="{board_name}" and ancestor::*[@role="option"]]'
                ]
                for i, selector in enumerate(fallback_selectors):
                    try:
                        self.logger.info(f"Trying fallback selector {i+1}: {selector}")
                        board_option = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, selector)))
                        board_option.click()
                        self.logger.info(f"Board selected using fallback selector {i+1}: {selector}")
                        return True
                    except Exception as e:
                        self.logger.debug(f"Fallback selector {i+1} failed: {str(e)}")
                        continue

                # If no direct selectors work, try finding the parent clickable element
                self.logger.info(f"Trying parent element approach for: {board_name}")
                text_elements = self.driver.find_elements(By.XPATH, f'//*[contains(text(), "{board_name}")]')
                for text_element in text_elements:
                    try:
                        if text_element.is_displayed() and text_element.is_enabled():
                            text_element.click()
                            self.logger.info(f"Board selected by clicking text element: {board_name}")
                            return True
                    except Exception:
                        pass
                    # Find the closest clickable parent
                    try:
                        clickable_parent = self.driver.execute_script("""
                            function findClickableParent(element) {
                                let current = element;
                                while (current && current !== document.body) {
                                    if (current.onclick || current.getAttribute('role') === 'option' || 
                                        current.tagName === 'BUTTON' || current.tagName === 'A' ||
                                        current.getAttribute('data-test-id') || 
                                        window.getComputedStyle(current).cursor === 'pointer') {
                                        return current;
                                    }
                                    current = current.parentElement;
                                }
                                return null;
                            }
                            return findClickableParent(arguments[0]);
                        """, text_element)
                        if clickable_parent:
                            clickable_parent.click()
                            self.logger.info(f"Board selected by clicking parent element: {board_name}")
                            return True
                    except Exception:
                        pass
                # End of parent clickable element fallback
            except Exception as e:
                self.logger.warning(f"Board selection method failed: {str(e)}")

            # Method 4: JavaScript-based selection with board-row awareness
            try:
                board_dropdown = self.wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "[data-test-id='board-dropdown-select-button']")))
                board_dropdown.click()
                self._human_delay(2, 3)
                board_found = self.driver.execute_script("""
                    const boardName = arguments[0];
                    // First try the board-row structure
                    const boardRowSelector = `div[data-test-id=\"board-row-${boardName}\"]`;
                    const boardRow = document.querySelector(boardRowSelector);
                    if (boardRow) {
                        const publishButton = boardRow.querySelector('button[aria-label="Publish"]');
                        if (publishButton) {
                            publishButton.click();
                            return true;
                        } else {
                            boardRow.click();
                            return true;
                        }
                    }
                    // Fallback to traditional option selection
                    const options = document.querySelectorAll('[role="option"], .board-option, div[data-test-id*="board"]');
                    for (const option of options) {
                        if (option.textContent.trim().toLowerCase().includes(boardName.toLowerCase())) {
                            option.click();
                            return true;
                        }
                    }
                    // Try broader search
                    const allDivs = document.querySelectorAll('div');
                    for (const div of allDivs) {
                        if (div.textContent.trim().toLowerCase() === boardName.toLowerCase() && 
                            div.offsetParent !== null) {
                            // Find clickable parent
                            let parent = div;
                            while (parent && parent !== document.body) {
                                if (parent.onclick || parent.getAttribute('role') === 'option' || 
                                    parent.style.cursor === 'pointer' || 
                                    window.getComputedStyle(parent).cursor === 'pointer') {
                                    parent.click();
                                    return true;
                                }
                                parent = parent.parentElement;
                            }
                        }
                    }
                    return false;
                """, board_name)
                if board_found:
                    self.logger.info("Board selected using JavaScript method")
                    return True
            except Exception as e:
                self.logger.warning(f"JavaScript board selection failed: {str(e)}")

            self.logger.warning(f"Could not select board '{board_name}' - using default")
            return True  # Don't fail the entire process
        except Exception as e:
            self.logger.error(f"Select board error: {str(e)}")
            return True  # Don't fail the entire process
    
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
        
    def publish_pin(self):
        """Publish the pin with multiple fallback methods and enhanced debugging"""
        try:
            self.logger.info("Publishing pin...")
            self._human_delay(2, 3)
            
            # First check if pin was already published (e.g., during board selection)
            already_published = self.driver.execute_script("""
                // Check for success indicators that suggest pin is already published
                const bodyText = document.body.innerText.toLowerCase();
                return bodyText.includes('saved to') ||
                       bodyText.includes('pin created') ||
                       bodyText.includes('your pin was saved') ||
                       bodyText.includes('successfully published') ||
                       bodyText.includes('pin saved') ||
                       !window.location.href.includes('pin-creation') && 
                       !window.location.href.includes('pin-builder');
            """)
            
            if already_published:
                self.logger.info("Pin appears to already be published!")
                return True
            
            # Debug: Log all available buttons for troubleshooting
            button_debug_info = self.driver.execute_script("""
                const buttons = document.querySelectorAll('button, input[type="submit"], [role="button"]');
                const buttonInfo = Array.from(buttons)
                    .filter(btn => btn.offsetParent !== null) // Only visible buttons
                    .map(btn => ({
                        text: btn.textContent?.trim() || btn.value || '',
                        ariaLabel: btn.getAttribute('aria-label') || '',
                        dataTestId: btn.getAttribute('data-test-id') || '',
                        className: btn.className || '',
                        type: btn.type || '',
                        isEnabled: btn.disabled === false,
                        tagName: btn.tagName
                    }));
                return buttonInfo;
            """)
            self.logger.info(f"Available buttons on page: {button_debug_info}")
            
            # Try multiple selectors for publish button with more comprehensive list
            publish_selectors = [
                "[data-test-id='board-dropdown-save-button']",
                "[data-test-id='save-button']", 
                "[data-test-id='publish-button']",
                "[data-test-id='done-button']",
                "button[data-test-id*='publish']",
                "button[data-test-id*='save']",
                "button[data-test-id*='done']",
                "button[aria-label*='Publish']",
                "button[aria-label*='Save']",
                "button[aria-label*='Done']",
                "button[type='submit']",
                "button.primary",
                ".publish-button",
                ".save-button",
                "button:contains('Publish')",
                "button:contains('Save')",
                "button:contains('Done')"
            ]
            
            for i, selector in enumerate(publish_selectors):
                try:
                    self.logger.debug(f"Trying publish selector {i+1}: {selector}")
                    publish_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    if publish_button.is_displayed() and publish_button.is_enabled():
                        self.logger.info(f"Found publish button with selector: {selector}")
                        publish_button.click()
                        self.logger.info(f"Pin published successfully using selector: {selector}")
                        # Wait and verify the click worked
                        self._human_delay(2, 3)
                        return self._verify_publish_success()
                except Exception as e:
                    self.logger.debug(f"Selector {selector} failed: {str(e)}")
                    continue
            
            # Enhanced JavaScript fallback with debugging and more patience
            self.logger.info("Trying JavaScript fallback for publish button")
            result = self.driver.execute_script("""
                function findAndClickPublishButton() {
                    console.log('Starting publish button search...');
                    
                    // Get all potential buttons
                    const allButtons = document.querySelectorAll('button, input[type="submit"], [role="button"]');
                    const visibleButtons = Array.from(allButtons).filter(btn => btn.offsetParent !== null);
                    
                    console.log(`Found ${visibleButtons.length} visible buttons`);
                    
                    // Try various button text patterns (more comprehensive)
                    const publishTexts = [
                        'publish', 'save', 'post', 'done', 'create pin', 'save pin', 
                        'publish pin', 'submit', 'finish', 'complete', 'create'
                    ];
                    
                    // First pass: exact text matches
                    for (const button of visibleButtons) {
                        const text = (button.textContent || button.value || '').toLowerCase().trim();
                        const ariaLabel = (button.getAttribute('aria-label') || '').toLowerCase();
                        const dataTestId = (button.getAttribute('data-test-id') || '').toLowerCase();
                        
                        console.log(`Checking button: text="${text}", aria="${ariaLabel}", testId="${dataTestId}"`);
                        
                        // Check for exact matches first
                        for (const publishText of publishTexts) {
                            if (text === publishText || ariaLabel === publishText || 
                                dataTestId.includes(publishText)) {
                                console.log(`Found exact match for "${publishText}"`);
                                button.click();
                                return { success: true, method: `exact match: ${publishText}` };
                            }
                        }
                    }
                    
                    // Second pass: partial matches
                    for (const button of visibleButtons) {
                        const text = (button.textContent || button.value || '').toLowerCase().trim();
                        const ariaLabel = (button.getAttribute('aria-label') || '').toLowerCase();
                        const dataTestId = (button.getAttribute('data-test-id') || '').toLowerCase();
                        
                        for (const publishText of publishTexts) {
                            if (text.includes(publishText) || ariaLabel.includes(publishText) || 
                                dataTestId.includes(publishText)) {
                                console.log(`Found partial match for "${publishText}"`);
                                button.click();
                                return { success: true, method: `partial match: ${publishText}` };
                            }
                        }
                    }
                    
                    // Third pass: Look for primary/submit buttons
                    for (const button of visibleButtons) {
                        if (button.type === 'submit' || 
                            button.classList.contains('primary') ||
                            button.classList.contains('btn-primary') ||
                            button.getAttribute('data-test-id')?.includes('save') ||
                            button.getAttribute('data-test-id')?.includes('publish')) {
                            console.log('Found primary/submit button');
                            button.click();
                            return { success: true, method: 'primary/submit button' };
                        }
                    }
                    
                    // Fourth pass: Look for Pinterest-specific contexts
                    const boardDropdownSave = document.querySelector('[data-test-id*="board-dropdown"] button');
                    if (boardDropdownSave && boardDropdownSave.offsetParent) {
                        console.log('Found board dropdown save button');
                        boardDropdownSave.click();
                        return { success: true, method: 'board dropdown button' };
                    }
                    
                    // Last resort: try the most prominent button
                    const prominentButtons = visibleButtons.filter(btn => 
                        btn.offsetWidth > 50 && btn.offsetHeight > 20 && 
                        !btn.textContent.toLowerCase().includes('cancel') &&
                        !btn.textContent.toLowerCase().includes('back')
                    );
                    
                    if (prominentButtons.length > 0) {
                        console.log('Trying most prominent button as last resort');
                        prominentButtons[0].click();
                        return { success: true, method: 'prominent button fallback' };
                    }
                    
                    return { success: false, method: 'no suitable button found' };
                }
                return findAndClickPublishButton();
            """)
            
            if result and result.get('success'):
                self.logger.info(f"Pin published using JavaScript method: {result.get('method')}")
                self._human_delay(2, 3)
                return self._verify_publish_success()
            else:
                self.logger.warning(f"Could not find publish button - tried method: {result.get('method') if result else 'script failed'}")
                
                # Take a screenshot for debugging
                try:
                    screenshot_path = f"publish_debug_{int(time.time())}.png"
                    self.driver.save_screenshot(screenshot_path)
                    self.logger.info(f"Debug screenshot saved: {screenshot_path}")
                except Exception:
                    pass
                
                # Wait and check for success indicators one more time
                self._human_delay(3, 5)
                return self._verify_publish_success()
                
        except Exception as e:
            self.logger.error(f"Publish pin error: {str(e)}")
            return False  # Return False on actual errors
    
    def _verify_publish_success(self):
        """Verify if the pin was successfully published"""
        try:
            success_check = self.driver.execute_script("""
                const bodyText = document.body.innerText.toLowerCase();
                const url = window.location.href.toLowerCase();
                
                // Check for success text indicators
                const hasSuccessText = bodyText.includes('saved to') ||
                       bodyText.includes('pin created') ||
                       bodyText.includes('your pin was saved') ||
                       bodyText.includes('successfully published') ||
                       bodyText.includes('pin saved');
                
                // Check if we've been redirected away from creation page
                const redirected = !url.includes('pin-creation') && !url.includes('pin-builder');
                
                // Check if we're on a pin page now
                const onPinPage = url.includes('/pin/');
                
                return hasSuccessText || redirected || onPinPage;
            """)
            
            if success_check:
                self.logger.info("Pin appears to have been published successfully")
                return True
            else:
                self.logger.warning("Could not verify pin publication success")
                return False
        except Exception as e:
            self.logger.error(f"Error verifying publish success: {str(e)}")
            return False
    
    def upload_pin(self, email, password, image_path, title, description, board_name, link_url=None):
        """Complete pin upload workflow - the main method called by Flask app"""
        try:
            self.logger.info("=== STARTING COMPLETE PIN UPLOAD WORKFLOW ===")
            
            # Initialize driver
            if not self._setup_driver():
                return {
                    'success': False,
                    'message': 'Failed to initialize browser driver'
                }
            
            # Login to Pinterest
            if not self.login(email, password):
                return {
                    'success': False,
                    'message': 'Failed to login to Pinterest. Please check your credentials.'
                }
            
            # Navigate to pin creation
            if not self.navigate_to_pin_creation():
                return {
                    'success': False,
                    'message': 'Failed to navigate to pin creation page'
                }
            
            # Upload image
            if not self.upload_image(image_path):
                return {
                    'success': False,
                    'message': 'Failed to upload image'
                }
            
            # Set title
            if not self.set_title(title):
                return {
                    'success': False,
                    'message': 'Failed to set pin title'
                }
            
            # Set description
            if not self.set_description(description):
                return {
                    'success': False,
                    'message': 'Failed to set pin description'
                }
            
            # Set link (optional - don't fail if this doesn't work)
            if link_url:
                self.set_link(link_url)
              # Select board
            if not self.select_board(board_name):
                return {
                    'success': False,
                    'message': f'Failed to select board: {board_name}'
                }
              # Publish pin (more persistent about success)
            publish_success = self.publish_pin()
            if not publish_success:
                self.logger.warning("Publish step failed - attempting to verify if pin was still saved")
                # Give it one more chance - sometimes Pinterest saves pins even if button clicks fail
                self._human_delay(3, 5)
                final_check = self._verify_publish_success()
                if not final_check:
                    # Take a final screenshot for debugging
                    try:
                        screenshot_path = f"final_publish_failure_{int(time.time())}.png"
                        self.driver.save_screenshot(screenshot_path)
                        self.logger.info(f"Final failure screenshot saved: {screenshot_path}")
                    except Exception:
                        pass
                    
                    return {
                        'success': False,
                        'message': 'Failed to publish pin - could not find or click publish button'
                    }
            
            # Wait a bit for Pinterest to process
            self._human_delay(3, 5)
            
            # Check for success by looking at URL change
            current_url = self.driver.current_url
            if "pin-builder" not in current_url and "pin-creation" not in current_url:
                # Successfully redirected away from pin creation page
                pin_url = current_url if "/pin/" in current_url else None
                
                self.logger.info("=== PIN UPLOAD COMPLETED SUCCESSFULLY ===")
                return {
                    'success': True,
                    'message': 'Pin uploaded successfully to Pinterest!',
                    'pin_url': pin_url
                }
            else:
                # Still on pin creation page - check for success indicators
                success_text = self.driver.execute_script("""
                    return document.body.innerText.includes('Saved to') ||
                           document.body.innerText.includes('Pin created') ||
                           document.body.innerText.includes('Your Pin was saved') ||
                           document.body.innerText.includes('Successfully published');
                """)
                
                if success_text:
                    self.logger.info("Pin appears to have been published successfully")
                    return {
                        'success': True,
                        'message': 'Pin uploaded successfully to Pinterest!'
                    }
                else:
                    return {
                        'success': False,
                        'message': 'Pin upload may have failed - please check your Pinterest account'
                    }
            
        except Exception as e:
            self.logger.error(f"Upload pin workflow error: {str(e)}")
            return {
                'success': False,
                'message': f'Upload failed with error: {str(e)}'
            }
        finally:
            # Always clean up the browser
            self.quit()
    
    def quit(self):
        """Close browser session and cleanup"""
        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
                self.logger.info("Browser session closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing browser: {str(e)}")
