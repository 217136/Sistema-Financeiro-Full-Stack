@echo off
echo Iniciando a atualizacao do Banco de Dados (Keep Alive Oracle)
cd /d "%~dp0"

echo Rodando carga_selic...
python carga_selic.py

echo Rodando carga_moedas...
python carga_moedas.py

echo Rodando carga_focus...
python carga_focus.py

echo Atualizacao concluida!

timeout /t 15