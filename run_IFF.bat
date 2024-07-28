@echo off
setlocal enabledelayedexpansion

REM Set repository information
set REPO_URL=https://raw.githubusercontent.com/Keymasterkid/IFF/main
set VERSION_FILE=version.txt

REM Check for the latest version on GitHub
echo Checking for updates...
curl -s %REPO_URL%/%VERSION_FILE% -o latest_version.txt

REM Check if the version file was downloaded
if not exist latest_version.txt (
    echo Error: Could not download version file from GitHub.
    pause
    exit /b
)

REM Read the current version from config.json
set "CURRENT_VERSION="
for /f "tokens=2 delims=:," %%a in ('findstr "version" config.json') do (
    set "CURRENT_VERSION=%%a"
    set "CURRENT_VERSION=!CURRENT_VERSION:~2,-1!"
)

REM Check if CURRENT_VERSION is set
if "%CURRENT_VERSION%"=="" (
    echo Error: Could not read current version from config.json.
    pause
    exit /b
)

REM Read the latest version from the downloaded version file
set /p LATEST_VERSION=<latest_version.txt

REM Remove any potential newline characters from LATEST_VERSION
for /f "delims=" %%a in ("%LATEST_VERSION%") do set LATEST_VERSION=%%a

REM Output the current and latest version for debugging
echo Current version: [%CURRENT_VERSION%]
echo Latest version: [%LATEST_VERSION%]

REM Compare versions using goto
echo Comparing versions...
if "%CURRENT_VERSION%"=="%LATEST_VERSION%" (
    goto :equal_versions
) else (
    goto :unequal_versions
)

:equal_versions
echo You are using the latest version (%CURRENT_VERSION%).
goto :install_packages

:unequal_versions
echo A new version (%LATEST_VERSION%) is available. You are using version %CURRENT_VERSION%.
set /p UPDATE=Do you want to update? (Y/N): 
if /i "%UPDATE%"=="Y" (
    echo Updating...
    curl -s %REPO_URL%/IFF.py -o IFF.py
    echo Updated to version %LATEST_VERSION%.
    REM Update the version in config.json
    powershell -Command "(Get-Content config.json) -replace '\"version\": \"%CURRENT_VERSION%\"', '\"version\": \"%LATEST_VERSION%\"' | Set-Content config.json"
) else (
    echo Skipping update.
)

:install_packages
REM Install required Python packages
echo Installing required Python packages...
pip install instaloader colorama

REM Run the Python script
echo Running Instagram Followers/Followings Checker...
python IFF.py
pause

endlocal
