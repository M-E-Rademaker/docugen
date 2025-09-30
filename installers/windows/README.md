# Windows Installer Build

The Windows installer is built automatically by GitHub Actions.

## Placeholder Files

The following placeholder files are created automatically during the GitHub Actions build:
- `docugen.ico` - Application icon
- `header.bmp` - Installer header image
- `welcome.bmp` - Welcome screen image

## Manual Build (Windows only)

If you want to build the installer manually on Windows:

1. Install NSIS from https://nsis.sourceforge.io/Download
2. Build the binary: `pyinstaller docugen.spec`
3. Create placeholder images (or use real ones)
4. Run: `makensis installers/windows/installer.nsi`

## Output

The installer will be created as: `DocuGen-Setup-v1.0.0.exe`