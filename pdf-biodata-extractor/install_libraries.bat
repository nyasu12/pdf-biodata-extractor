@echo off
:: コマンドプロンプトのエンコーディングをUTF-8に変更
chcp 65001 >nul

echo Pythonライブラリをインストールしています...


where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo エラー: Pythonが見つかりません。Pythonがインストールされているか、システムPATHに追加されているか確認してください。
    echo 推奨: Python 3.13をhttps://www.python.org/downloads/からインストールし、"Add Python to PATH"を有効にしてください。
    pause
    exit /b 1
)


python --version | findstr "3.13" >nul
if %ERRORLEVEL% neq 0 (
    echo 警告: Python 3.13が必要です。現在のバージョンが異なる場合、動作しない可能性があります。
)


echo pandasをインストールしています...
python -m pip install pandas
if %ERRORLEVEL% neq 0 (
    echo エラー: pandasのインストールに失敗しました。
    pause
    exit /b 1
)

echo google-cloud-visionをインストールしています...
python -m pip install google-cloud-vision
if %ERRORLEVEL% neq 0 (
    echo エラー: google-cloud-visionのインストールに失敗しました。
    pause
    exit /b 1
)

echo pdf2imageをインストールしています...
python -m pip install pdf2image
if %ERRORLEVEL% neq 0 (
    echo エラー: pdf2imageのインストールに失敗しました。
    pause
    exit /b 1
)

echo openpyxlをインストールしています...
python -m pip install openpyxl
if %ERRORLEVEL% neq 0 (
    echo エラー: openpyxlのインストールに失敗しました。
    pause
    exit /b 1
)
echo openai==0.28 をインストールしています...
python -m pip install openai==0.28
if %ERRORLEVEL% neq 0 (
    echo エラー: openaiのインストールに失敗しました。
    pause
    exit /b 1
)


echo ライブラリインストールが完了しました！
pause
exit /b 0
