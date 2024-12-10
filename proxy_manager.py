import logging
import random
import subprocess  # Import subprocess for Popen
from subprocess import Popen, PIPE  # Ensure Popen and PIPE are available
import requests

# Set up logging
logger = logging.getLogger(__name__)

WEBSHARE_API_KEY = "p71v0m82iwngh6lj9uc9n3t9w7kpyud25jhuukdr"
WEBSHARE_API_URL = "https://proxy.webshare.io/api/v2/proxy/list/"

def fetch_proxies(country_code=None):
    """Fetches a list of proxies from Webshare."""
    params = {
        "mode": "direct",
        "page": 1,
        "page_size": 25,
    }
    if country_code:
        params["country_code__in"] = country_code

    headers = {"Authorization": f"Token {WEBSHARE_API_KEY}"}
    logger.info(f"Requesting Webshare proxies with {params}")

    response = requests.get(WEBSHARE_API_URL, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()
    return data.get("results", [])

def validate_proxy(proxy_string):
    """Validates a proxy by attempting a connection to Google using curl."""
    logger.info(f"Validating proxy using curl: {proxy_string}...")
    curl_command = [
        "curl",
        "-x", f"http://{proxy_string}",
        "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "https://www.google.com",
    ]
    process = Popen(curl_command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    if process.returncode == 0:
        http_status = stdout.decode().strip()
        logger.info(f"HTTP Status Code: {http_status}")
        return http_status == "200"
    else:
        logger.error(f"Curl failed: {stderr.decode().strip()}")
        return False

def get_valid_proxy(country_code=None):
    """Fetch and validate proxies, returning the first valid one."""
    logger.info("Fetching proxy list...")
    proxies = fetch_proxies(country_code=country_code)
    if not proxies:
        raise ValueError("No proxies available.")

    for proxy in proxies:
        proxy_string = f"{proxy['username']}:{proxy['password']}@{proxy['proxy_address']}:{proxy['port']}"
        logger.info(f"Testing proxy: {proxy_string}")
        if validate_proxy(proxy_string):
            logger.info(f"Valid proxy found: {proxy_string}")
            return proxy  # Return the full proxy dictionary

    raise ValueError("No valid proxies found.")
