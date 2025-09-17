#!/usr/bin/env python3
"""
Complete build script for Social Media Downloader
Creates both the executable and the installer
"""

import os
import sys
import subprocess
import shutil
import urllib.request
import zipfile
from pathlib import Path

def run_command(command, description, critical=True):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"STEP: {description}")
    print(f"{'='*60}")
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
        if critical:
            print("This is a critical error. Build cannot continue.")
            return False
        else:
            print("This is a non-critical error. Continuing...")
            return True

def download_file(url, destination, description):
    """Download a file with progress"""
    print(f"\nDownloading {description}...")
    print(f"URL: {url}")
    print(f"Destination: {destination}")
    
    try:
        def progress_hook(block_num, block_size, total_size):
            if total_size > 0:
                percent = min(100, (block_num * block_size * 100) // total_size)
                print(f"\rProgress: {percent}%", end="", flush=True)
        
        urllib.request.urlretrieve(url, destination, progress_hook)
        print(f"\n{description} downloaded successfully!")
        return True
    except Exception as e:
        print(f"\nFailed to download {description}: {e}")
        return False

def create_license_file():
    """Create a basic LICENSE.txt file"""
    license_content = """MIT License

Copyright (c) 2025 Social Media Downloader

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

    with open("LICENSE.txt", "w", encoding="utf-8") as f:
        f.write(license_content)
    print("Created LICENSE.txt")

def create_readme_file():
    """Create a README.md file"""
    readme_content = """# Social Media Downloader

A powerful desktop application for downloading videos and files from various social media platforms including YouTube, Instagram, TikTok, Twitter, and Facebook.

## Features

- **Multi-Platform Support**: Download from YouTube, Instagram, TikTok, Twitter, Facebook, and more
- **File Downloads**: Direct file downloads from URLs
- **High-Quality Downloads**: Choose your preferred video quality and audio bitrate
- **Concurrent Downloads**: Download multiple files simultaneously
- **Pause/Resume**: Full control over your downloads
- **Progress Tracking**: Real-time download progress and speed monitoring
- **Modern UI**: Clean, intuitive interface with dark/light theme support

## Installation

1. Run `SocialMediaDownloader_Setup.exe`
2. Follow the installation wizard
3. The installer will automatically download and configure FFmpeg
4. Launch the application from the desktop shortcut or Start menu

## System Requirements

- Windows 10 or later (64-bit)
- Internet connection for downloads
- At least 100MB free disk space for installation
- Additional space for downloaded content

## Usage

1. **Video Downloads**: 
   - Paste any supported social media URL in the Video Downloader tab
   - Click "Download" or press Enter
   - Monitor progress in the download queue

2. **File Downloads**:
   - Paste direct file URLs in the File Downloader tab
   - Support for documents, images, archives, and more

3. **Settings**:
   - Customize download path, quality preferences, and behavior
   - Adjust concurrent download limits
   - Choose appearance theme

## Supported Platforms

- YouTube (videos, playlists, channels)
- Instagram (posts, stories, reels)
- TikTok (videos, profiles)
- Twitter/X (videos, images)
- Facebook (videos, posts)
- And many more...

## Legal Notice

This software is for personal use only. Please respect copyright laws and platform terms of service. Only download content you have permission to download.

## Support

For issues, feature requests, or questions, please visit our support page or contact support.

## Version History

### v1.0.0 (2025)
- Initial release
- Multi-platform download support
- Modern UI with customizable themes
- Concurrent download management
- File download capabilities
"""

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("Created README.md")

def setup_nsis():
    """Download and setup NSIS if not available"""
    nsis_path = Path("nsis")
    makensis_exe = nsis_path / "Bin" / "makensis.exe"
    
    if makensis_exe.exists():
        print("NSIS already available")
        return str(makensis_exe)
    
    print("NSIS not found. Downloading...")
    nsis_url = "https://downloads.sourceforge.net/project/nsis/NSIS%203/3.08/nsis-3.08.zip"
    nsis_zip = "nsis.zip"
    
    if not download_file(nsis_url, nsis_zip, "NSIS"):
        return None
    
    print("Extracting NSIS...")
    try:
        with zipfile.ZipFile(nsis_zip, 'r') as zip_ref:
            zip_ref.extractall(".")
        
        # Find the extracted NSIS directory
        for item in Path(".").iterdir():
            if item.is_dir() and "nsis" in item.name.lower():
                item.rename("nsis")
                break
        
        os.remove(nsis_zip)
        
        if makensis_exe.exists():
            print("NSIS setup complete")
            return str(makensis_exe)
        else:
            print("NSIS extraction failed")
            return None
            
    except Exception as e:
        print(f"Error extracting NSIS: {e}")
        return None

def main():
    print("Social Media Downloader - Complete Build System")
    print("="*60)
    
    # Check if main script exists
    if not Path("test2.py").exists():
        print("Error: test2.py not found!")
        print("Please ensure test2.py is in the current directory.")
        return False
    
    # Create necessary files
    create_license_file()
    create_readme_file()
    
    # Step 1: Install build dependencies
    build_requirements = [
        "pyinstaller>=5.13.0",
        "customtkinter>=5.2.0",
        "yt-dlp>=2023.12.30",
        "requests>=2.31.0",
        "Pillow>=10.0.0",
        "packaging>=21.0"
    ]
    
    print("\nInstalling dependencies...")
    for requirement in build_requirements:
        if not run_command(f'pip install "{requirement}"', 
                         f"Installing {requirement}"):
            return False
    
    # Step 2: Build executable
    print("\nBuilding executable...")
    
    # Clean previous builds
    build_dirs = ["build", "dist", "__pycache__"]
    for dir_name in build_dirs:
        if Path(dir_name).exists():
            print(f"Cleaning {dir_name}...")
            shutil.rmtree(dir_name)
    
    # PyInstaller command
    icon_option = "--icon=icon.ico" if Path("icon.ico").exists() else ""
    version_option = "--version-file=version_info.txt" if Path("version_info.txt").exists() else ""
    
    build_cmd = f"""pyinstaller --onefile --windowed --clean --noconfirm \
        --name SocialMediaDownloader \
        --hidden-import customtkinter \
        --hidden-import yt_dlp \
        --hidden-import requests \
        --hidden-import PIL \
        --hidden-import tkinter \
        --collect-all customtkinter \
        --collect-all yt_dlp \
        {icon_option} \
        {version_option} \
        test2.py"""
    
    if not run_command(build_cmd.replace('\n', ' ').replace('\\', ''), "Building executable with PyInstaller"):
        return False
    
    # Step 3: Verify executable
    exe_path = Path("dist/SocialMediaDownloader.exe")
    if not exe_path.exists():
        print("Error: Executable was not created!")
        return False
    
    file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
    print(f"\nExecutable created successfully!")
    print(f"Location: {exe_path}")
    print(f"Size: {file_size:.1f} MB")
    
    # Step 4: Setup NSIS for installer creation
    print("\nSetting up NSIS for installer creation...")
    makensis_path = setup_nsis()
    
    if not makensis_path:
        print("Warning: Could not setup NSIS. You can install it manually from https://nsis.sourceforge.io/")
        print("The executable is ready in the 'dist' folder.")
        return True
    
    # Step 5: Create installer
    print("\nCreating installer...")
    
    if not Path("installer.nsi").exists():
        print("Error: installer.nsi script not found!")
        print("The executable is ready, but installer creation failed.")
        return False
    
    installer_cmd = f'"{makensis_path}" installer.nsi'
    if not run_command(installer_cmd, "Creating installer with NSIS", critical=False):
        print("Installer creation failed, but executable is available in 'dist' folder.")
        return True
    
    # Step 6: Verify installer
    installer_path = Path("SocialMediaDownloader_Setup.exe")
    if installer_path.exists():
        installer_size = installer_path.stat().st_size / (1024 * 1024)  # MB
        print(f"\n{'='*60}")
        print("BUILD COMPLETED SUCCESSFULLY!")
        print(f"{'='*60}")
        print(f"Executable: dist/SocialMediaDownloader.exe ({file_size:.1f} MB)")
        print(f"Installer: SocialMediaDownloader_Setup.exe ({installer_size:.1f} MB)")
        print("\nWhat you can do now:")
        print("1. Test the executable: dist/SocialMediaDownloader.exe")
        print("2. Distribute the installer: SocialMediaDownloader_Setup.exe")
        print("3. The installer will automatically handle FFmpeg installation")
        return True
    else:
        print("\nExecutable created but installer creation failed.")
        print("You can still use the executable from the 'dist' folder.")
        return True

def create_batch_installer():
    """Create a simple batch file installer as fallback"""
    batch_content = '''@echo off
echo Social Media Downloader - Simple Installer
echo ==========================================
echo.

:: Create installation directory
set "INSTALL_DIR=%PROGRAMFILES%\\Social Media Downloader"
echo Creating installation directory...
mkdir "%INSTALL_DIR%" 2>nul

:: Copy executable
echo Installing application...
copy /Y "dist\\SocialMediaDownloader.exe" "%INSTALL_DIR%\\" >nul
if errorlevel 1 (
    echo Error: Failed to copy executable. Please run as administrator.
    pause
    exit /b 1
)

:: Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Social Media Downloader.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\SocialMediaDownloader.exe'; $Shortcut.Save()"

:: Create start menu shortcut
echo Creating start menu shortcut...
mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Social Media Downloader" 2>nul
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Social Media Downloader\\Social Media Downloader.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\SocialMediaDownloader.exe'; $Shortcut.Save()"

:: Download and install FFmpeg (simplified)
echo.
echo FFmpeg Installation:
echo FFmpeg is required for video processing.
echo Please download it manually from: https://ffmpeg.org/download.html
echo Or install it using: winget install FFmpeg
echo.

echo Installation completed successfully!
echo You can launch Social Media Downloader from:
echo - Desktop shortcut
echo - Start menu
echo - Direct path: %INSTALL_DIR%\\SocialMediaDownloader.exe
echo.
pause
'''
    
    with open("install.bat", "w") as f:
        f.write(batch_content)
    
    print("Created simple batch installer: install.bat")

if __name__ == "__main__":
    success = main()
    
    if success:
        # Create a simple batch installer as backup
        create_batch_installer()
        
        print("\n" + "="*60)
        print("ADDITIONAL OPTIONS:")
        print("="*60)
        print("1. Advanced installer: SocialMediaDownloader_Setup.exe (if created)")
        print("2. Simple installer: install.bat (batch file)")
        print("3. Portable: Just copy dist/SocialMediaDownloader.exe anywhere")
        print("\nNOTE: Users will need to install FFmpeg separately if not using")
        print("the advanced installer. They can:")
        print("- Download from https://ffmpeg.org/")
        print("- Use: winget install FFmpeg")
        print("- Use: choco install ffmpeg")
    
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)