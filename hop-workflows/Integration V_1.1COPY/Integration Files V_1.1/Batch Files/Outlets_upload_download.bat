@echo off
setlocal enabledelayedexpansion

:: Check if source_name argument is provided
if "%~1"=="" (
    echo Usage: Outlets_upload_download.bat [source_name]
    exit /b 1
)

:: Get the script directory and move one level up
set SCRIPT_DIR=%~dp0
set PARENT_DIR=%SCRIPT_DIR%..\

:: Define Automation Scripts directory dynamically
set AUTOMATION_SCRIPTS_DIR=%PARENT_DIR%Automation Scripts

:: Set the upload and target script paths
set UPLOAD_SCRIPTS_DIR=%AUTOMATION_SCRIPTS_DIR%\Upload Scripts
set TARGET_SCRIPTS_DIR=%AUTOMATION_SCRIPTS_DIR%\Target Scripts

:: Store the source_name argument correctly
set "SOURCE_NAME=%~1"

:: ======= Run create_outlets_mdm.py =======
if exist "%UPLOAD_SCRIPTS_DIR%\create_outlets_mdm.py" (
    echo Running create_outlets_mdm.py with source_name: "%SOURCE_NAME%"
    python "%UPLOAD_SCRIPTS_DIR%\create_outlets_mdm.py" "%SOURCE_NAME%"
) else (
    echo Error: create_outlets_mdm.py not found in Upload Scripts
    exit /b 1
)

:: Wait for 5 seconds before running the next script
echo Waiting for 5 seconds...
timeout /t 5 /nobreak >nul

:: ======= Run Target_Outlets.py =======
if exist "%TARGET_SCRIPTS_DIR%\Target_Outlets.py" (
    echo Running Target_Outlets.py with source_name: "%SOURCE_NAME%"
    python "%TARGET_SCRIPTS_DIR%\Target_Outlets.py" "%SOURCE_NAME%"
) else (
    echo Error: Target_Outlets.py not found in Target Scripts
    exit /b 1
)

echo All scripts executed successfully!
endlocal
exit /b 0
