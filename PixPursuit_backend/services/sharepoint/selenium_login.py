"""
services/sharepoint/selenium_login.py

Provides functionality to automate browser actions for logging into a SharePoint site
using Selenium WebDriver. It handles web navigation, input of credentials, and extraction
of session cookies for subsequent authenticated requests.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from config.logging_config import setup_logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.constants import (
    USER_AGENT_ARG, SP_AUTH_COOKIES, HEADLESS_ARG, DISABLE_GPU_ARG, LOGIN_FIELD,
    USERNAME_FIELD, PASSWORD_FIELD, SUBMIT_BUTTON_FIELD, ACCEPT_BUTTON_FIELD,
    NO_SANDBOX_ARG, DISABLE_DEV_SHM_USAGE_ARG, REMOTE_DEBUGGING_PORT_ARG,
    DISABLE_SOFTWARE_RASTERIZER_ARG, DISABLE_EXTENSIONS_ARG, HUB_URL)

logger = setup_logging(__name__)


def setup_driver() -> webdriver.Chrome:
    """
    Sets up the Selenium WebDriver with necessary options.

    :return: A Selenium WebDriver instance for Chrome.
    """
    chrome_options = Options()
    chrome_options.add_argument(HEADLESS_ARG)
    chrome_options.add_argument(DISABLE_GPU_ARG)
    chrome_options.add_argument(USER_AGENT_ARG)
    chrome_options.add_argument(NO_SANDBOX_ARG)
    chrome_options.add_argument(DISABLE_DEV_SHM_USAGE_ARG)
    chrome_options.add_argument(REMOTE_DEBUGGING_PORT_ARG)
    chrome_options.add_argument(DISABLE_SOFTWARE_RASTERIZER_ARG)
    chrome_options.add_argument(DISABLE_EXTENSIONS_ARG)
    try:
        driver = webdriver.Remote(
            command_executor=HUB_URL,
            options=chrome_options
        )
        return driver
    except Exception as e:
        logger.error(f"Failed to set up ChromeDriver: {e}")
        raise e


def perform_login(driver: webdriver.Chrome, url: str, username: str, password: str):
    """
    Performs login action on the specified URL using provided credentials.

    :param driver: The Selenium WebDriver instance.
    :param url: The URL to perform login action.
    :param username: The username for login.
    :param password: The password for login.
    """
    wait = WebDriverWait(driver, 10)
    driver.get(url)

    email_field = wait.until(EC.visibility_of_element_located((By.NAME, LOGIN_FIELD)))
    email_field.send_keys(username)
    wait.until(EC.element_to_be_clickable((By.ID, ACCEPT_BUTTON_FIELD))).click()

    username_field = wait.until(EC.visibility_of_element_located((By.NAME, USERNAME_FIELD)))
    username_field.clear()
    username_field.send_keys(username)

    password_field = wait.until(EC.visibility_of_element_located((By.NAME, PASSWORD_FIELD)))
    password_field.send_keys(password)
    wait.until(EC.element_to_be_clickable((By.ID, SUBMIT_BUTTON_FIELD))).click()

    wait.until(EC.element_to_be_clickable((By.ID, ACCEPT_BUTTON_FIELD))).click()


def extract_cookies(driver: webdriver.Chrome) -> list[dict[str, str]]:
    """
    Extracts cookies from the current session of the driver.

    :param driver: The Selenium WebDriver instance.
    :return: A list of cookies.
    """
    return driver.get_cookies()


def selenium_login(sharepoint_url: str, username: str, password: str) -> list[dict[str, str]] or None:
    """
    Attempts to log in to SharePoint using Selenium and returns session cookies.

    :param sharepoint_url: The URL of the SharePoint site to log into.
    :param username: The username for login.
    :param password: The password for login.
    :return: A list of cookie dictionaries if login is successful, otherwise None.
    """
    driver = None
    for attempt in range(5):
        try:
            driver = setup_driver()
            perform_login(driver, sharepoint_url, username, password)
            cookies = extract_cookies(driver)
            driver.quit()
            return cookies
        except Exception as e:
            logger.error(f"Error during login: {e}")
            if attempt == 4:
                return None
        finally:
            if driver:
                driver.quit()


def get_cookies(url: str, username: str, password: str) -> dict[str, str] or None:
    """
    Retrieves authentication cookies for a given SharePoint site by performing a login.

    :param url: The URL of the SharePoint site to retrieve cookies for.
    :param username: The username for login.
    :param password: The password for login.
    :return: A dictionary containing the 'FedAuth' and 'rtFa' cookies if successful, otherwise None.
    """
    cookies = selenium_login(url, username, password)
    if cookies is None:
        return None

    auth_cookies = {cookie['name']: cookie['value'] for cookie in cookies if cookie['name'] in SP_AUTH_COOKIES}
    return auth_cookies if len(auth_cookies) == 2 else None
