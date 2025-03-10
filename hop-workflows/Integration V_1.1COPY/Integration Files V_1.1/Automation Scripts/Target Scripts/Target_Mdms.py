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

# === Step 3: Extract Configurations ===
LOGIN_URL = config["target_login_url"]["login_url"]
USERNAME = config["target_credentials"]["username"]
PASSWORD = config["target_credentials"]["password"]

# Replace `{source_name}` in download directories dynamically
download_dirs = {
    key: value.replace("{source_name}", args.source_name)
    for key, value in config["download_dir"].items()
}

# Convert paths to absolute
MDMS_DIR = os.path.abspath(os.path.join(script_dir, download_dirs["mdms_dir"]))

# Extract MDMS Download Parameters
MDMS_DOWNLOADS = config["target_downloads"]["mdms_downloads"]
DOWNLOAD_BUTTON_XPATH = "//img[@onclick='downloadxls();']"

# Ensure the MDMS folder exists
os.makedirs(MDMS_DIR, exist_ok=True)


def initialize_webdriver(download_dir):
    """Set up and return the Chrome WebDriver with required options."""
    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "directory_upgrade": True
    }
    options.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def clear_specific_file(download_dir, file_name):
    """Delete the specific file if it exists."""
    file_path = os.path.join(download_dir, file_name)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Deleted existing file: {file_path}")
        except Exception as e:
            print(f"Failed to delete file {file_name}: {e}")


def login(driver, login_url, username, password):
    """Perform login to the application."""
    driver.get(login_url)
    driver.maximize_window()
    wait = WebDriverWait(driver, 20)

    try:
        # Enter username
        username_field = wait.until(EC.presence_of_element_located((By.ID, "UserUsername")))
        username_field.send_keys(username)

        # Enter password
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(password)

        # Click login button
        login_button = driver.find_element(By.XPATH, "//input[@value='Login']")
        login_button.click()

        print("Login successful.")
    except Exception as e:
        print(f"Login failed: {e}")
        raise


def navigate_and_download(driver, download_page_url, download_button_xpath):
    """Navigate to the download page and trigger the download."""
    try:
        driver.get(download_page_url)
        print("Navigated to download page.")
        wait = WebDriverWait(driver, 20)
        download_button = wait.until(EC.element_to_be_clickable((By.XPATH, download_button_xpath)))
        download_button.click()
        print("Download initiated.")
    except Exception as e:
        print(f"Failed to navigate or initiate download: {e}")
        raise


def wait_for_download_and_rename(download_dir, target_file_name, timeout=60):
    """Wait for the file to download and rename it."""
    print("Waiting for file download to complete...")
    start_time = time.time()
    initial_files = set(os.listdir(download_dir))

    while time.time() - start_time < timeout:
        time.sleep(1)
        current_files = set(os.listdir(download_dir))
        new_files = current_files - initial_files
        downloaded_files = [f for f in new_files if f.endswith('.xls')]

        if downloaded_files:
            latest_file = os.path.join(download_dir, downloaded_files[0])
            renamed_file = os.path.join(download_dir, target_file_name)
            try:
                os.rename(latest_file, renamed_file)
                print(f"File renamed to: {renamed_file}")
                return renamed_file
            except Exception as e:
                print(f"Error renaming file: {e}")
                return None

    raise TimeoutError("File download did not complete within the expected time.")


def main():
    """Main function to handle the entire process."""
    print(f"\nUsing Brand Folder: {args.source_name}")
    print(f"MDMS Directory: {MDMS_DIR}\n")

    driver = initialize_webdriver(MDMS_DIR)

    try:
        # Login to the application
        login(driver, LOGIN_URL, USERNAME, PASSWORD)

        for config in MDMS_DOWNLOADS:
            print(f"\nProcessing: {config['url']}")

            # Clean up previous file
            clear_specific_file(MDMS_DIR, config['file_to_delete'])

            # Navigate and download the new file
            navigate_and_download(driver, config['url'], DOWNLOAD_BUTTON_XPATH)

            # Wait for the download and rename the file
            try:
                wait_for_download_and_rename(MDMS_DIR, config['target_file_name'])
            except TimeoutError as e:
                print(str(e))

    except Exception as e:
        print(f"An error occurred during execution: {e}")

    finally:
        print("Closing browser...")
        driver.quit()


if __name__ == "__main__":
    main()
