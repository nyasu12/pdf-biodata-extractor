[Setup]
AppName=GodmodePyInstaller
AppVersion=1.00
AppPublisher=Shota Shimaki
DefaultDirName={autopf64}\GodmodePyInstaller
DefaultGroupName=GodmodePyInstaller
OutputDir=C:\InstallerOutput
OutputBaseFilename=GodmodePySetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
Uninstallable=yes
UninstallDisplayName=GodmodePyInstaller Uninstaller
UninstallFilesDir={app}
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "C:\InstallerFiles\poppler-24.08.0\Library\bin\*"; DestDir: "C:\Program Files\Poppler\bin"; Flags: recursesubdirs createallsubdirs
Source: "C:\InstallerFiles\vision-api-key.json"; DestDir: "{app}\Credentials"
Source: "C:\InstallerFiles\godmode.py"; DestDir: "{app}"
Source: "C:\InstallerFiles\install_libraries.bat"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Dirs]
Name: "C:\temp\GodmodePy\bio_data"; Flags: uninsneveruninstall
Name: "C:\temp\GodmodePy\output"; Flags: uninsneveruninstall
Name: "C:\temp\GodmodePy\output\debug"; Flags: uninsneveruninstall
Name: "C:\Program Files\Poppler"; Flags: uninsneveruninstall
Name: "C:\Program Files\Poppler\bin"; Flags: uninsneveruninstall
Name: "{app}\Credentials"; Flags: uninsneveruninstall

[Icons]
Name: "{autodesktop}\bio_data - Shortcut"; Filename: "C:\temp\GodmodePy\bio_data"; Comment: "Place PDF files here for godmode.py"

[Run]
Filename: "cmd.exe"; Parameters: "/c setx PATH ""C:\Program Files\Poppler\bin;%PATH%"" /M"; StatusMsg: "Setting Poppler PATH..."; Flags: runhidden waituntilterminated
Filename: "cmd.exe"; Parameters: "/c setx GOOGLE_APPLICATION_CREDENTIALS ""{app}\Credentials\vision-api-key.json"" /M"; StatusMsg: "Setting Google Cloud credentials..."; Flags: runhidden waituntilterminated
Filename: "{tmp}\install_libraries.bat"; StatusMsg: "Installing Python libraries..."; Flags: waituntilterminated

[UninstallDelete]
Type: filesandordirs; Name: "C:\Program Files\Poppler"
Type: filesandordirs; Name: "{app}\Credentials"
Type: filesandordirs; Name: "C:\temp\GodmodePy"
Type: files; Name: "{autodesktop}\bio_data - Shortcut.lnk"

[Code]
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Exec('cmd.exe', '/c where python', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  if ResultCode <> 0 then
  begin
    MsgBox('Pythonが見つかりません。Python 3.13をインストールし、システムPATHに追加してください。ダウンロード: https://www.python.org/downloads/', mbCriticalError, MB_OK);
    Result := False;
  end
  else
    Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox('インストールが完了しました！デスクトップにC:\temp\GodmodePy\bio_dataへのショートカットが作成されました。PDFファイルをそこに置き、{app}のgodmode.pyをcmdで実行してください。', mbInformation, MB_OK);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  Path: string;
  NewPath: string;
  I: Integer;
  Parts: array of string;
  PartCount: Integer;
begin
  if CurUninstallStep = usUninstall then
  begin
    if RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'GOOGLE_APPLICATION_CREDENTIALS', Path) then
    begin
      RegDeleteValue(HKEY_LOCAL_MACHINE, 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'GOOGLE_APPLICATION_CREDENTIALS');
    end;

    if RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'Path', Path) then
    begin
      NewPath := '';
      PartCount := 0;
      while Length(Path) > 0 do
      begin
        I := Pos(';', Path);
        if I = 0 then
        begin
          I := Length(Path) + 1;
        end;
        SetArrayLength(Parts, PartCount + 1);
        Parts[PartCount] := Copy(Path, 1, I - 1);
        Delete(Path, 1, I);
        PartCount := PartCount + 1;
      end;

      for I := 0 to PartCount - 1 do
      begin
        if (Parts[I] <> '') and 
           (Uppercase(Parts[I]) <> Uppercase('C:\Program Files\Poppler\bin')) then
        begin
          if NewPath <> '' then
            NewPath := NewPath + ';';
          NewPath := NewPath + Parts[I];
        end;
      end;

      RegWriteStringValue(HKEY_LOCAL_MACHINE, 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'Path', NewPath);
    end;
  end;

  if CurUninstallStep = usDone then
  begin
    MsgBox('アンインストールが完了しました！Pythonとそのライブラリは他のアプリケーションで使用される可能性があるため削除されませんでした。必要に応じて、コントロールパネルまたはhttps://www.python.org/downloads/からPythonをアンインストールしてください。', mbInformation, MB_OK);
  end;
end;
