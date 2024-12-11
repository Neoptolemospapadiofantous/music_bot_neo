import os
import time
import random
import logging
from seleniumwire import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

# Configure logging
logger = logging.getLogger(__name__)

class BrowserActions:
    def __init__(self):
        self.screenshots_dir = "screenshots"
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)

    def save_screenshot(self, driver, action_name):
	    """
	    Save a screenshot for the given action with unique filenames.
	    Ensures no stale state by capturing new screenshots every time.
	    """
	    try:
	        # Ensure unique filenames by appending a timestamp
	        timestamp = time.strftime("%Y%m%d_%H%M%S")
	        filepath = os.path.join(self.screenshots_dir, f"{action_name}_{timestamp}.png")

	        # Explicitly refresh the page to avoid stale state if needed
	        driver.execute_script("void(0);")  # No-op to ensure the page context is current

	        driver.save_screenshot(filepath)
	        logger.info(f"Screenshot saved: {filepath}")
	    except Exception as e:
	        logger.error(f"Failed to save screenshot for {action_name}: {e}")

    def _type_like_human(self, element, text, delay_range=(0.1, 0.3)):
        """Simulate human-like typing with random delays."""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(*delay_range))

    def _wait_for_element(self, driver, by, value, timeout=20):
        """Wait for an element to be present and clickable."""
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except TimeoutException:
            logger.error(f"Element not found: {value}")
            return None

    def _click_element(self, driver, locator):
        """Click an element safely with delays to simulate human actions."""
        try:
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(locator)
            )
            time.sleep(random.uniform(0.5, 1.5))  # Pause before clicking
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            element.click()
        except ElementClickInterceptedException:
            logger.warning("Element click intercepted. Retrying...")
            from selenium.webdriver.common.action_chains import ActionChains
            ActionChains(driver).move_to_element(element).click().perform()

    def _handle_overlays(self, driver):
	    """Handle and close any overlays or pop-ups that might obstruct interactions."""
	    try:
	        logger.info("Checking for overlays...")
	        if self._handle_dynamic_overlay(driver):
	            logger.info("Overlay handled successfully.")
	        else:
	            logger.info("No overlays to handle.")
	    except Exception as e:
	        logger.error(f"Failed to handle overlays: {e}")
	        self.save_screenshot(driver, "error_handling_overlays")
	        raise

    def _handle_dynamic_overlay(self, driver):
        """
        Detect and close any overlay or pop-up that might be obstructing element interactions.

        Returns:
            bool: True if an overlay was handled, False otherwise.
        """
        try:
            # Define a list of potential close button XPaths for common overlays
            potential_close_buttons = [
                "//button[text()='Close']",
                "//button[text()='No thanks']",
                "//button[contains(@aria-label, 'Close')]",
                "//div[@role='dialog']//button[contains(text(), 'Close')]",
                "//div[contains(@class, 'overlay')]//button",
                "//div[contains(@class, 'modal')]//button",
                "//button[contains(@class, 'close')]",
                "//button[contains(text(), 'Dismiss')]",
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'Agree')]",
                "//button[contains(text(), 'Got it')]",
            ]

            for btn_xpath in potential_close_buttons:
                try:
                    close_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, btn_xpath))
                    )
                    close_button.click()
                    logger.info(f"Closed overlay using button: {btn_xpath}")
                    time.sleep(random.uniform(1, 2))  # Wait briefly for the overlay to disappear
                    return True
                except TimeoutException:
                    continue  # Try the next close button
            logger.info("No known overlay close buttons found.")
            return False
        except Exception as e:
            logger.error(f"Failed to handle dynamic overlay: {e}")
            self.save_screenshot(driver, "overlay_error")
            return False

    def initialize_webdriver(self, proxy):
	    """Initialize the WebDriver with the provided proxy settings and a custom User-Agent."""
	    try:
	        logger.info("Initializing WebDriver with proxy...")

	        # Extract proxy details
	        proxy_address = proxy['proxy_address']
	        proxy_port = proxy['port']
	        proxy_username = proxy.get('username', None)
	        proxy_password = proxy.get('password', None)

	        # Configure Firefox options
	        options = FirefoxOptions()
	        options.add_argument('--headless')  # Enable headless mode

	        # Set a modern User-Agent
	        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
	        options.set_preference("general.useragent.override", user_agent)

	        # Selenium Wire proxy configuration
	        seleniumwire_options = {
	            'proxy': {
	                'http': f"http://{proxy_username}:{proxy_password}@{proxy_address}:{proxy_port}",
	                'https': f"https://{proxy_username}:{proxy_password}@{proxy_address}:{proxy_port}",
	                'no_proxy': 'localhost,127.0.0.1'  # Bypass proxy for localhost
	            }
	        }

	        driver = webdriver.Firefox(options=options, seleniumwire_options=seleniumwire_options)
	        driver.set_page_load_timeout(60)  # Set timeout for navigation
	        logger.info("WebDriver initialized successfully with User-Agent.")
	        return driver

	    except Exception as e:
	        logger.error(f"Failed to initialize WebDriver: {e}")
	        raise

    def navigate_to_google(self, driver):
	    """Navigate to Google and log page content."""
	    logger.info("Navigating to Google homepage...")
	    try:
	        driver.get("https://www.google.com")

	        # Wait for the page to fully load
	        logger.info("Waiting for the page to load completely...")
	        WebDriverWait(driver, 20).until(
	            lambda d: d.execute_script("return document.readyState") == "complete"
	        )
	        logger.info("Page fully loaded.")

	        # Handle overlays
	        self._handle_overlays(driver)

	        # Save a screenshot of the Google homepage
	        self.save_screenshot(driver, "google_homepage")
	        logger.info("Successfully loaded Google homepage.")
	    except Exception as e:
	        logger.error(f"Failed to navigate to Google: {e}")
	        self.save_screenshot(driver, "error_google_navigation")
	        raise

    def accept_cookies(self, driver):
	    """Handle cookie acceptance banner."""
	    try:
	        logger.info("Attempting to accept cookies...")
	        cookie_locators = [
	            (By.XPATH, "//button[contains(text(), 'Accept All')]"),
	            (By.XPATH, "//button[contains(text(), 'I agree')]"),
	        ]

	        for locator in cookie_locators:
	            try:
	                accept_button = WebDriverWait(driver, 5).until(
	                    EC.element_to_be_clickable(locator)
	                )
	                self._click_element(driver, locator)
	                logger.info("Cookies accepted successfully.")
	                self.save_screenshot(driver, "after_accepting_cookies")
	                return
	            except TimeoutException:
	                continue  # Try the next locator
	        logger.info("No cookie consent banner found.")
	    except Exception as e:
	        logger.error(f"Failed to accept cookies: {e}")
	        self.save_screenshot(driver, "error_accepting_cookies")
	        raise

    def click_sign_in_button(self, driver):
	    """Click on the Sign In button."""
	    logger.info("Clicking on the Sign In button...")
	    try:
	        self.save_screenshot(driver, "before_clicking_sign_in")
	        logger.info(f"Current page title: {driver.title}")
	        logger.info(f"Current page URL: {driver.current_url}")

	        # Wait for the page to fully load
	        logger.info("Waiting for the page to load completely...")
	        WebDriverWait(driver, 20).until(
	            lambda d: d.execute_script("return document.readyState") == "complete"
	        )
	        logger.info("Page fully loaded.")

	        # Handle overlays
	        self._handle_dynamic_overlay(driver)

	        # Refined XPath to target the "Sign In" button
	        sign_in_locator = (By.XPATH, "//a[@aria-label='Sign in' and @href]")
	        logger.info("Waiting for the Sign In button to be clickable...")
	        sign_in_button = WebDriverWait(driver, 15).until(
	            EC.element_to_be_clickable(sign_in_locator)
	        )
	        sign_in_button.click()
	        logger.info("Clicked on the Sign In button.")
	        self.save_screenshot(driver, "after_clicking_sign_in")

	    except TimeoutException:
	        logger.error("Sign In button was not found or clickable within the timeout.")
	        self.save_screenshot(driver, "error_sign_in_button_timeout")
	        logger.info("Page source after timeout:")
	        logger.info(driver.page_source[:500])  # Log the first 500 characters of the page source
	        raise
	    except Exception as e:
	        logger.error(f"Error clicking Sign In button: {e}")
	        self.save_screenshot(driver, "error_clicking_sign_in")
	        raise

    def perform_login(self, driver, email, password):
        """Perform the login process by entering email and password."""
        try:
            logger.info("Performing login...")

            # Step 1: Enter Email
            logger.info("Entering email...")
            email_input_locator = (By.ID, "identifierId")
            email_input = self._wait_for_element(driver, *email_input_locator)
            if email_input:
                email_input.clear()
                self._type_like_human(email_input, email)
                email_input.send_keys(Keys.RETURN)
                self.save_screenshot(driver, "after_email_submission")
                logger.info("Email submitted. Waiting for password field...")
                time.sleep(3)  # Wait briefly to ensure page loads

            # Step 2: Enter Password
            logger.info("Entering password...")
            password_locators = [
                (By.NAME, "password"),
                (By.XPATH, "//input[@type='password']"),
                (By.CSS_SELECTOR, "input[type='password']"),
            ]
            password_input = None
            for locator in password_locators:
                try:
                    password_input = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable(locator)
                    )
                    break  # Stop if the input is found
                except TimeoutException:
                    continue
            if not password_input:
                raise Exception("Password input field not found.")

            password_input.clear()
            self._type_like_human(password_input, password)
            password_input.send_keys(Keys.RETURN)
            self.save_screenshot(driver, "after_password_submission")
            logger.info("Password submitted. Login process complete.")

        except Exception as e:
            logger.error(f"Login failed: {e}")
            self.save_screenshot(driver, "error_during_login")
            raise
