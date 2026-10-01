@echo off
echo ============================================
echo Instalando Cadastro Automatico de Bobinas
echo ============================================

REM Cria o ambiente virtual, se ainda nao existir
if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Instalando dependencias Python...
pip install --upgrade pip
pip install -r requirements.txt

echo Instalando navegador do Playwright (Chromium)...
python -m playwright install chromium

echo.
echo ============================================
echo Instalacao concluida!
echo Use o arquivo "executar.bat" para abrir o programa.
echo ============================================
pause
