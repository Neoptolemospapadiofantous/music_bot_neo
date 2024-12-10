from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
import logging

# Configure logging
logger = logging.getLogger(__name__)

import logging
from selenium import webdriver
from selenium.webdriver import FirefoxOptions

logger = logging.getLogger(__name__)

def initialize_webdriver(proxy):
    """
    Initialize the WebDriver with the provided proxy settings.

    Parameters:
        proxy (dict): Proxy configuration in JSON format.

    Returns:
        WebDriver: Configured WebDriver instance.
    """
    try:
        logger.info("Initializing WebDriver with proxy...")

        # Extract proxy information
        proxy_address = proxy['proxy_address']
        proxy_port = proxy['port']
        proxy_username = proxy['username']
        proxy_password = proxy['password']

        # Configure proxy settings
        options = FirefoxOptions()
        options.add_argument('--headless')  # Enable headless mode
        options.set_preference("network.proxy.type", 1)  # Manual proxy configuration
        options.set_preference("network.proxy.http", proxy_address)
        options.set_preference("network.proxy.http_port", int(proxy_port))
        options.set_preference("network.proxy.ssl", proxy_address)
        options.set_preference("network.proxy.ssl_port", int(proxy_port))
        options.set_preference("network.proxy.socks_remote_dns", True)  # Ensure DNS resolution uses proxy

        # Set authentication for proxies requiring username and password
        if proxy_username and proxy_password:
            logger.info("Setting proxy authentication.")
            options.set_preference("network.proxy.autoconfig_url", "")
            options.set_preference("network.proxy.autoconfig_url.include_host", False)
            options.set_preference("network.proxy.autoconfig_url.username", proxy_username)
            options.set_preference("network.proxy.autoconfig_url.password", proxy_password)

        logger.info(f"HTTP Proxy: {proxy_address}")
        logger.info(f"Port: {proxy_port}")

        # Initialize WebDriver
        driver = webdriver.Firefox(options=options)
        logger.info("WebDriver initialized successfully.")
        return driver

    except Exception as e:
        logger.error(f"Failed to initialize WebDriver: {e}")
        raise

def navigate_to_google(driver):
    """Navigate to Google and log page content."""
    logger.info("Navigating to Google homepage...")
    try:
        driver.get("https://www.google.com")
        page_source = driver.page_source
        logger.info("Successfully loaded Google homepage.")
        logger.debug(f"Page content: {page_source[:500]}...")  # Log the first 500 characters
    except Exception as e:
        logger.error(f"Failed to navigate to Google: {e}")
        raise

def accept_cookies(driver):
    """Accept cookies on the Google homepage."""
    try:
        logger.info("Attempting to accept cookies...")
        accept_button_locator = (By.XPATH, "//button[contains(text(), 'I agree') or contains(text(), 'Accept all')]")
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(accept_button_locator)).click()
        logger.info("Cookies accepted successfully.")
    except Exception as e:
        logger.error(f"Failed to accept cookies: {e}")
        raise
