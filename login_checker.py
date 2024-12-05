from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from datetime import datetime
import os
from dotenv import load_dotenv
import sys
import time
import json

# Load environment variables
load_dotenv()

class LoginChecker:
    def __init__(self):
        # Set config file path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(script_dir, "config.json")
        
        # Load configuration
        self.load_config()
        self.setup_driver()
        
        # Get credentials from config
        self.username = self.config.get('credentials', {}).get('username', '')
        self.password = self.config.get('credentials', {}).get('password', '')
        
        if not self.username or not self.password:
            print("Warning: Credentials not set in config. Please set them in config.json.")
        
    def setup_driver(self):
        """Setup Edge driver with appropriate options"""
        try:
            edge_options = Options()
            # Removed headless mode to make browser visible
            edge_options.add_argument("--no-sandbox")
            edge_options.add_argument("--disable-dev-shm-usage")
            edge_options.add_argument("--disable-gpu")
            
            # Install Edge WebDriver using webdriver_manager
            driver_path = EdgeChromiumDriverManager().install()
            service = Service(driver_path)
            
            # Create the WebDriver instance
            self.driver = webdriver.Edge(service=service, options=edge_options)
            self.driver.implicitly_wait(10)
            
        except Exception as e:
            print(f"Error setting up Edge driver: {str(e)}")
            print("\nPlease make sure you have Microsoft Edge installed on your system.")
            print("Edge should be installed by default on Windows 10/11.")
            sys.exit(1)

    def load_config(self):
        """Load configuration from config.json"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                'use_gui': True,  # Preserve GUI setting
                'delay_seconds': 3,
                'credentials': {
                    'username': '',
                    'password': ''
                },
                'urls': []
            }
            # Only create a new config file if one doesn't exist
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)

    def check_login(self, url):
        """Attempt to login to a given URL and return the result"""
        try:
            print(f"\nTesting login for: {url}")
            print(f"Using delay of {self.config['delay_seconds']} seconds between actions")
            
            # Navigate to the URL
            self.driver.get(url)
            time.sleep(self.config['delay_seconds'])  # Configurable delay
            
            # Wait for username field to be present (adjust selector based on actual page)
            print("Looking for username field...")
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            time.sleep(self.config['delay_seconds'])  # Configurable delay
            
            print("Looking for password field...")
            password_field = self.driver.find_element(By.NAME, "password")
            time.sleep(self.config['delay_seconds'])  # Configurable delay
            
            # Fill in the credentials
            print("Filling in credentials...")
            username_field.send_keys(self.username)
            time.sleep(self.config['delay_seconds'])  # Configurable delay
            password_field.send_keys(self.password)
            time.sleep(self.config['delay_seconds'])  # Configurable delay
            
            # Find and click login button (adjust selector based on actual page)
            print("Attempting to click login button...")
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            time.sleep(self.config['delay_seconds'])  # Configurable delay
            
            # Check for error messages first (common error message selectors)
            error_selectors = [
                # Modal dialogs
                (By.CLASS_NAME, "modal-body"),
                (By.CLASS_NAME, "modal-content"),
                (By.CLASS_NAME, "modal-header"),
                (By.CLASS_NAME, "modal-dialog"),
                # Alert/Error messages
                (By.CLASS_NAME, "alert"),
                (By.CLASS_NAME, "error-message"),
                (By.CLASS_NAME, "alert-danger"),
                (By.CLASS_NAME, "alert-error"),
                (By.CLASS_NAME, "error"),
                (By.CLASS_NAME, "validation-error"),
                # Common error containers
                (By.CLASS_NAME, "error-container"),
                (By.CLASS_NAME, "message-error"),
                (By.CLASS_NAME, "error-summary"),
                # Error text elements
                (By.CLASS_NAME, "error-text"),
                (By.CLASS_NAME, "help-block"),
                (By.CLASS_NAME, "invalid-feedback"),
                # Specific error messages
                (By.XPATH, "//*[contains(@class, 'error')]"),
                (By.XPATH, "//*[contains(@class, 'alert')]"),
                (By.XPATH, "//*[contains(@class, 'modal')]"),
                # Dialog boxes
                (By.XPATH, "//div[@role='dialog']"),
                (By.XPATH, "//div[@role='alert']"),
                # Common modal title locations
                (By.XPATH, "//h4[contains(@class, 'modal-title')]"),
                (By.XPATH, "//h5[contains(@class, 'modal-title')]"),
                # Generic error messages
                (By.XPATH, "//*[contains(text(), 'error')]"),
                (By.XPATH, "//*[contains(text(), 'Error')]"),
                (By.XPATH, "//*[contains(text(), 'failed')]"),
                (By.XPATH, "//*[contains(text(), 'Failed')]"),
                (By.XPATH, "//*[contains(text(), 'invalid')]"),
                (By.XPATH, "//*[contains(text(), 'Invalid')]")
            ]
            
            # Check each error selector
            for selector in error_selectors:
                try:
                    error_elements = self.driver.find_elements(*selector)
                    for error_element in error_elements:
                        try:
                            if error_element.is_displayed():
                                error_text = error_element.text.strip()
                                if error_text and any(keyword in error_text.lower() for keyword in ['error', 'invalid', 'failed', 'incorrect']):
                                    print(f"Found error message: {error_text}")
                                    return f"Login Failed - {error_text}"
                        except:
                            continue
                except:
                    continue
            
            # If no error messages found, check for success indicators
            try:
                # Wait for successful login indicator (adjust based on your system)
                print("Checking if login was successful...")
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "dashboard"))
                )
                return "Success"
            except TimeoutException:
                # Check for other success indicators if dashboard not found
                success_selectors = [
                    (By.CLASS_NAME, "welcome-message"),
                    (By.CLASS_NAME, "user-profile"),
                    (By.CLASS_NAME, "logged-in"),
                    (By.CLASS_NAME, "dashboard-container"),
                    (By.CLASS_NAME, "user-dashboard"),
                    (By.XPATH, "//*[contains(@class, 'dashboard')]"),
                    (By.XPATH, "//*[contains(@class, 'welcome')]"),
                    (By.XPATH, "//div[contains(text(), 'Welcome')]"),
                    # Add more success indicators as needed
                ]
                
                for selector in success_selectors:
                    try:
                        WebDriverWait(self.driver, 3).until(
                            EC.presence_of_element_located(selector)
                        )
                        return "Success"
                    except TimeoutException:
                        continue
            
                # Take screenshot if no success indicators found
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = f"login_error_{timestamp}.png"
                self.driver.save_screenshot(screenshot_path)
                print(f"Saved error screenshot to: {screenshot_path}")
                
                return "Login Failed - Could not verify successful login"
            
        except TimeoutException:
            return "Timeout - Site might be down or too slow"
        except WebDriverException as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    def check_all_urls(self, urls):
        """Check login for multiple URLs and generate a report"""
        results = {}
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for url in urls:
            results[url] = self.check_login(url)
            time.sleep(5)  # Wait 5 seconds between checking different URLs
            
        # Generate report
        print("\n=== Login Check Report ===")
        print(f"Timestamp: {timestamp}\n")
        for url, status in results.items():
            print(f"URL: {url}")
            print(f"Status: {status}\n")
            
        self.driver.quit()

def main():
    checker = LoginChecker()
    
    # Use URLs from config
    for url in checker.config['urls']:
        checker.check_login(url)
    
    checker.driver.quit()

if __name__ == "__main__":
    main()
