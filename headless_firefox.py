import logging
from proxy_manager import get_valid_proxy
from browser_actions import BrowserActions

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        # Initialize BrowserActions class
        actions = BrowserActions()

        # Step 1: Fetch a valid proxy
        logger.info("Fetching proxy...")
        proxy = get_valid_proxy()
        logger.info(f"Selected valid proxy: {proxy}")

        # Step 2: Initialize WebDriver with the proxy
        logger.info("Initializing WebDriver...")
        driver = actions.initialize_webdriver(proxy)

        # Step 3: Navigate to Google homepage
        logger.info("Navigating to Google homepage...")
        actions.navigate_to_google(driver)

        # Step 4: Accept cookies if present
        logger.info("Accepting cookies...")
        actions.accept_cookies(driver)

        # Step 5: Click on the Sign-In button
        logger.info("Clicking on the Sign-In button...")
        actions.click_sign_in_button(driver)

        # Step 6: Perform login
        email = "neoptolemos8@gmail.com"  # Replace with your email
        password = "Tjwtp2005!"       # Replace with your password
        logger.info("Performing login...")
        actions.perform_login(driver, email, password)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        # Ensure browser is closed
        if 'driver' in locals():
            driver.quit()
            logger.info("WebDriver closed.")

if __name__ == "__main__":
    main()
