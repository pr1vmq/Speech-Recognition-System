#!/bin/bash
# ----------------------------------------------------------------------------------------------------
# FILE: install_debian.sh
# PROJECT: Communication Systems Engineering - Speech Recognition System
# INSTITUTION: HCMUT
# DESCRIPTION: Setup for Debian/Ubuntu/Mint/Kali Linux.
# ----------------------------------------------------------------------------------------------------

echo "========================================================"
echo "      SETUP ENVIRONMENT FOR DEBIAN/UBUNTU"
echo "========================================================"

# 1. Cài đặt các gói hệ thống cần thiết
echo "[1/3] Installing System Dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv portaudio19-dev python3-tk

# 2. Cài đặt thư viện Python
echo "[2/3] Installing Python Dependencies..."
# Lưu ý: Trên các bản Ubuntu mới, có thể cần flag --break-system-packages nếu không dùng venv
# Tuy nhiên, khuyến khích dùng pip cơ bản trước.
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "========================================================"
echo "      INSTALLATION COMPLETED!"
echo "Note: You might need to run the app with 'sudo' to capture keyboard events."
echo "========================================================"