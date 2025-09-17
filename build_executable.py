#!/usr/bin/env python3
"""
Build script for Social Media Downloader executable
Run this script to create the .exe file
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"STEP: {description}")
    print(f"{'='*50}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stdout:
            print("stdout:", e.stdout)
        if e.stderr:
            print("stderr:", e.stderr)
        return False

def main():
    print("Social Media Downloader - Build Script")
    print("=" * 50)
    
    # Check if Python is installed
    try:
        python_version = subprocess.run([sys.executable, "--version"], 
                                      capture_output=True, text=True)
        print(f"Python version: {python_version.stdout.strip()}")
    except Exception:
        print("Error: Python not found!")
        return False
    
    # Install required packages for building
    build_requirements = [
        "pyinstaller>=5.13.0",
        "auto-py-to-exe>=2.40.0",
    ]
    
    print("\nInstalling build dependencies...")
    for requirement in build_requirements:
        if not run_command(f'pip install "{requirement}"', 
                         f"Installing {requirement}"):
            return False
    
    # Install project dependencies
    print("\nInstalling project dependencies...")
    if not run_command("pip install -r requirements.txt", 
                      "Installing project requirements"):
        return False
    
    # Create icon if it doesn't exist (optional)
    icon_path = Path("icon.ico")
    if not icon_path.exists():
        print("\nWarning: icon.ico not found. The exe will be built without an icon.")
        print("You can add an icon.ico file in the same directory for a custom icon.")
    
    # Clean previous builds
    build_dirs = ["build", "dist", "__pycache__"]
    for dir_name in build_dirs:
        if Path(dir_name).exists():
            print(f"Cleaning {dir_name}...")
            shutil.rmtree(dir_name)
    
    # Build with PyInstaller using the spec file
    print("\nBuilding executable with PyInstaller...")
    spec_file = "social_downloader.spec"
    
    if Path(spec_file).exists():
        build_cmd = f"pyinstaller {spec_file} --clean --noconfirm"
    else:
        # Fallback to direct command if spec file doesn't exist
        build_cmd = (
            "pyinstaller --onefile --windowed --clean --noconfirm "
            "--add-data \"venv/Lib/site-packages/customtkinter;customtkinter/\" "
            "--hidden-import customtkinter --hidden-import yt_dlp "
            "--hidden-import requests --hidden-import PIL "
            "--name SocialMediaDownloader test2.py"
        )
        
        if icon_path.exists():
            build_cmd += f" --icon={icon_path}"
    
    if not run_command(build_cmd, "Building executable"):
        return False
    
    # Check if build was successful
    exe_path = Path("dist/SocialMediaDownloader.exe")
    if exe_path.exists():
        file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
        print(f"\n{'='*50}")
        print("BUILD SUCCESSFUL!")
        print(f"{'='*50}")
        print(f"Executable created: {exe_path}")
        print(f"File size: {file_size:.1f} MB")
        print("\nNext steps:")
        print("1. Test the executable by running it")
        print("2. Create an installer using the installer script")
        return True
    else:
        print("\n" + "="*50)
        print("BUILD FAILED!")
        print("="*50)
        print("The executable was not created successfully.")
        return False

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)