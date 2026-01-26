#!/bin/bash
# ----------------------------------------------------------------------------------------------------
# FILE: install_arch.sh
# PROJECT: Communication Systems Engineering - Speech Recognition System
# INSTITUTION: HCMUT
# DESCRIPTION: Setup for Arch Linux/Manjaro/EndeavourOS.
# ----------------------------------------------------------------------------------------------------

echo "========================================================"
echo "      SETUP ENVIRONMENT FOR ARCH LINUX"
echo "========================================================"

# 1. Cài đặt gói hệ thống
echo "[1/3] Installing System Dependencies..."
sudo pacman -Syu --noconfirm python-pip portaudio tk

# 2. Cài đặt thư viện Python
echo "[2/3] Installing Python Dependencies..."
# Arch Linux quản lý python rất chặt, thường yêu cầu cài qua pacman hoặc venv
# Ở đây dùng pip install --user để an toàn
python -m pip install --upgrade pip
python -m pip install --user -r requirements.txt

echo "========================================================"
echo "      INSTALLATION COMPLETED!"
echo "========================================================"