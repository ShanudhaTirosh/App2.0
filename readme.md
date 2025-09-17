I'll help you create an executable and installer for your Social Media Downloader application. This involves several steps: creating the .exe file, handling dependencies, and creating a proper installer.

customtkinter>=5.2.0
yt-dlp>=2023.12.30
requests>=2.31.0
Pillow>=10.0.0
packaging>=21.0

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['test2.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include customtkinter assets
        ('venv/Lib/site-packages/customtkinter', 'customtkinter/'),
        # Include yt-dlp data files if any
        ('venv/Lib/site-packages/yt_dlp', 'yt_dlp/'),
    ],
    hiddenimports=[
        'customtkinter',
        'yt_dlp',
        'requests',
        'PIL',
        'tkinter',
        'threading',
        'json',
        'os',
        'urllib.parse',
        'pathlib',
        'queue',
        'subprocess',
        'platform',
        'time',
        're',
        # yt-dlp extractors
        'yt_dlp.extractor',
        'yt_dlp.extractor.youtube',
        'yt_dlp.extractor.instagram',
        'yt_dlp.extractor.tiktok',
        'yt_dlp.extractor.twitter',
        'yt_dlp.extractor.facebook',
        # Additional imports that might be missed
        'yt_dlp.utils',
        'yt_dlp.downloader',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SocialMediaDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # Add your icon file here
    version='version_info.txt'  # Add version info
)

# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x4,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Your Company Name'),
        StringStruct(u'FileDescription', u'Social Media Downloader - Download videos and files from social media platforms'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'SocialMediaDownloader'),
        StringStruct(u'LegalCopyright', u'Copyright (C) 2025 Your Company Name'),
        StringStruct(u'OriginalFilename', u'SocialMediaDownloader.exe'),
        StringStruct(u'ProductName', u'Social Media Downloader'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)

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

Now I'll create the installer script and additional files for creating a professional installer:

;NSIS Installer Script for Social Media Downloader
;Requires NSIS 3.0 or later

!define APP_NAME "Social Media Downloader"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "Your Company Name"
!define APP_URL "https://yourwebsite.com"
!define APP_EXE "SocialMediaDownloader.exe"
!define APP_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
!define APP_UNINST_ROOT_KEY "HKLM"

; Modern UI
!include "MUI2.nsh"
!include "FileFunc.nsh"

; General settings
Name "${APP_NAME}"
OutFile "SocialMediaDownloader_Setup.exe"
InstallDir "$PROGRAMFILES64\${APP_NAME}"
InstallDirRegKey HKLM "Software\${APP_NAME}" "InstallPath"
ShowInstDetails show
ShowUnInstDetails show

; Request admin privileges
RequestExecutionLevel admin

; Version information
VIProductVersion "${APP_VERSION}.0"
VIAddVersionKey "ProductName" "${APP_NAME}"
VIAddVersionKey "CompanyName" "${APP_PUBLISHER}"
VIAddVersionKey "LegalCopyright" "© 2025 ${APP_PUBLISHER}"
VIAddVersionKey "FileDescription" "${APP_NAME} Installer"
VIAddVersionKey "FileVersion" "${APP_VERSION}.0"
VIAddVersionKey "ProductVersion" "${APP_VERSION}.0"

; Modern UI settings
!define MUI_ABORTWARNING
!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "header.bmp" ; 150x57 pixels
!define MUI_WELCOMEFINISHPAGE_BITMAP "welcome.bmp" ; 164x314 pixels

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\${APP_EXE}"
!define MUI_FINISHPAGE_RUN_TEXT "Launch ${APP_NAME}"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installer sections
Section "Core Application" SecCore
    SectionIn RO ; Required section
    
    ; Set output path
    SetOutPath "$INSTDIR"
    
    ; Copy main executable
    File "dist\${APP_EXE}"
    
    ; Copy additional files if they exist
    IfFileExists "README.md" 0 +2
    File "README.md"
    
    IfFileExists "LICENSE.txt" 0 +2
    File "LICENSE.txt"
    
    ; Create application data directory
    CreateDirectory "$APPDATA\${APP_NAME}"
    
    ; Write uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Registry entries
    WriteRegStr HKLM "Software\${APP_NAME}" "InstallPath" "$INSTDIR"
    WriteRegStr HKLM "Software\${APP_NAME}" "Version" "${APP_VERSION}"
    
    ; Add/Remove Programs registry entries
    WriteRegStr ${APP_UNINST_ROOT_KEY} "${APP_UNINST_KEY}" "DisplayName" "${APP_NAME}"
    WriteRegStr ${APP_UNINST_ROOT_KEY} "${APP_UNINST_KEY}" "DisplayVersion" "${APP_VERSION}"
    WriteRegStr ${APP_UNINST_ROOT_KEY} "${APP_UNINST_KEY}" "Publisher" "${APP_PUBLISHER}"
    WriteRegStr ${APP_UNINST_ROOT_KEY} "${APP_UNINST_KEY}" "URLInfoAbout" "${APP_URL}"
    WriteRegStr ${APP_UNINST_ROOT_KEY} "${APP_UNINST_KEY}" "DisplayIcon" "$INSTDIR\${APP_EXE}"
    WriteRegStr ${APP_UNINST_ROOT_KEY} "${APP_UNINST_KEY}" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr ${APP_UNINST_ROOT_KEY} "${APP_UNINST_KEY}" "QuietUninstallString" "$INSTDIR\Uninstall.exe /S"
    WriteRegDWORD ${APP_UNINST_ROOT_KEY} "${APP_UNINST_KEY}" "NoModify" 1
    WriteRegDWORD ${APP_UNINST_ROOT_KEY} "${APP_UNINST_KEY}" "NoRepair" 1
    
    ; Get size
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD ${APP_UNINST_ROOT_KEY} "${APP_UNINST_KEY}" "EstimatedSize" "$0"
    
SectionEnd

Section "Desktop Shortcut" SecDesktop
    CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_EXE}" 0
SectionEnd

Section "Start Menu Shortcuts" SecStartMenu
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_EXE}" 0
    CreateShortcut "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0
SectionEnd

Section "FFmpeg (Required for video processing)" SecFFmpeg
    ; Download and install FFmpeg
    DetailPrint "Downloading FFmpeg..."
    
    ; Create temp directory
    CreateDirectory "$TEMP\${APP_NAME}_setup"
    
    ; Download FFmpeg (you can host your own or use a reliable mirror)
    NSISdl::download "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip" "$TEMP\${APP_NAME}_setup\ffmpeg.zip"
    Pop $R0
    StrCmp $R0 "success" +3
    MessageBox MB_OK "Failed to download FFmpeg. You can download it manually later."
    Goto ffmpeg_done
    
    ; Extract FFmpeg
    DetailPrint "Installing FFmpeg..."
    nsisunz::UnzipToLog "$TEMP\${APP_NAME}_setup\ffmpeg.zip" "$TEMP\${APP_NAME}_setup"
    
    ; Find the ffmpeg.exe in the extracted folder
    FindFirst $0 $1 "$TEMP\${APP_NAME}_setup\ffmpeg-*\bin\ffmpeg.exe"
    StrCmp $1 "" ffmpeg_not_found
    
    ; Copy ffmpeg to installation directory
    CreateDirectory "$INSTDIR\ffmpeg"
    CopyFiles "$TEMP\${APP_NAME}_setup\ffmpeg-*\bin\*.*" "$INSTDIR\ffmpeg\"
    
    ; Add to PATH
    EnVar::SetHKLM
    EnVar::AddValue "PATH" "$INSTDIR\ffmpeg"
    Pop $0
    
    ffmpeg_not_found:
    FindClose $0
    
    ffmpeg_done:
    ; Cleanup
    RMDir /r "$TEMP\${APP_NAME}_setup"
    
SectionEnd

Section "File Associations" SecAssociations
    ; Register for common video URLs (optional)
    ; This is a basic example - full implementation would be more complex
    WriteRegStr HKCR "http\shell\${APP_NAME}" "" "Download with ${APP_NAME}"
    WriteRegStr HKCR "http\shell\${APP_NAME}\command" "" '"$INSTDIR\${APP_EXE}" "%1"'
    WriteRegStr HKCR "https\shell\${APP_NAME}" "" "Download with ${APP_NAME}"
    WriteRegStr HKCR "https\shell\${APP_NAME}\command" "" '"$INSTDIR\${APP_EXE}" "%1"'
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${SecCore} "Core application files (required)"
!insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} "Create a desktop shortcut"
!insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} "Create Start Menu shortcuts"
!insertmacro MUI_DESCRIPTION_TEXT ${SecFFmpeg} "Download and install FFmpeg for video processing"
!insertmacro MUI_DESCRIPTION_TEXT ${SecAssociations} "Register file associations for easy downloading"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller section
Section "Uninstall"
    ; Remove files
    Delete "$INSTDIR\${APP_EXE}"
    Delete "$INSTDIR\Uninstall.exe"
    Delete "$INSTDIR\README.md"
    Delete "$INSTDIR\LICENSE.txt"
    RMDir /r "$INSTDIR\ffmpeg"
    
    ; Remove shortcuts
    Delete "$DESKTOP\${APP_NAME}.lnk"
    RMDir /r "$SMPROGRAMS\${APP_NAME}"
    
    ; Remove registry entries
    DeleteRegKey ${APP_UNINST_ROOT_KEY} "${APP_UNINST_KEY}"
    DeleteRegKey HKLM "Software\${APP_NAME}"
    
    ; Remove file associations
    DeleteRegKey HKCR "http\shell\${APP_NAME}"
    DeleteRegKey HKCR "https\shell\${APP_NAME}"
    
    ; Remove from PATH
    EnVar::SetHKLM
    EnVar::DeleteValue "PATH" "$INSTDIR\ffmpeg"
    Pop $0
    
    ; Remove installation directory
    RMDir "$INSTDIR"
    
    ; Remove application data (ask user first)
    MessageBox MB_YESNO|MB_ICONQUESTION "Do you want to remove all application data and settings?" IDNO +2
    RMDir /r "$APPDATA\${APP_NAME}"
    
SectionEnd

Now let me create a comprehensive build script and additional files:

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
        --add-data "venv/Lib/site-packages/
        
        


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

Now let me create some additional helpful files:

# Social Media Downloader - Build Instructions

This guide will help you create both an executable (.exe) and installer for the Social Media Downloader application.

## Prerequisites

1. **Python 3.8+** installed on Windows
2. **Git** (optional, for version control)
3. **Administrative privileges** (for some build steps)

## Quick Start

1. **Clone or download all files** to a directory
2. **Run the complete build script**:
   ```bash
   python build_installer.py
   ```

This single command will:
- Install all dependencies
- Create the executable
- Download NSIS (if needed)
- Create the installer
- Handle FFmpeg integration

## Manual Step-by-Step Process

If you prefer to build manually or troubleshoot issues:

### Step 1: Prepare Environment

```bash
# Install build dependencies
pip install -r requirements.txt
pip install pyinstaller>=5.13.0

# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Build Executable

```bash
# Option A: Use the build script
python build_executable.py

# Option B: Manual PyInstaller command
pyinstaller social_downloader.spec --clean --noconfirm
```

### Step 3: Test Executable

```bash
# Test the created executable
dist\SocialMediaDownloader.exe
```

### Step 4: Create Installer

```bash
# Install NSIS from https://nsis.sourceforge.io/ (if not using auto-download)
# Then run:
makensis installer.nsi
```

## File Structure

Your directory should contain:
```
├── test2.py                    # Main application file
├── requirements.txt            # Python dependencies
├── social_downloader.spec      # PyInstaller configuration
├── version_info.txt            # Version information for executable
├── installer.nsi               # NSIS installer script
├── build_executable.py         # Executable build script
├── build_installer.py          # Complete build script
├── BUILD_INSTRUCTIONS.md       # This file
├── icon.ico                    # Application icon (optional)
├── LICENSE.txt                 # License file (auto-generated)
└── README.md                   # Documentation (auto-generated)
```

## Output Files

After successful build:

### Executable Only
- `dist/SocialMediaDownloader.exe` - Standalone executable (~50-80MB)

### Full Installer Package
- `SocialMediaDownloader_Setup.exe` - Complete installer (~60-100MB)
- Includes FFmpeg auto-download
- Creates desktop/start menu shortcuts
- Handles Windows registry entries
- Includes uninstaller

### Fallback Options
- `install.bat` - Simple batch installer
- Portable executable (just copy .exe file)

## Troubleshooting

### Common Issues

1. **"Module not found" errors during build**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Use `--collect-all` flags in PyInstaller for problematic modules

2. **Large executable size**
   - Normal for bundled applications (50-80MB expected)
   - Use `--exclude-module` to remove unused modules if needed

3. **FFmpeg not found errors**
   - The installer handles FFmpeg automatically
   - Manual install: Download from https://ffmpeg.org/
   - Or use: `winget install FFmpeg`

4. **NSIS errors**
   - Ensure NSIS 3.x is installed
   - The build script can auto-download NSIS
   - Check installer.nsi syntax if modified

5. **Antivirus false positives**
   - Common with PyInstaller executables
   - Submit to antivirus vendors for whitelisting
   - Code signing helps (requires certificate)

### Build Environment Issues

**Windows Defender/Antivirus**
- Temporarily disable real-time protection during build
- Add build directory to exclusions

**Path Issues**
- Use full paths in commands if relative paths fail
- Ensure Python and pip are in system PATH

**Permission Issues**
- Run command prompt as Administrator
- Ensure write permissions to build directory

## Advanced Options

### Custom Icon
- Create/download an `icon.ico` file (48x48 recommended)
- Place in root directory before building

### Code Signing
- Purchase code signing certificate
- Use `signtool` to sign the executable:
  ```bash
  signtool sign /f certificate.p12 /p password /t http://timestamp.server dist\SocialMediaDownloader.exe
  ```

### Custom Installer Options
- Edit `installer.nsi` to modify installer behavior
- Add custom pages, registry entries, or file associations
- Include additional dependencies or files

### Distribution
- Test installer on clean Windows systems
- Consider creating portable version (just .exe file)
- Upload to download servers or create update mechanism

## Dependencies Explained

### Runtime Dependencies (included in exe)
- `customtkinter` - Modern UI framework
- `yt-dlp` - Video download engine
- `requests` - HTTP requests
- `Pillow` - Image processing

### Build Dependencies (not included in exe)
- `pyinstaller` - Creates executable
- `NSIS` - Creates installer (auto-downloaded)

### External Dependencies (handled by installer)
- `FFmpeg` - Video/audio processing (auto-downloaded)

## Performance Notes

- First launch may be slower (extraction)
- Executable size is normal for bundled Python apps
- Consider creating update mechanism for future versions
- Installer handles PATH modifications and file associations

## Legal Considerations

- Respect platform terms of service
- Include appropriate licenses
- Consider copyright implications
- User responsibility for downloaded content

## Support and Updates

- Test thoroughly before distribution
- Create documentation for end users
- Consider automatic update mechanism
- Provide support contact information

Finally, let me create a simple batch file to handle the entire build process:

@echo off
setlocal

echo ================================================================
echo Social Media Downloader - Complete Build System
echo ================================================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found in PATH
    echo Please install Python 3.8+ and add it to your PATH
    echo Download from: https://python.org/downloads/
    pause
    exit /b 1
)

:: Check if main script exists
if not exist "test2.py" (
    echo Error: test2.py not found in current directory
    echo Please ensure all files are in the same folder
    pause
    exit /b 1
)

echo Found Python installation
echo Main script: test2.py found
echo.

:: Create virtual environment (optional but recommended)
echo Creating virtual environment...
python -m venv build_env
call build_env\Scripts\activate.bat

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install requirements
echo Installing build requirements...
pip install pyinstaller>=5.13.0
pip install customtkinter>=5.2.0
pip install yt-dlp>=2023.12.30
pip install requests>=2.31.0
pip install Pillow>=10.0.0
pip install packaging>=21.0

if errorlevel 1 (
    echo Error installing requirements
    pause
    exit /b 1
)

:: Run the complete build script
echo.
echo ================================================================
echo Running complete build process...
echo ================================================================
python build_installer.py

if errorlevel 1 (
    echo Build process failed
    pause
    exit /b 1
)

:: Deactivate virtual environment
call deactivate

echo.
echo ================================================================
echo Build process completed!
echo ================================================================
echo.

:: Show results
if exist "dist\SocialMediaDownloader.exe" (
    echo ✓ Executable created: dist\SocialMediaDownloader.exe
    for %%I in ("dist\SocialMediaDownloader.exe") do echo   Size: %%~zI bytes
)

if exist "SocialMediaDownloader_Setup.exe" (
    echo ✓ Installer created: SocialMediaDownloader_Setup.exe
    for %%I in ("SocialMediaDownloader_Setup.exe") do echo   Size: %%~zI bytes
)

if exist "install.bat" (
    echo ✓ Simple installer: install.bat
)

echo.
echo What to do next:
echo 1. Test the executable: dist\SocialMediaDownloader.exe
echo 2. Distribute the installer: SocialMediaDownloader_Setup.exe
echo 3. Or use the simple installer: install.bat
echo.

pause

I've created a complete build system for your Social Media Downloader application. Here's what you now have:

## Complete Build System Files:

1. **requirements.txt** - All Python dependencies
2. **social_downloader.spec** - PyInstaller configuration with all necessary settings
3. **version_info.txt** - Version information for the executable
4. **build_executable.py** - Script to create just the .exe file
5. **installer.nsi** - Professional NSIS installer script with FFmpeg auto-download
6. **build_installer.py** - Complete automated build script
7. **build_all.bat** - Simple batch file to run everything
8. **BUILD_INSTRUCTIONS.md** - Comprehensive documentation

## Usage Options:

### Option 1: One-Click Build (Easiest)
```bash
build_all.bat
```
This will handle everything automatically.

### Option 2: Python Script
```bash
python build_installer.py
```

### Option 3: Just the executable
```bash
python build_executable.py
```

## What the system does:

1. **Creates a professional executable** (~50-80MB) with:
   - All dependencies bundled
   - Windows version info
   - Custom icon support
   - No console window

2. **Builds a complete installer** that:
   - Auto-downloads and installs FFmpeg
   - Creates desktop and start menu shortcuts
   - Adds to Windows Add/Remove Programs
   - Handles PATH environment variables
   - Includes uninstaller

3. **Handles all dependencies**:
   - Python packages (bundled in exe)
   - FFmpeg (downloaded by installer)
   - NSIS (auto-downloaded if needed)

## Key Features:

- **Automatic FFmpeg handling** - The installer downloads FFmpeg and adds it to PATH
- **Professional installer** - Proper Windows integration with uninstaller
- **Error handling** - Comprehensive error checking and recovery
- **Multiple distribution options** - Full installer, simple installer, or portable exe
- **User-friendly** - Clear progress indicators and instructions

The system addresses common PyInstaller issues like missing modules, handles the complex FFmpeg dependency automatically, and creates a distribution-ready installer that end users can run without technical knowledge.

Just run `build_all.bat` and you'll get both the executable and installer ready for distribution!