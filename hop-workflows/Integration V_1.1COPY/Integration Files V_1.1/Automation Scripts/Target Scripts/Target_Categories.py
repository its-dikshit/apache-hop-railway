import os
import time
import json
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# === Step 1: Parse Command-Line Argument for source_name ===
parser = argparse.ArgumentParser(description="Run script with a dynamic source_name.")
parser.add_argument("source_name", type=str, help="Brand folder name (e.g., 'Brand A')")
args = parser.parse_args()

# === Step 2: Load JSON Configuration from Dynamic Path ===
script_dir = os.path.dirname(os.path.abspath(__file__))  # Get current script directory
config_path = os.path.abspath(os.path.join(script_dir, "..", "..", args.source_name, "config.json"))  # Set dynamic config path

if not os.path.exists(config_path):
    print(f"Error: Config file not found at {config_path}")
    exit(1)

with open(config_path, "r") as file:
    config = json.load(file)

# Extract Target Login & Credentials
LOGIN_URL = config["target_login_url"]["login_url"]
USERNAME = config["target_credentials"]["username"]
PASSWORD = config["target_credentials"]["password"]

# Extract Target Download Parameters
download_params = config["target_downloads"]["target_categories"]
CATEGORIES_URL = download_params["categories_url"]
DOWNLOAD_BUTTON_ID = download_params["download_button_id"]
FILE_PREFIX = download_params["file_prefix"]

# Extract Target Directory
TARGET_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), config["download_dir"]["target_dir"]))


def ensure_directory_exists(path: str):
    """Ensure the specified directory exists."""
    if not os.path.exists(path):
        os.makedirs(path)


def delete_existing_files(target_dir: str, file_prefix: str):
    """Delete any existing files that match the prefix in the target directory."""
    for file in os.listdir(target_dir):
        if file.startswith(file_prefix):
            file_path = os.path.join(target_dir, file)
            os.remove(file_path)
            print(f"Deleted existing file: {file_path}")


def wait_for_download(target_dir: str, download_start_time: float, timeout: int = 60) -> str:
    """Wait for a file to be downloaded in the target directory after the given timestamp."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        for file in os.listdir(target_dir):
            file_path = os.path.join(target_dir, file)
            if os.path.getctime(file_path) > download_start_time:
                return file_path
        time.sleep(1)
    raise TimeoutError(f"Download timed out after {timeout} seconds.")


def rename_downloaded_file(downloaded_file_path: str, new_name: str):
    """Rename the downloaded file to the specified name while keeping the extension unchanged."""
    target_dir = os.path.dirname(downloaded_file_path)
    file_extension = os.path.splitext(downloaded_file_path)[1]  # Keep original extension
    target_file_path = os.path.join(target_dir, f"{new_name}{file_extension}")

    os.rename(downloaded_file_path, target_file_path)
    print(f"Renamed file {downloaded_file_path} to {target_file_path}")


def login_to_website(driver: webdriver.Chrome, wait: WebDriverWait):
    """Perform login operation on the website."""
    driver.get(LOGIN_URL)

    username_field = wait.until(EC.presence_of_element_located((By.ID, "UserUsername")))
    username_field.send_keys(USERNAME)

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(PASSWORD)

    login_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
    login_button.click()
    print("Login successful.")


def navigate_to_categories(driver: webdriver.Chrome, wait: WebDriverWait) -> float:
    """Navigate to the categories section and initiate download."""
    wait.until(EC.url_contains("/users/dashboard"))
    driver.get(CATEGORIES_URL)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    download_button = wait.until(EC.element_to_be_clickable((By.ID, DOWNLOAD_BUTTON_ID)))
    download_start_time = time.time()
    download_button.click()
    print("Download initiated.")
    return download_start_time


def configure_webdriver() -> tuple[webdriver.Chrome, WebDriverWait]:
    """Set up and configure the WebDriver."""
    chrome_options = Options()

    prefs = {
        "download.default_directory": TARGET_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 20)

    return driver, wait


def main():
    """Main function to automate login, navigation, and file download process."""
    ensure_directory_exists(TARGET_DIR)

    driver, wait = configure_webdriver()

    try:
        delete_existing_files(TARGET_DIR, FILE_PREFIX)
        login_to_website(driver, wait)
        download_start_time = navigate_to_categories(driver, wait)

        downloaded_file_path = wait_for_download(TARGET_DIR, download_start_time)
        rename_downloaded_file(downloaded_file_path, FILE_PREFIX)

        print(f"Process completed successfully. File saved as: {FILE_PREFIX}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
