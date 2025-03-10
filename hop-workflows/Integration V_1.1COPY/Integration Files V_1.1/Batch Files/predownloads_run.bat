@echo off
setlocal enabledelayedexpansion

:: Check if source_name argument is provided
if "%~1"=="" (
    echo Usage: run_all_scripts.bat [source_name]
    exit /b 1
)

:: Get the script directory and move one level up
set SCRIPT_DIR=%~dp0
set PARENT_DIR=%SCRIPT_DIR%..\

:: Define Automation Scripts directory dynamically
set AUTOMATION_SCRIPTS_DIR=%PARENT_DIR%Automation Scripts

:: Ensure the directories exist before proceeding
if not exist "%AUTOMATION_SCRIPTS_DIR%\Source Scripts" (
    echo Error: Source Scripts directory not found in %AUTOMATION_SCRIPTS_DIR%
    exit /b 1
)

if not exist "%AUTOMATION_SCRIPTS_DIR%\Target Scripts" (
    echo Error: Target Scripts directory not found in %AUTOMATION_SCRIPTS_DIR%
    exit /b 1
)

:: Store the source_name argument correctly
set "SOURCE_NAME=%~1"

:: ======= Run Source Scripts =======
echo Running Source Scripts...
for %%S in (
    Source_Areas.py
    Source_Skunits.py
    Source_Outlets.py
) do (
    if exist "%AUTOMATION_SCRIPTS_DIR%\Source Scripts\%%S" (
        echo Running %%S with source_name: "%SOURCE_NAME%"
        python "%AUTOMATION_SCRIPTS_DIR%\Source Scripts\%%S" "%SOURCE_NAME%"
    ) else (
        echo Error: %%S not found in Source Scripts
    )
)

:: ======= Run Target Scripts =======
echo Running Target Scripts...
for %%S in (
    Target_Categories.py
    Target_Subcategories.py
    Target_Mdms.py
) do (
    if exist "%AUTOMATION_SCRIPTS_DIR%\Target Scripts\%%S" (
        echo Running %%S with source_name: "%SOURCE_NAME%"
        python "%AUTOMATION_SCRIPTS_DIR%\Target Scripts\%%S" "%SOURCE_NAME%"
    ) else (
        echo Error: %%S not found in Target Scripts
    )
)

echo All scripts executed successfully!
endlocal
exit /b 0
