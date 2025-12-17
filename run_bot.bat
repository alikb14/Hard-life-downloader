@echo off
setlocal
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
REM Combined setup + run for tg-ytdlp-bot (Windows)

cd /d "%~dp0"

set LOGFILE=%~dp0run_bot.log
set VENV_DIR=%~dp0venv
set PY_EXE=%VENV_DIR%\Scripts\python.exe
set PIP_EXE=%VENV_DIR%\Scripts\pip.exe
set DEPS_MARK=%VENV_DIR%\.deps_installed
set CERT_FILE=%VENV_DIR%\Lib\site-packages\pip\_vendor\certifi\cacert.pem
set TASK_NAME=telegram-downloader-bot
set MODE=%1
set SKIP_INSTALL=0

if exist "%DEPS_MARK%" (
    set SKIP_INSTALL=1
)

echo -------------- >> "%LOGFILE%"
echo [%date% %time%] start run_bot.bat mode=%MODE% >> "%LOGFILE%"

REM Prefer py -3.11 if available; otherwise fall back to python
set PY_CMD=py -3.11
py -3.11 -c "import sys" >nul 2>&1
if errorlevel 1 (
    set PY_CMD=python
)

REM Rebuild venv if it exists but is not 3.11 and 3.11 is available (only when we plan to install)
set REBUILD_VENV=0
if "%SKIP_INSTALL%"=="0" (
    if exist "%PY_EXE%" (
        "%PY_EXE%" --version >nul 2>&1
        if errorlevel 1 (
            set REBUILD_VENV=1
            echo [%date% %time%] existing venv python is broken, rebuilding >> "%LOGFILE%"
        ) else (
            for /f "tokens=2" %%v in ('"%PY_EXE%" --version') do set VENV_VER=%%v
            for /f "tokens=1,2 delims=." %%a in ("%VENV_VER%") do set VENV_SHORT=%%a.%%b
            echo [%date% %time%] detected venv python %VENV_SHORT% >> "%LOGFILE%"
            if "%VENV_SHORT%" NEQ "3.11" (
                py -3.11 -c "import sys" >nul 2>&1
                if not errorlevel 1 (
                    set REBUILD_VENV=1
                    echo [%date% %time%] rebuilding venv to 3.11 >> "%LOGFILE%"
                ) else (
                    echo [%date% %time%] WARNING: venv is %VENV_SHORT% and 3.11 not available >> "%LOGFILE%"
                )
            )
        )
    )
)

if "%REBUILD_VENV%"=="1" (
    rmdir /s /q "%VENV_DIR%" 2>nul
    del "%DEPS_MARK%" 2>nul
)
if not exist "%CERT_FILE%" (
    echo [%date% %time%] cert bundle missing, forcing reinstall of deps >> "%LOGFILE%"
    set SKIP_INSTALL=0
)

echo [1/5] Ensuring virtual environment...
if not exist "%PY_EXE%" (
    %PY_CMD% -m venv "%VENV_DIR%" >> "%LOGFILE%" 2>&1
    if errorlevel 1 (
        echo Failed to create venv. See %LOGFILE% for details.
        echo [%date% %time%] venv creation failed >> "%LOGFILE%"
        exit /b 1
    )
) else (
    echo venv already exists, skipping creation.
)

echo [2/5] Installing requirements (skip if already done)...
if "%SKIP_INSTALL%"=="1" (
    echo Requirements already installed, skipping.
) else (
    call "%PY_EXE%" -m pip install --upgrade --force-reinstall --no-cache-dir pip certifi >> "%LOGFILE%" 2>&1
    call "%PY_EXE%" -m pip install --upgrade pip >> "%LOGFILE%" 2>&1
    call "%PIP_EXE%" install --no-cache-dir -r requirements.txt >> "%LOGFILE%" 2>&1
    if errorlevel 1 (
        echo Failed to install requirements. See %LOGFILE%.
        echo [%date% %time%] requirements install failed >> "%LOGFILE%"
        exit /b 1
    )
    echo ok>"%DEPS_MARK%"
)

echo [3/5] Creating/Updating Windows scheduled task (runs on user logon)...
schtasks /Create /TN "%TASK_NAME%" /TR "\"%~dp0run_bot.bat\" auto" /SC ONLOGON /RL HIGHEST /F >> "%LOGFILE%" 2>&1
if errorlevel 1 (
    echo [%date% %time%] schtasks create failed with /RL HIGHEST, retrying without elevation... >> "%LOGFILE%"
    schtasks /Create /TN "%TASK_NAME%" /TR "\"%~dp0run_bot.bat\" auto" /SC ONLOGON /F >> "%LOGFILE%" 2>&1
)

REM ------------------------------------------------
REM Start local cookie HTTP server (BACKGROUND)
REM ------------------------------------------------
echo [3.5/5] Starting local cookie HTTP server...
cd /d "%~dp0cookies"
start "cookie-server" /min python -m http.server 8080
cd /d "%~dp0"

echo [4/5] Starting bot...
call "%~dp0venv\Scripts\activate.bat" >> "%LOGFILE%" 2>&1
"%PY_EXE%" magic.py >> "%LOGFILE%" 2>&1

echo Done.
if /I not "%MODE%"=="auto" (
    echo.
    echo Press any key to close...
    pause >nul
)
endlocal
goto :eof
