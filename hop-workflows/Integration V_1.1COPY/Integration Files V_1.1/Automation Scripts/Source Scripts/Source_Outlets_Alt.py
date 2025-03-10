import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Parameterized values
USERNAME = "test@qunova"
PASSWORD = "Test@123"
LOGIN_URL = "https://bizzplus.bizom.in/users/login"
DASHBOARD_URL = "https://bizzplus.bizom.in/companies/dashboard"
DOWNLOAD_URL = "https://bizzplus.bizom.in/companies/downloadoutletforwarehouse/95"
DOWNLOAD_SOURCE_FILE = "Source_Outlets_Alt"
FILE_EXTENSION = ".csv"
DOWNLOAD_DIR = "../Source"

def main():
    # Define paths
    scripts_dir = os.path.abspath(os.path.dirname(__file__))
    source_dir = os.path.abspath(os.path.join(scripts_dir, DOWNLOAD_DIR))

    if not os.path.exists(source_dir):
        os.makedirs(source_dir)

    # Remove existing source file before proceeding
    source_file_path = os.path.join(source_dir, f"{DOWNLOAD_SOURCE_FILE}{FILE_EXTENSION}")
    if os.path.exists(source_file_path):
        os.remove(source_file_path)

    # Configure Chrome options
    chrome_options = Options()
    prefs = {
        "download.default_directory": source_dir,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Initialize the WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.maximize_window()  # Maximize the browser window
    wait = WebDriverWait(driver, 20)

    try:
        # Step 1: Login to the website
        driver.get(LOGIN_URL)

        # Locate and fill username
        username_field = wait.until(EC.presence_of_element_located((By.ID, "UserUsername")))
        username_field.send_keys(USERNAME)

        # Locate and fill password
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(PASSWORD)

        # Locate and click the Login button
        login_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
        login_button.click()

        # Step 2: Ensure login success and navigate to the dashboard
        wait.until(EC.url_contains("/users/dashboard"))  # Ensure login is successful
        driver.get(DASHBOARD_URL)

        # Step 3: Directly access the download link
        download_start_time = time.time()
        driver.get(DOWNLOAD_URL)  # Direct download request

        # Step 4: Wait for the file to download
        downloaded_file_path = wait_for_download(source_dir, download_start_time, FILE_EXTENSION)

        # Step 5: Rename the downloaded file
        rename_downloaded_file(downloaded_file_path, DOWNLOAD_SOURCE_FILE, FILE_EXTENSION)

    finally:
        # Close the browser
        driver.quit()

def wait_for_download(source_dir, download_start_time, file_extension, timeout=60):
    """Wait for a file to be downloaded in the source directory after the given timestamp."""
    start_time = time.time()
    while True:
        files = os.listdir(source_dir)
        for file in files:
            file_path = os.path.join(source_dir, file)
            if file.endswith(file_extension) and os.path.getctime(file_path) > download_start_time:
                return file_path
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Download timed out after waiting for {timeout} seconds.")
        time.sleep(1)

def rename_downloaded_file(downloaded_file_path, new_name, file_extension):
    """Rename the downloaded file to the specified name, keeping the file extension unchanged."""
    source_dir = os.path.dirname(downloaded_file_path)
    source_file_path = os.path.join(source_dir, f"{new_name}{file_extension}")

    # Rename the downloaded file
    os.rename(downloaded_file_path, source_file_path)
    print(f"Renamed file {downloaded_file_path} to {source_file_path}")

if __name__ == "__main__":
    main()
