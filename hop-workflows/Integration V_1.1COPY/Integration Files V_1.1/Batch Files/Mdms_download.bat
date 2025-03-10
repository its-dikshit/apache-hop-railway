@echo off
setlocal

:: Check if source_name argument is provided
if "%~1"=="" (
    echo Usage: run_target_mdms.bat [source_name]
    exit /b 1
)

:: Get the script directory
set SCRIPT_DIR=%~dp0

:: Move up one level to find "Automation Scripts"
set AUTOMATION_SCRIPTS_DIR=%SCRIPT_DIR%..\Automation Scripts\Target Scripts

:: Locate Target_Mdms.py
set TARGET_MDMS_SCRIPT=%AUTOMATION_SCRIPTS_DIR%\Target_Mdms.py

:: Check if Target_Mdms.py exists
if not exist "%TARGET_MDMS_SCRIPT%" (
    echo Error: Target_Mdms.py not found in %AUTOMATION_SCRIPTS_DIR%
    exit /b 1
)

:: Execute Target_Mdms.py with source_name argument
echo Running Target_Mdms.py with source_name: %1
python "%TARGET_MDMS_SCRIPT%" %1

:: End script
echo Execution completed successfully!
endlocal
