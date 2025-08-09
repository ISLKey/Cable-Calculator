#!/bin/bash

# Check for Python installation
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.10+ from your package manager or python.org."
    exit 1
fi

# Check for pip installation
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install pip3 from your package manager."
    exit 1
fi

echo "Checking and installing dependencies..."

# Install Pillow for image handling
pip3 install Pillow

# Check for tkinter (Linux/Mac specific)
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "tkinter is not installed. Installing..."
    if command -v apt-get &> /dev/null; then
        # Debian/Ubuntu
        sudo apt-get update && sudo apt-get install python3-tk -y
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        sudo yum install tkinter -y
    elif command -v dnf &> /dev/null; then
        # Fedora
        sudo dnf install python3-tkinter -y
    elif command -v pacman &> /dev/null; then
        # Arch Linux
        sudo pacman -S tk --noconfirm
    elif command -v brew &> /dev/null; then
        # macOS with Homebrew
        brew install python-tk
    else
        echo "Could not automatically install tkinter. Please install it manually for your system."
        exit 1
    fi
fi

echo "Dependencies checked/installed. Launching GUI..."

python3 cable_calculator.py

echo "Press any key to continue..."
read -n 1 -s

