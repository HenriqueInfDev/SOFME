; Inno Setup script template for SOFME
; To compile: install Inno Setup and run: ISCC.exe SOFME_installer.iss

[Setup]
AppName=SOFME
AppVersion=1.0
DefaultDirName={pf}\SOFME
DefaultGroupName=SOFME
DisableProgramGroupPage=yes
OutputDir=..
OutputBaseFilename=SOFME_Installer
Compression=lzma
SolidCompression=yes

[Files]
; Include all files from dist\SOFME
Source: "{#SourcePath}\*"; DestDir: "{app}"; Flags: recursedirectories createallsubdirs

[Icons]
Name: "{group}\SOFME"; Filename: "{app}\SOFME.exe"
Name: "{userdesktop}\SOFME"; Filename: "{app}\SOFME.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SOFME.exe"; Description: "Iniciar SOFME"; Flags: nowait postinstall skipifsilent

; Replace {#SourcePath} below before compiling or set it via preprocessor

; Example command to compile (after installing Inno Setup):
; ISCC.exe /DSourcePath="C:\path\to\SOFME\dist\SOFME" SOFME_installer.iss
