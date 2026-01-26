:: ----------------------------------------------------------------------------------------------------
:: FILE: install_windows.bat
:: PROJECT: Communication Systems Engineering - Speech Recognition System
:: INSTITUTION: Ho Chi Minh City University of Technology (HCMUT)
:: AUTHORS: Do Ngoc Gia Bao, Thai Duc Thien, Pham Minh Quang
:: DESCRIPTION: Environment setup script for Windows OS.
:: ----------------------------------------------------------------------------------------------------

@echo off
echo ========================================================
echo      SETUP ENVIRONMENT FOR WINDOWS
echo ========================================================

:: 1. Kiểm tra Python
python --version
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python chưa được cài đặt hoặc chưa thêm vào PATH.
    pause
    exit /b
)

:: 2. Nâng cấp PIP để tránh lỗi cài đặt wheel
echo.
echo [1/2] Upgrading pip...
python -m pip install --upgrade pip

:: 3. Cài đặt thư viện từ requirements.txt
echo.
echo [2/2] Installing dependencies...
python -m pip install -r requirements.txt

echo.
echo ========================================================
echo      INSTALLATION COMPLETED SUCCESSFULLY!
echo ========================================================
pause