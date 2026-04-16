#define AppName "JSON View"
#define AppVersion "0.1.0"
#define AppPublisher "xxmelar-ksaxx"
#define AppExeName "JSON View.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
AppId={{FD5F3D1C-D63C-4328-87C7-9D8CF2A9B932}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DisableProgramGroupPage=yes
; Output path and filename
OutputDir=dist
OutputBaseFilename=json-view-setup-v{#AppVersion}
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; Require admin if installing to Program Files and writing to HKLM registry
PrivilegesRequired=admin
ChangesAssociations=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "defaultapp"; Description: "Set {#AppName} as the default app for .json files"; GroupDescription: "File Associations:"
Name: "contextmenu_json"; Description: "Add ''Open with {#AppName}'' to .json files context menu"; GroupDescription: "File Associations:"
Name: "contextmenu_all"; Description: "Add ''Open with {#AppName}'' to all files context menu"; GroupDescription: "File Associations:"; Flags: unchecked

[Files]
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.png"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Registry]
; 1. Register the application
Root: HKLM; Subkey: "SOFTWARE\Classes\Applications\{#AppExeName}"; ValueType: string; ValueName: ""; ValueData: "{#AppName}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\Classes\Applications\{#AppExeName}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"" ""%1"""

; 2. Register file type & default app (Tasks: defaultapp)
Root: HKLM; Subkey: "SOFTWARE\Classes\.json"; ValueType: string; ValueName: ""; ValueData: "JSONView.JsonFile"; Flags: uninsdeletevalue; Tasks: defaultapp
Root: HKLM; Subkey: "SOFTWARE\Classes\JSONView.JsonFile"; ValueType: string; ValueName: ""; ValueData: "JSON File"; Flags: uninsdeletekey; Tasks: defaultapp
Root: HKLM; Subkey: "SOFTWARE\Classes\JSONView.JsonFile\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"",0"; Tasks: defaultapp
Root: HKLM; Subkey: "SOFTWARE\Classes\JSONView.JsonFile\shell\open"; ValueType: string; ValueName: ""; ValueData: "Open with {#AppName}"; Tasks: defaultapp
Root: HKLM; Subkey: "SOFTWARE\Classes\JSONView.JsonFile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"" ""%1"""; Tasks: defaultapp

; 3. Add to right-click context menu for .json files (Tasks: contextmenu_json)
Root: HKLM; Subkey: "SOFTWARE\Classes\SystemFileAssociations\.json\shell\OpenWithJSONView"; ValueType: string; ValueName: ""; ValueData: "Open with {#AppName}"; Flags: uninsdeletekey; Tasks: contextmenu_json
Root: HKLM; Subkey: "SOFTWARE\Classes\SystemFileAssociations\.json\shell\OpenWithJSONView"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\{#AppExeName}"",0"; Tasks: contextmenu_json
Root: HKLM; Subkey: "SOFTWARE\Classes\SystemFileAssociations\.json\shell\OpenWithJSONView\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"" ""%1"""; Tasks: contextmenu_json

; 4. Add general right-click option for all files (Tasks: contextmenu_all)
Root: HKLM; Subkey: "SOFTWARE\Classes\*\shell\OpenWithJSONView"; ValueType: string; ValueName: ""; ValueData: "Open with {#AppName}"; Flags: uninsdeletekey; Tasks: contextmenu_all
Root: HKLM; Subkey: "SOFTWARE\Classes\*\shell\OpenWithJSONView"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\{#AppExeName}"",0"; Tasks: contextmenu_all
Root: HKLM; Subkey: "SOFTWARE\Classes\*\shell\OpenWithJSONView\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"" ""%1"""; Tasks: contextmenu_all
