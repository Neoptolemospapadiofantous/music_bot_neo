import logging
import os
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

def save_screenshot(driver, filename):
    """
    Utility function to take a screenshot and log the action.
    """
    try:
        os.makedirs("screenshots", exist_ok=True)
        filepath = os.path.join("screenshots", filename)
        driver.save_screenshot(filepath)
        logger.info(f"Screenshot saved: {filepath}")
    except Exception as e:
        logger.error(f"Failed to save screenshot: {e}")

def initialize_webdriver(proxy):
    """
    Initialize the WebDriver with Selenium Wire for authenticated proxy.
    proxy is a dictionary containing 'username', 'password', 'proxy_address', and 'port'.
    """
    try:
        logger.info("Initializing WebDriver with proxy...")
        proxy_address = proxy['proxy_address']
        proxy_port = proxy['port']
        proxy_user = proxy['username']
        proxy_pass = proxy['password']

        # Construct the authenticated proxy URL
        auth_proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_address}:{proxy_port}"

        seleniumwire_options = {
            'proxy': {
                'http': auth_proxy_url,
                'https': auth_proxy_url,
                'no_proxy': 'localhost,127.0.0.1'
            }
        }

        firefox_options = FirefoxOptions()
        firefox_options.add_argument('--headless')

        driver = webdriver.Firefox(seleniumwire_options=seleniumwire_options, options=firefox_options)
        driver.set_page_load_timeout(60)
        logger.info("WebDriver initialized successfully with authenticated proxy.")
        return driver

    except Exception as e:
        logger.error(f"Failed to initialize WebDriver with auth proxy: {e}")
        raise

def navigate_to_google(driver):
    """
    Navigate to the Google homepage and capture logs.
    """
    try:
        url = "https://www.google.com"
        logger.info(f"Navigating to {url}...")
        driver.get(url)

        # Log current URL and page title
        current_url = driver.current_url
        logger.info(f"Current URL after navigation: {current_url}")
        page_title = driver.title
        logger.info(f"Page title: {page_title}")

        # Save page source for debugging
        os.makedirs("logs", exist_ok=True)
        page_source_path = "logs/google_homepage.html"
        with open(page_source_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        logger.info(f"Page source saved: {page_source_path}")

        # Take a screenshot
        save_screenshot(driver, "google_homepage.png")

        # Check for CAPTCHA
        if "captcha" in driver.page_source.lower():
            logger.warning("CAPTCHA detected on the Google homepage.")
        else:
            logger.info("Google homepage loaded successfully without CAPTCHA.")

    except Exception as e:
        logger.error(f"Failed to navigate to Google: {e}")
        save_screenshot(driver, "google_navigation_error.png")
        # Save page source on error
        os.makedirs("logs", exist_ok=True)
        error_page_source_path = "logs/navigation_error.html"
        with open(error_page_source_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        logger.info(f"Error page source saved: {error_page_source_path}")
        raise

def accept_cookies(driver):
    """
    Accept cookies on the Google homepage.
    """
    try:
        logger.info("Attempting to accept cookies...")
        cookie_button_locator = (By.XPATH, "//button[contains(text(), 'I agree') or contains(text(), 'Accept all')]")
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(cookie_button_locator)).click()
        logger.info("Cookies accepted successfully.")
        save_screenshot(driver, "after_accepting_cookies.png")
    except Exception as e:
        logger.error(f"Failed to accept cookies: {e}")
        save_screenshot(driver, "error_accepting_cookies.png")
        raise
