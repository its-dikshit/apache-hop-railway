@echo off
setlocal enabledelayedexpansion

:: Check if source_name argument is provided
if "%~1"=="" (
    echo Usage: run_upload_orders_mdm.bat [source_name]
    exit /b 1
)

:: Get the script directory and move one level up
set SCRIPT_DIR=%~dp0
set PARENT_DIR=%SCRIPT_DIR%..\

:: Define Automation Scripts directory dynamically
set AUTOMATION_SCRIPTS_DIR=%PARENT_DIR%Automation Scripts

:: Set the upload script path
set UPLOAD_SCRIPTS_DIR=%AUTOMATION_SCRIPTS_DIR%\Upload Scripts

:: Store the source_name argument correctly
set "SOURCE_NAME=%~1"

:: ======= Run upload_orders_mdm.py =======
if exist "%UPLOAD_SCRIPTS_DIR%\upload_orders_mdm.py" (
    echo Running upload_orders_mdm.py with source_name: "%SOURCE_NAME%"
    python "%UPLOAD_SCRIPTS_DIR%\upload_orders_mdm.py" "%SOURCE_NAME%"
) else (
    echo Error: upload_orders_mdm.py not found in Upload Scripts
    exit /b 1
)

echo Script executed successfully!
endlocal
exit /b 0
