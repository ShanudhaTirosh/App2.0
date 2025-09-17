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