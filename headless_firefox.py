import logging
from proxy_manager import get_valid_proxy
from browser_actions import initialize_webdriver, navigate_to_google, accept_cookies

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        # Step 1: Fetch a valid proxy
        logger.info("Fetching proxy...")
        proxy = get_valid_proxy()
        logger.info(f"Selected valid proxy: {proxy}")

        # Step 2: Initialize WebDriver with proxy
        logger.info("Initializing WebDriver...")
        driver = initialize_webdriver(proxy)

        # Step 3: Navigate to Google homepage
        logger.info("Navigating to Google homepage...")
        navigate_to_google(driver)

        # Step 4: Accept cookies if present
        logger.info("Accepting cookies...")
        accept_cookies(driver)

        # (Optional) Add further actions like login here...

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        # Ensure browser is closed
        if 'driver' in locals():
            driver.quit()
            logger.info("WebDriver closed.")

if __name__ == "__main__":
    main()
