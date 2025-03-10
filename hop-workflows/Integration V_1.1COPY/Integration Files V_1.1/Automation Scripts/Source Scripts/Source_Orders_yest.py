import os
import time
import json
import argparse
import zipfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException
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
USERNAME = config["source_distributor_credentials"]["username"]
PASSWORD = config["source_distributor_credentials"]["password"]

# Extract global download directory
SOURCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), config["download_dir"]["source_dir"]))

# Extract specific parameters for Source_Orders
download_params = config["source_downloads"]["source_orders"]
REPORT_URL = download_params["report_url"]
FILE_PREFIX = download_params["file_prefix"]
ZONE_SELECTION_VALUE = download_params["zone_selection_value"]


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


def clear_specific_file(download_dir, file_prefix):
    """Deletes a specific file in the download directory."""
    file_deleted = False
    for file in os.listdir(download_dir):
        if file.startswith(file_prefix):
            file_path = os.path.join(download_dir, file)
            try:
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
                file_deleted = True
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")
    if not file_deleted:
        print(f"No file with prefix '{file_prefix}' found to delete.")


def wait_for_download_to_finish_and_rename(download_dir, new_file_name, timeout=120):
    """Waits for the download to finish and renames the downloaded file."""
    print("Waiting for file download to complete...")
    start_time = time.time()
    initial_files = set(os.listdir(download_dir))

    while time.time() - start_time < timeout:
        time.sleep(1)
        current_files = set(os.listdir(download_dir))
        new_files = current_files - initial_files
        downloaded_files = [f for f in new_files if not f.endswith(".crdownload")]

        if downloaded_files:
            latest_file = os.path.join(download_dir, downloaded_files[0])
            renamed_file = os.path.join(download_dir, new_file_name)
            try:
                os.rename(latest_file, renamed_file)
                print(f"File renamed to: {renamed_file}")
                return renamed_file
            except Exception as e:
                print(f"Error renaming file: {e}")
                return None
    raise TimeoutError("File download did not complete within the expected time.")


def wait_for_data_to_load(driver, timeout=60):
    """Waits for the data to load after clicking the update button."""
    print("Waiting for data to load...")
    try:
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element((By.XPATH, "//div[contains(@class, 'loading-indicator')]"))
        )
        print("Data loaded successfully.")
    except Exception as e:
        print(f"Data loading took too long: {e}")


def login_and_navigate(driver, login_url, report_url, username, password):
    """Handles the login process and navigates to the reports page."""
    driver.get(login_url)
    driver.maximize_window()

    wait = WebDriverWait(driver, 20)
    username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
    username_field.send_keys(username)

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(password)

    login_button = driver.find_element(By.ID, "login")
    login_button.click()

    print("Login successful. Navigating to reports page...")

    # Navigate to the reports page after login
    time.sleep(3)
    driver.get(report_url)


def main():
    ensure_directory_exists(SOURCE_DIR)

    # Ensure specific file is deleted before proceeding
    clear_specific_file(SOURCE_DIR, FILE_PREFIX)

    driver = initialize_webdriver(SOURCE_DIR)

    try:
        # Login and navigate to reports page
        login_and_navigate(driver, LOGIN_URL, REPORT_URL, USERNAME, PASSWORD)

        # Dropdown Handling
        wait = WebDriverWait(driver, 20)
        dropdown_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'multiselect dropdown-toggle')]")))
        dropdown_button.click()

        while True:
            all_checkboxes = driver.find_elements(By.XPATH, "//label[contains(@class, 'checkbox')]/input[@type='checkbox']")
            stale_element_found = False
            for checkbox in all_checkboxes:
                try:
                    if checkbox.is_selected():
                        checkbox.click()
                except StaleElementReferenceException:
                    stale_element_found = True
                    break
            if not stale_element_found:
                break

        # Select Zone Checkbox
        zone_checkbox = wait.until(EC.presence_of_element_located((By.XPATH, f"//label[contains(@class, 'checkbox')]/input[@value='{ZONE_SELECTION_VALUE}']")))

        if not zone_checkbox.is_selected():
            zone_checkbox.click()
        print(f"Checkbox with value '{ZONE_SELECTION_VALUE}' selected successfully.")

        # Select Date Option
        date_dropdown = wait.until(EC.presence_of_element_located((By.ID, "reportrange0")))
        driver.execute_script("arguments[0].scrollIntoView(true);", date_dropdown)
        driver.execute_script("arguments[0].click();", date_dropdown)

        today_option = wait.until(EC.presence_of_element_located((By.XPATH, "//li[contains(text(), 'Yesterday')]")))
        driver.execute_script("arguments[0].click();", today_option)
        print("Date option 'Today' selected successfully.")

        # Update Reports
        update_button = wait.until(EC.presence_of_element_located((By.ID, "reportsUpdateButton")))
        for _ in range(3):
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", update_button)
                driver.execute_script("arguments[0].click();", update_button)
                print("Update button clicked successfully.")
                break
            except ElementClickInterceptedException:
                print("Retrying click on update button...")
                time.sleep(1)

        # Wait for data to load
        wait_for_data_to_load(driver)

        # Download Reports
        option_dropdown = wait.until(EC.presence_of_element_located((By.ID, "option-dropdown")))
        driver.execute_script("arguments[0].scrollIntoView(true);", option_dropdown)
        driver.execute_script("arguments[0].click();", option_dropdown)

        download_link = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@onclick, 'downloadReport(4)')]")))
        driver.execute_script("arguments[0].click();", download_link)
        print("Download initiated successfully.")

        # Wait for Download to Finish and Rename
        try:
            renamed_file = wait_for_download_to_finish_and_rename(SOURCE_DIR, FILE_PREFIX + ".csv")
            print(f"Process completed successfully. File available at: {renamed_file}")
        except TimeoutError as e:
            print(str(e))

    finally:
        print("Closing browser...")
        driver.quit()


if __name__ == "__main__":
    main()
