@echo off
cd /d "%~dp0"

if not exist venv\Scripts\activate.bat (
    echo Nao encontrei a pasta venv nesse local.
    echo Verifique se o arquivo executar.bat esta na pasta certa do projeto.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

python main.py

pause