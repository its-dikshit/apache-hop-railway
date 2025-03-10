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

# Extract MDMS Upload Parameters for Outlets
MDMS_UPLOAD = config["target_mdm_uploads"]["create_outlets_mdm"]
UPLOAD_URL = MDMS_UPLOAD["upload_url"]
FILE_NAME = MDMS_UPLOAD["file_name"]

# Extract MDMS Directory
MDMS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), config["download_dir"]["mdms_dir"]))

# Initialize WebDriver
options = webdriver.ChromeOptions()
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# **Maximize browser window for better visibility**
driver.maximize_window()

try:
    # Step 1: Login
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 15)

    username_input = wait.until(EC.element_to_be_clickable((By.ID, "UserUsername")))
    username_input.send_keys(USERNAME)

    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys(PASSWORD)

    login_button = driver.find_element(By.CSS_SELECTOR, "input[title='Login to Bizom']")
    driver.execute_script("arguments[0].click();", login_button)  # JavaScript click for reliability
    print("Logged in successfully.")

    # Wait for the dashboard to load
    time.sleep(3)

    print(f"Processing Upload: {FILE_NAME}")

    # Step 2: Navigate to the specific MDMS upload page
    driver.get(UPLOAD_URL)

    # Step 3: Locate the Upload Button and Click It
    upload_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//img[@src='/img/upload.jpeg']")))
    driver.execute_script("arguments[0].scrollIntoView(true);", upload_button)
    driver.execute_script("arguments[0].click();", upload_button)
    print("Upload button clicked.")

    # Step 4: Find the specific file to upload
    if not os.path.exists(MDMS_DIR):
        print(f"Error: Folder not found: {MDMS_DIR}")
    else:
        file_path = os.path.join(MDMS_DIR, FILE_NAME)
        if not os.path.exists(file_path):
            print(f"Error: No file named '{FILE_NAME}' found in folder {MDMS_DIR}")
        else:
            # Upload the file
            file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            driver.execute_script("arguments[0].scrollIntoView(true);", file_input)
            file_input.send_keys(file_path)

            # Confirm upload
            time.sleep(3)
            print(f"Uploaded file: {file_path}")

            # Step 5: Click the "Validate data" button
            validate_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@onclick=\"saveDataFromTable('validate');\"]")))
            driver.execute_script("arguments[0].scrollIntoView(true);", validate_button)
            driver.execute_script("arguments[0].click();", validate_button)
            print("Validate data button clicked.")

            # Step 6: Wait for validation message
            try:
                validation_message = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "text-success"))
                )
                validation_text = validation_message.text
            except:
                validation_text = ""

            if "Validation is successful" in validation_text:
                # Step 7: Click the "Save data" button
                save_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@onclick=\"saveDataFromTable('save');\"]")))
                driver.execute_script("arguments[0].scrollIntoView(true);", save_button)
                driver.execute_script("arguments[0].click();", save_button)
                print("Data saved successfully.")
            else:
                # Step 8: Click "Cancel Upload" if validation fails
                cancel_button = driver.find_element(By.ID, "cancel-btn")
                driver.execute_script("arguments[0].scrollIntoView(true);", cancel_button)
                driver.execute_script("arguments[0].click();", cancel_button)
                print("Upload canceled due to validation issues.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the browser
    driver.quit()
