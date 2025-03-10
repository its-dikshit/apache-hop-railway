import time
import os
import json
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

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

# Extract MDMS Upload Parameters for Categories
MDMS_UPLOAD = config["target_mdm_uploads"]["create_categories_mdm"]
UPLOAD_URL = MDMS_UPLOAD["upload_url"]
FILE_NAME = MDMS_UPLOAD["file_name"]

# Extract MDMS Directory
MDMS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), config["download_dir"]["mdms_dir"]))

# Initialize WebDriver
options = webdriver.ChromeOptions()
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # Step 1: Login
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 10)
    
    username_input = wait.until(EC.presence_of_element_located((By.ID, "UserUsername")))
    username_input.send_keys(USERNAME)

    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys(PASSWORD)

    login_button = driver.find_element(By.CSS_SELECTOR, "input[title='Login to Bizom']")
    login_button.click()

    # Wait for the dashboard to load
    time.sleep(1)

    print(f"Processing Upload: {FILE_NAME}")

    # Step 2: Navigate to the specific MDMS upload page
    driver.get(UPLOAD_URL)

    # Locate the upload button
    upload_button = wait.until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='mdmFileUploadForm']/div/div[2]/label/img"))
    )

    # Step 3: Find the specific file to upload
    if not os.path.exists(MDMS_DIR):
        print(f"Folder not found: {MDMS_DIR}")
    else:
        file_path = os.path.join(MDMS_DIR, FILE_NAME)
        if not os.path.exists(file_path):
            print(f"No file named '{FILE_NAME}' found in folder {MDMS_DIR}")
        else:
            # Upload the file
            file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            file_input.send_keys(file_path)

            # Confirm upload
            time.sleep(2)
            print(f"Uploaded file: {file_path}")

            # Step 4: Validate data
            validate_button = driver.find_element(By.CSS_SELECTOR, "button[onclick=\"saveDataFromTable('validate');\"]")
            validate_button.click()

            # Wait for validation message
            validation_message = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "text-success"))
            )

            if "Validation is successful" in validation_message.text:
                # Click Save data button
                save_button = driver.find_element(By.CSS_SELECTOR, "button[onclick=\"saveDataFromTable('save');\"]")
                save_button.click()
                print("Data saved successfully.")
            else:
                # Click Cancel Upload button
                cancel_button = driver.find_element(By.ID, "cancel-btn")
                cancel_button.click()
                print("Upload canceled due to validation issues.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the browser
    driver.quit()
