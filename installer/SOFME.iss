; Inno Setup Script for SOFME
; Professional installer for Windows

[Setup]
AppName=SOFME
AppVersion=1.0.0
AppPublisher=SOFME
AppPublisherURL=https://example.com
AppSupportURL=https://example.com
AppUpdatesURL=https://example.com
DefaultDirName={autopf}\SOFME
DefaultGroupName=SOFME
Compression=lzma2
SolidCompression=yes
OutputBaseFilename=SOFME_Setup
OutputDir=.
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
CreateAppDir=yes
AllowNoIcons=yes
SetupIconFile=..\app\images\icon.png
UninstallDisplayIcon={app}\SOFME.exe
ChangesEnvironment=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: checkedonce
Name: "startmenuicon"; Description: "Create a &Start menu shortcut"; GroupDescription: "Additional icons:"; Flags: checkedonce

[Files]
Source: "..\dist\SOFME\SOFME.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\SOFME\*.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\SOFME\*.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\SOFME\*.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\SOFME\*.zip"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\SOFME\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\app\images\*"; DestDir: "{app}\assets\images"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\local_params.txt"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{app}\Dados"
Name: "{app}\logs"

[Icons]
Name: "{group}\SOFME"; Filename: "{app}\SOFME.exe"
Name: "{commondesktop}\SOFME"; Filename: "{app}\SOFME.exe"; Tasks: desktopicon
Name: "{commonstartmenu}\SOFME"; Filename: "{app}\SOFME.exe"; Tasks: startmenuicon

[Run]
Filename: "{app}\SOFME.exe"; Description: "Launch SOFME"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{sys}\cmd.exe"; Parameters: "/c echo SOFME desinstalado"; Flags: waituntilterminated

[UninstallDelete]
Type: filesandordirs; Name: "{app}\Dados"

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
