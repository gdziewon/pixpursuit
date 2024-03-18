from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from config.logging_config import setup_logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = setup_logging(__name__)


def selenium_login(sharepoint_url, username, password):
    for attempt in range(5):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
            chrome_options.add_argument('user-agent={0}'.format(user_agent))

            driver = webdriver.Chrome(options=chrome_options)
            wait = WebDriverWait(driver, 10)

            driver.get(sharepoint_url)

            email_field = wait.until(EC.visibility_of_element_located((By.NAME, "loginfmt")))
            email_field.send_keys(username)

            next_button = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
            next_button.click()

            username_field = wait.until(EC.visibility_of_element_located((By.NAME, "UserName")))
            username_field.clear()
            username_field.send_keys(username)

            password_field = wait.until(EC.visibility_of_element_located((By.NAME, "Password")))
            password_field.send_keys(password)

            login_button = wait.until(EC.element_to_be_clickable((By.ID, "submitButton")))
            login_button.click()

            yes_button = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
            yes_button.click()

            cookies = driver.get_cookies()

            driver.quit()
            return cookies
        except Exception as e:
            logger.error(f"Error during login: {e}")
            if attempt == 4:
                return None


def get_cookies(url: str, username: str, password: str) -> dict[str, str] or None:
    cookies = selenium_login(url, username, password)
    auth_cookies = {}

    for cookie in cookies:
        if cookie['name'] == 'FedAuth':
            auth_cookies['FedAuth'] = cookie['value']
        elif cookie['name'] == 'rtFa':
            auth_cookies['rtFa'] = cookie['value']
    if len(auth_cookies) == 2:
        return auth_cookies
    else:
        return None
