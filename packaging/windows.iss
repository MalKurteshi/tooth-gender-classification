#define AppName "Tooth Gender Classification"
#define AppVersion "2.2.0"
[Setup]
AppId={{CF475B21-994E-431D-96F8-B232784FD59F}
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={localappdata}\Programs\ToothGenderClassification
DefaultGroupName={#AppName}
PrivilegesRequired=lowest
OutputDir=..\dist
OutputBaseFilename=ToothGenderClassification-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=..\assets\tooth_icon.ico
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\ToothGenderClassification.exe
CloseApplications=yes
[Files]
Source: "..\dist\ToothGenderClassification\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{userdesktop}\{#AppName}"; Filename: "{app}\ToothGenderClassification.exe"; IconFilename: "{app}\ToothGenderClassification.exe"; IconIndex: 0
Name: "{userprograms}\{#AppName}"; Filename: "{app}\ToothGenderClassification.exe"; IconFilename: "{app}\ToothGenderClassification.exe"; IconIndex: 0
[Run]
Filename: "{app}\ToothGenderClassification.exe"; Description: "Open {#AppName}"; Flags: nowait postinstall skipifsilent
