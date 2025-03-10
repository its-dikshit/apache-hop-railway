import os
import time
import json
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

# Extract common configurations
LOGIN_URL = config["source_login_url"]["login_url"]
USERNAME = config["source_admin_credentials"]["username"]
PASSWORD = config["source_admin_credentials"]["password"]

# Extract global download directory
SOURCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), config["download_dir"]["source_dir"]))

# Extract specific parameters for Source_Areas
download_params = config["source_downloads"]["source_areas"]
REPORT_URL = download_params["report_url"]
FILE_PREFIX = download_params["file_prefix"]
DOWNLOAD_DIR = SOURCE_DIR  # Use the common download directory


def ensure_directory_exists(path):
    """Ensure the specified directory exists."""
    if not os.path.exists(path):
        os.makedirs(path)


def initialize_webdriver(download_dir):
    """Set up and return the Chrome WebDriver with required options."""
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "directory_upgrade": True
    }
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def clean_directory(download_dir, file_prefix):
    """Delete any existing files matching the specified file prefix before download."""
    for file_name in os.listdir(download_dir):
        if file_name.startswith(file_prefix) and not file_name.endswith('.crdownload'):
            file_path = os.path.join(download_dir, file_name)
            try:
                os.unlink(file_path)
                print(f"Deleted old file: {file_path}")
            except Exception as e:
                print(f"Failed to delete {file_name}: {e}")


def login_and_navigate(driver, login_url, username, password, report_url, download_dir, file_prefix):
    """Log in to Bizom and navigate to the specified report page."""
    driver.get(login_url)
    driver.maximize_window()
    wait = WebDriverWait(driver, 20)

    # Enter credentials
    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login").click()

    # Clean directory after login
    clean_directory(download_dir, file_prefix)

    # Wait for login to process and navigate to the report page
    time.sleep(3)
    driver.get(report_url)


def wait_for_download(download_dir, initial_files, timeout=60):
    """Wait for a new file to appear in the download directory and ensure it is fully downloaded."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        current_files = set(os.listdir(download_dir))
        new_files = current_files - initial_files
        if new_files:
            latest_file = max(new_files, key=lambda f: os.path.getctime(os.path.join(download_dir, f)))
            file_path = os.path.join(download_dir, latest_file)
            if not file_path.endswith('.crdownload') and time.time() - os.path.getctime(file_path) > 2:
                return file_path
        time.sleep(1)
    raise TimeoutError("Download did not complete in time!")


def download_report(driver, download_dir, file_prefix):
    """Trigger the report download and rename the file once completed."""
    wait = WebDriverWait(driver, 20)
    initial_files = set(os.listdir(download_dir))

    # Click update and download the report
    wait.until(EC.presence_of_element_located((By.ID, "reportsUpdateButton"))).click()
    wait.until(EC.presence_of_element_located((By.ID, "option-dropdown"))).click()
    wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@onclick, 'downloadReport(4)')]"))).click()

    # Wait for the file to download completely
    latest_file = wait_for_download(download_dir, initial_files)
    file_extension = os.path.splitext(latest_file)[1]
    renamed_file = os.path.join(download_dir, f"{file_prefix}{file_extension}")

    try:
        os.rename(latest_file, renamed_file)
        print(f"Report downloaded and renamed to: {renamed_file}")
    except Exception as e:
        print(f"Failed to rename file: {e}")


def run():
    """Execute the full download process without using a class."""
    ensure_directory_exists(DOWNLOAD_DIR)
    driver = initialize_webdriver(DOWNLOAD_DIR)
    
    try:
        login_and_navigate(driver, LOGIN_URL, USERNAME, PASSWORD, REPORT_URL, DOWNLOAD_DIR, FILE_PREFIX)
        download_report(driver, DOWNLOAD_DIR, FILE_PREFIX)
    finally:
        driver.quit()
        print("Process completed successfully.")


if __name__ == "__main__":
    run()
