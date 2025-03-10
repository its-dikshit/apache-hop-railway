@echo off
setlocal enabledelayedexpansion

:: Check if source_name argument is provided
if "%~1"=="" (
    echo Usage: Skunits_update.bat [source_name]
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

:: ======= Run update_skunits_mdm.py =======
if exist "%UPLOAD_SCRIPTS_DIR%\update_skunits_mdm.py" (
    echo Running update_skunits_mdm.py with source_name: "%SOURCE_NAME%"
    python "%UPLOAD_SCRIPTS_DIR%\update_skunits_mdm.py" "%SOURCE_NAME%"
) else (
    echo Error: update_skunits_mdm.py not found in Upload Scripts
    exit /b 1
)

echo Script executed successfully!
endlocal
exit /b 0
