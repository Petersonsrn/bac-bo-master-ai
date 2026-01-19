@echo off
title UPLOAD PARA GITHUB - BAC BO MASTER
color 0A

echo ========================================================
echo      ENVIANDO PROJETO PARA SEU GITHUB PESSOAL
echo ========================================================
echo.
echo 1. Va no site github.com e crie um NOVO repositorio.
echo 2. Copie o link HTTPS dele (ex: https://github.com/user/repo.git)
echo.
set /p REPO_URL="Cole o LINK do Repositorio aqui: "

if "%REPO_URL%"=="" goto error

echo.
echo [1/3] Configurando remoto...
git remote remove origin
git remote add origin %REPO_URL%

echo [2/3] Definindo branch Principal...
git branch -M main

echo [3/3] Enviando arquivos...
git push -u origin main

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha ao enviar! Verifique se o link esta correto.
    pause
    exit /b
)

echo.
echo [SUCESSO] Projeto enviado com sucesso para o GitHub! 🚀
pause
exit /b

:error
echo Voce nao colou o link!
pause
