; DocuGen Windows Installer Script (NSIS)
; This installer handles installation, PATH configuration, and API key setup

!include "MUI2.nsh"
!include "FileFunc.nsh"

; Application Info
!define APPNAME "DocuGen"
!define COMPANYNAME "DocuGen"
!define DESCRIPTION "AI-Powered Code Documentation Tool"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://github.com/yourusername/docugen"
!define UPDATEURL "https://github.com/yourusername/docugen/releases"
!define ABOUTURL "https://github.com/yourusername/docugen"

; Installer properties
Name "${APPNAME}"
Icon "docugen.ico"
OutFile "DocuGen-Setup-v${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}.exe"
InstallDir "$PROGRAMFILES64\${APPNAME}"
InstallDirRegKey HKLM "Software\${APPNAME}" "InstallLocation"
RequestExecutionLevel admin

; Modern UI Configuration
!define MUI_ABORTWARNING
!define MUI_ICON "docugen.ico"
!define MUI_UNICON "docugen.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "header.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "welcome.bmp"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY

; Custom API Key Page
Page custom APIKeyPage APIKeyPageLeave

!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

; Variables
Var Dialog
Var APIKeyLabel
Var APIKeyText
Var APIKeyInput
Var APIKeyLink
Var APIKeyValue

; API Key Page
Function APIKeyPage
    !insertmacro MUI_HEADER_TEXT "API Key Configuration" "Enter your Anthropic API key"

    nsDialogs::Create 1018
    Pop $Dialog

    ${If} $Dialog == error
        Abort
    ${EndIf}

    ${NSD_CreateLabel} 0 0 100% 24u "DocuGen requires an Anthropic API key to generate documentation.$\r$\n$\r$\nYou can get your API key from the Anthropic Console:"
    Pop $APIKeyLabel

    ${NSD_CreateLink} 0 28u 100% 12u "https://console.anthropic.com/"
    Pop $APIKeyLink
    ${NSD_OnClick} $APIKeyLink OpenAnthropicConsole

    ${NSD_CreateLabel} 0 48u 100% 12u "Enter your Anthropic API key:"
    Pop $APIKeyText

    ${NSD_CreateText} 0 64u 100% 12u ""
    Pop $APIKeyInput

    ${NSD_CreateLabel} 0 84u 100% 24u "Note: You can skip this step and configure the API key later by:$\r$\n1. Setting the ANTHROPIC_API_KEY environment variable$\r$\n2. Running 'docugen' and following the first-run setup"
    Pop $0

    nsDialogs::Show
FunctionEnd

Function APIKeyPageLeave
    ${NSD_GetText} $APIKeyInput $APIKeyValue
FunctionEnd

Function OpenAnthropicConsole
    ExecShell "open" "https://console.anthropic.com/"
FunctionEnd

; Main Installation Section
Section "Install"
    SetOutPath $INSTDIR

    ; Install the executable
    File "..\..\dist\docugen.exe"

    ; Create uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"

    ; Add to PATH
    EnVar::SetHKLM
    EnVar::AddValue "PATH" "$INSTDIR"

    ; Registry information for Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$INSTDIR\docugen.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1

    ; Get file size for Add/Remove Programs
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" "$0"

    ; Save API key if provided
    ${If} $APIKeyValue != ""
        ; Create config directory
        CreateDirectory "$APPDATA\DocuGen"

        ; Write config file
        FileOpen $0 "$APPDATA\DocuGen\config.json" w
        FileWrite $0 '{"anthropic_api_key": "$APIKeyValue"}'
        FileClose $0

        ; Set restrictive permissions
        AccessControl::SetFileOwner "$APPDATA\DocuGen\config.json" "$USERNAME"
        AccessControl::ClearOnFile "$APPDATA\DocuGen\config.json" "(BU)" "FullAccess"
        AccessControl::GrantOnFile "$APPDATA\DocuGen\config.json" "$USERNAME" "FullAccess"
    ${EndIf}

    ; Create start menu shortcut
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortcut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe"

    ; Show completion message
    MessageBox MB_OK "Installation complete!$\r$\n$\r$\nYou can now use 'docugen' from any command prompt or terminal.$\r$\n$\r$\nExample: docugen myfile.py"
SectionEnd

; Uninstaller Section
Section "Uninstall"
    ; Remove from PATH
    EnVar::SetHKLM
    EnVar::DeleteValue "PATH" "$INSTDIR"

    ; Remove files
    Delete "$INSTDIR\docugen.exe"
    Delete "$INSTDIR\uninstall.exe"
    RMDir "$INSTDIR"

    ; Remove shortcuts
    RMDir /r "$SMPROGRAMS\${APPNAME}"

    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
    DeleteRegKey HKLM "Software\${APPNAME}"

    ; Ask about removing configuration
    MessageBox MB_YESNO "Do you want to remove your DocuGen configuration (API key)?" IDNO SkipConfigRemoval
    RMDir /r "$APPDATA\DocuGen"
    SkipConfigRemoval:
SectionEnd