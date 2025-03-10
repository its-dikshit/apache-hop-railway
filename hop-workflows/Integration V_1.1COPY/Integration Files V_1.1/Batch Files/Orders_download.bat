@echo off
setlocal

:: Check if source_name argument is provided
if "%~1"=="" (
    echo Usage: run_source_orders.bat [source_name]
    exit /b 1
)

:: Get the script directory (move one level up to find Automation Scripts)
set SCRIPT_DIR=%~dp0
set AUTOMATION_SCRIPTS_DIR=%SCRIPT_DIR%..\Automation Scripts\Source Scripts

:: Locate Source_Orders.py
set SOURCE_ORDERS_SCRIPT=%AUTOMATION_SCRIPTS_DIR%\Source_Orders.py

:: Check if Source_Orders.py exists
if not exist "%SOURCE_ORDERS_SCRIPT%" (
    echo Error: Source_Orders.py not found in %AUTOMATION_SCRIPTS_DIR%
    exit /b 1
)

:: Execute Source_Orders.py with source_name argument
echo Running Source_Orders.py with source_name: %1
python "%SOURCE_ORDERS_SCRIPT%" %1

:: End script
echo Execution completed successfully!
endlocal
