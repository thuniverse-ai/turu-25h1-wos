#define MyAppName "Turu"
#define MyAppVersion "25H1-WoS"
#define MyAppPublisher "Thuniverse AI"
#define MyAppURL "https://turu.thuniverse.ai/"
#define MyAppIcon "..\..\src\multi-chat\public\images\kuwa-logo.ico"

[Setup]
AppId={{B37EB0AF-B52C-4200-B80F-671FBCE385DC}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName=C:/kuwa/GenAI OS
DefaultGroupName=Kuwa GenAI OS
AllowNoIcons=yes
LicenseFile=../../LICENSE
PrivilegesRequired=lowest
OutputDir=.
OutputBaseFilename=Turu-25H1-WoS-Setup
SetupIconFile={#MyAppIcon}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
DiskSpanning=yes
DiskSliceSize="2000000000"


[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "chinesetraditional"; MessagesFile: "compiler:Languages\ChineseTraditional.isl"
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "czech"; MessagesFile: "compiler:Languages\Czech.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

; Inno Setup supports several languages by default, but Kuwa currently lacks
; translations for these languages. Contributions are welcome.
; Name: "armenian"; MessagesFile: "compiler:Languages\Armenian.isl"
; Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
; Name: "bulgarian"; MessagesFile: "compiler:Languages\Bulgarian.isl"
; Name: "catalan"; MessagesFile: "compiler:Languages\Catalan.isl"
; Name: "corsican"; MessagesFile: "compiler:Languages\Corsican.isl"
; Name: "danish"; MessagesFile: "compiler:Languages\Danish.isl"
; Name: "dutch"; MessagesFile: "compiler:Languages\Dutch.isl"
; Name: "finnish"; MessagesFile: "compiler:Languages\Finnish.isl"
; Name: "hebrew"; MessagesFile: "compiler:Languages\Hebrew.isl"
; Name: "hungarian"; MessagesFile: "compiler:Languages\Hungarian.isl"
; Name: "icelandic"; MessagesFile: "compiler:Languages\Icelandic.isl"
; Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"
; Name: "norwegian"; MessagesFile: "compiler:Languages\Norwegian.isl"
; Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"
; Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"
; Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
; Name: "slovak"; MessagesFile: "compiler:Languages\Slovak.isl"
; Name: "slovenian"; MessagesFile: "compiler:Languages\Slovenian.isl"
; Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
; Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
; Name: "ukrainian"; MessagesFile: "compiler:Languages\Ukrainian.isl"

[Components]
Name: "product"; Description: "Core Components"; Types: full compact custom;Flags: fixed;
Name: "product\Turu"; Description: "Turu"; Types:  full compact custom ;Flags: fixed;

Name: "models"; Description: "On-device AI Models"; Types: full custom;Flags: fixed;
Name: "models\Llama_v3_2_3B_Chat_GENIE"; Description: "Llama-v3.2-3B-Chat-GENIE"; Types: full compact custom; Flags: fixed; ExtraDiskSpaceRequired:2637074432;
Name: "models\TAIDE_LX_8B_Chat_GENIE"; Description: "TAIDE-LX-8B-Chat-GENIE"; Types: full custom; ExtraDiskSpaceRequired:5143891968;
Name: "models\Phi_3_5_Mini_Instruct_GENIE"; Description: "Phi-3.5-Mini-Instruct-GENIE"; Types: full custom; ExtraDiskSpaceRequired:2227830784;
Name: "models\Llama_v3_1_8B_Chat_GENIE"; Description: "Llama-v3.1-8B-Chat-GENIE"; Types: full custom; ExtraDiskSpaceRequired:5131247616;

[Files]
Source: "..\..\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; \
    Excludes: "windows\packages\*,windows\cache\*,windows-setup-files\*.exe,windows-setup-files\*.bin,node_modules\*,vendor\*"; \
    Permissions: users-full; Components: "product\Turu"

Source: "..\..\.git\*"; DestDir: "{app}\.git"; Flags: ignoreversion recursesubdirs createallsubdirs; \
    Permissions: users-full; Components: "product\Turu"

[Icons]
Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "{#MyAppURL}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{group}\Kuwa GenAI OS"; Filename: "{app}\windows\start.bat"; IconFilename: "{app}\src\multi-chat\public\images\kuwa-logo.ico"
Name: "{group}\Construct RAG"; Filename: "{app}\windows\construct_rag.bat"; IconFilename: "{app}\src\multi-chat\public\images\kuwa-logo.ico"
Name: "{group}\Model Download"; Filename: "{app}\windows\executors\download.bat"; IconFilename: "{app}\src\multi-chat\public\images\kuwa-logo.ico"
Name: "{group}\Maintenance Tool"; Filename: "{app}\windows\tool.bat"; IconFilename: "{app}\src\multi-chat\public\images\kuwa-logo.ico"
Name: "{group}\Upgrade Kuwa"; Filename: "{app}\windows\update.bat"; IconFilename: "{app}\src\multi-chat\public\images\kuwa-logo.ico"
Name: "{userdesktop}\Kuwa GenAI OS"; Filename: "{app}\windows\start.bat"; WorkingDir: "{app}\windows"; IconFilename: "{app}\src\multi-chat\public\images\kuwa-logo.ico"
Name: "{userdesktop}\Construct RAG"; Filename: "{app}\windows\construct_rag.bat"; WorkingDir: "{app}\windows"; IconFilename: "{app}\src\multi-chat\public\images\kuwa-logo.ico"

[Run]
Filename: "{app}\windows\start.bat"; Flags: shellexec; Components: "product\Turu"

[Code]
var
  DownloadPage: TDownloadWizardPage;
  AccountPage: TInputQueryWizardPage;
  AutoLoginCheckBox: TNewCheckBox;
  Username, Password, ConfirmPass: String;
  AutoLoginValue: String;

function OnDownloadProgress(const Url, FileName: String; const Progress, ProgressMax: Int64): Boolean;
begin
  if Progress = ProgressMax then
    Log(Format('Successfully downloaded file to {tmp}: %s', [FileName]));
  Result := True;
end;

procedure InitializeWizard;
begin
  AccountPage := CreateInputQueryPage(wpUserInfo,
    'Create Root Account',
    'Please enter account details',
    'Enter an email address and password to create the root account.');

  AccountPage.Add('Email:', False); 
  AccountPage.Add('Password:', True); 
  AccountPage.Add('Confirm Password:', True); 

  AutoLoginCheckBox := TNewCheckBox.Create(WizardForm);
  AutoLoginCheckBox.Parent := AccountPage.Surface;
  AutoLoginCheckBox.Top := AccountPage.Edits[2].Top + AccountPage.Edits[2].Height + 12;
  AutoLoginCheckBox.Left := AccountPage.Edits[2].Left;
  AutoLoginCheckBox.Width := 300;
  AutoLoginCheckBox.Caption := 'Single User Mode';
  AutoLoginCheckBox.Checked := False; 
  DownloadPage := CreateDownloadPage(SetupMessage(msgWizardPreparing), SetupMessage(msgPreparingDesc), @OnDownloadProgress);
  DownloadPage.ShowBaseNameInsteadOfUrl := True;
end;
procedure CurStepChanged(CurStep: TSetupStep);
var
  InitFile: String;
  InitContent: String;
  Email: String;
begin
  if CurStep = ssPostInstall then
  begin
    Email := AccountPage.Values[0];
    Password := AccountPage.Values[1];
    ConfirmPass := AccountPage.Values[2];

    if (Email = '') or (Password = '') or (ConfirmPass = '') then
    begin
      Abort;
    end;
    
    if not (Password = ConfirmPass) then
    begin
      Abort;
    end;

    if AutoLoginCheckBox.Checked then
      AutoLoginValue := 'autologin=true' + #13#10
    else
      AutoLoginValue := 'autologin=false' + #13#10;

    InitContent := 'username=' + Email + #13#10 +
                   'password=' + Password + #13#10 +
                   AutoLoginValue;

    InitFile := ExpandConstant('{app}\windows\init.txt');

    SaveStringToFile(InitFile, InitContent, False);
  end;
end;
function IsValidEmail(strEmail: String): Boolean;
var
  nSpace: Integer;
  nAt: Integer;
begin
  strEmail := Trim(strEmail);
  nSpace := Pos(' ', strEmail);
  nAt := Pos('@', strEmail);

  // Valid if: no spaces, has an '@' not at start or end
  Result := (nSpace = 0) and (nAt > 1) and (nAt < Length(strEmail));
end;
function NextButtonClick(CurPageID: Integer): Boolean;
var InitModels: String;
    InitModelFile: String;
begin
  if CurPageID = wpReady then
  begin
    InitModels := '';
    InitModelFile := ExpandConstant('{app}\windows\src\conf\init_models.txt');
    if WizardIsComponentSelected('models\Llama_v3_2_3B_Chat_GENIE') then
    begin
      InitModels := InitModels + 'thuniverse-ai/Llama-v3.2-3B-Chat-GENIE' + #13#10;
    end;
    if WizardIsComponentSelected('models\Llama_v3_1_8B_Chat_GENIE') then
    begin
      InitModels := InitModels + 'thuniverse-ai/Llama-v3.1-8B-Chat-GENIE' + #13#10;
    end;
    if WizardIsComponentSelected('models\Phi_3_5_Mini_Instruct_GENIE') then
    begin
      InitModels := InitModels + 'thuniverse-ai/Phi-3.5-Mini-Instruct-GENIE' + #13#10;
    end;
    if WizardIsComponentSelected('models\TAIDE_LX_8B_Chat_GENIE') then
    begin
      InitModels := InitModels + 'thuniverse-ai/TAIDE-LX-8B-Chat-GENIE' + #13#10;
    end;
    ForceDirectories(ExtractFilePath(InitModelFile));
    SaveStringToFile(InitModelFile, InitModels, False);
    Result := True;
  end
  else if CurPageID = AccountPage.ID then
  begin
    Username := AccountPage.Values[0];
    Password := AccountPage.Values[1];
    ConfirmPass := AccountPage.Values[2];

    Result := True; // Default to True, set to False if validation fails

    if (Username = '') or (Password = '') then
    begin
      MsgBox('Both username and password are required.', mbError, MB_OK);
      Result := False;
    end;

    if ConfirmPass = '' then
    begin
      MsgBox('Please confirm your password.', mbError, MB_OK);
      Result := False;
    end
    else if ConfirmPass <> Password then
    begin
      MsgBox('Passwords do not match.', mbError, MB_OK);
      Result := False;
    end;

    if not IsValidEmail(Username) then
    begin
      MsgBox('Please enter a valid email address.', mbError, MB_OK);
      Result := False;
    end;
  end
  else
    Result := True;
end;
