#!/bin/bash
# ----------------------------------------------------------------------------------------------------
# FILE: install_macos.sh
# PROJECT: Communication Systems Engineering - Speech Recognition System
# INSTITUTION: HCMUT
# DESCRIPTION: Environment setup script for macOS (Requires Homebrew).
# ----------------------------------------------------------------------------------------------------

echo "========================================================"
echo "      SETUP ENVIRONMENT FOR MACOS"
echo "========================================================"

# 1. Cài đặt PortAudio (Yêu cầu bắt buộc cho sounddevice trên Mac)
if ! command -v brew &> /dev/null; then
    echo "[ERROR] Homebrew is required. Please install it first."
    exit 1
fi

echo "[1/3] Installing System Dependencies (PortAudio)..."
brew install portaudio

# 2. Tạo môi trường ảo (Khuyên dùng trên Mac để không xung đột hệ thống)
echo "[2/3] Creating Python Virtual Environment (Optional but recommended)..."
python3 -m venv venv
source venv/bin/activate

# 3. Cài đặt thư viện
echo "[3/3] Installing Python Dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

echo "========================================================"
echo "      INSTALLATION COMPLETED!"
echo "Note: On macOS, 'keyboard' library requires sudo privileges"
echo "or Accessibility permissions in System Settings."
echo "========================================================"