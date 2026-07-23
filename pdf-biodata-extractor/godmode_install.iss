[Setup]
AppName=PDF BioData Extractor
AppVersion=2.00
AppPublisher=Shota Shimaki
DefaultDirName={autopf64}\GodmodePyInstaller
DefaultGroupName=GodmodePyInstaller
OutputDir=C:\InstallerOutput
OutputBaseFilename=PDFBioDataExtractorSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
Uninstallable=yes
UninstallDisplayName=PDF BioData Extractor Uninstaller
UninstallFilesDir={app}
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "C:\InstallerFiles\poppler-24.08.0\Library\bin\*"; DestDir: "C:\Program Files\Poppler\bin"; Flags: recursesubdirs createallsubdirs
Source: "C:\InstallerFiles\dist\godmode.exe"; DestDir: "{app}"

[Dirs]
Name: "{app}\Credentials"; Flags: uninsneveruninstall
Name: "C:\temp\GodmodePy\bio_data"; Flags: uninsneveruninstall
Name: "C:\temp\GodmodePy\output"; Flags: uninsneveruninstall
Name: "C:\temp\GodmodePy\output\debug"; Flags: uninsneveruninstall
Name: "C:\Program Files\Poppler"; Flags: uninsneveruninstall
Name: "C:\Program Files\Poppler\bin"; Flags: uninsneveruninstall

[Icons]
Name: "{autodesktop}\Credentials - Shortcut"; Filename: "{app}\Credentials"
Name: "{autodesktop}\bio_data - Shortcut"; Filename: "C:\temp\GodmodePy\bio_data"

[Run]
Filename: "cmd.exe"; Parameters: "/c setx PATH ""C:\Program Files\Poppler\bin;%PATH%"" /M"; Flags: runhidden waituntilterminated

[UninstallDelete]
Type: filesandordirs; Name: "{app}\Credentials"
Type: filesandordirs; Name: "C:\temp\GodmodePy"
Type: filesandordirs; Name: "C:\Program Files\Poppler"
Type: files; Name: "{autodesktop}\Credentials - Shortcut.lnk"
Type: files; Name: "{autodesktop}\bio_data - Shortcut.lnk"

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox('Installation completed. Place your API keys inside the Credentials folder.', mbInformation, MB_OK);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usDone then
  begin
    MsgBox('Uninstall completed.', mbInformation, MB_OK);
  end;
end;
