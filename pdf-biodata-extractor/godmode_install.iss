#define MyAppName "PDF BioData Extractor"
#define MyAppVersion "3.00"
#define MyAppPublisher "PDF BioData Extractor"

#ifndef ExeSource
  #define ExeSource "dist\godmode.exe"
#endif
#ifndef ProfilesSource
  #define ProfilesSource "profiles\*"
#endif
#ifndef PopplerBinSource
  #define PopplerBinSource "vendor\poppler\Library\bin\*"
#endif
#ifndef InstallerOutputDir
  #define InstallerOutputDir "installer_output"
#endif

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf64}\PDFBioDataExtractor
DefaultGroupName={#MyAppName}
OutputDir={#InstallerOutputDir}
OutputBaseFilename=PDFBioDataExtractorSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
Uninstallable=yes
UninstallDisplayName={#MyAppName} Uninstaller
UninstallFilesDir={app}
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "{#ExeSource}"; DestDir: "{app}"
Source: "{#ProfilesSource}"; DestDir: "{app}\profiles"; Flags: recursesubdirs createallsubdirs
Source: "{#PopplerBinSource}"; DestDir: "{app}\poppler\bin"; Flags: recursesubdirs createallsubdirs

[Dirs]
Name: "{app}\Credentials"; Flags: uninsneveruninstall
Name: "C:\temp\GodmodePy\bio_data"; Flags: uninsneveruninstall
Name: "C:\temp\GodmodePy\output"; Flags: uninsneveruninstall
Name: "C:\temp\GodmodePy\output\debug"; Flags: uninsneveruninstall

[Icons]
Name: "{autodesktop}\PDF BioData Credentials"; Filename: "{app}\Credentials"
Name: "{autodesktop}\PDF BioData Input"; Filename: "C:\temp\GodmodePy\bio_data"

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox('Installation completed. Place config.json and Google Vision credentials inside the Credentials folder.', mbInformation, MB_OK);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usDone then
  begin
    MsgBox('Uninstall completed.', mbInformation, MB_OK);
  end;
end;
