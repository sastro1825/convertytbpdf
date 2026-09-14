@echo off
setlocal enabledelayedexpansion
title RidhoFajar Video to PDF - Frontend Next.js (Port 3000)

cd /d "%~dp0frontend"

echo ================================================================
echo        RIDHOFAJAR VIDEO TO PDF - FRONTEND NEXT.JS
echo ================================================================
echo.

REM 1. Periksa ketersediaan Node.js dan npm
where npm >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js dan npm belum terinstal di sistem.
    echo Unduh Node.js dari https://nodejs.org/
    goto :on_error
)

REM 2. Periksa apakah node_modules sudah terpasang
if not exist "node_modules" (
    echo [INFO] Memasang dependensi frontend (npm install)...
    npm install
    if errorlevel 1 (
        echo [ERROR] Gagal memasang dependensi frontend.
        goto :on_error
    )
)

REM 3. Jalankan server Next.js dev pada port 3000
echo [INFO] Menjalankan frontend Next.js di http://localhost:3000 ...
echo.
npm run dev -- -p 3000
if errorlevel 1 (
    echo.
    echo [ERROR] Terjadi kesalahan pada server frontend.
    goto :on_error
)
goto :end

:on_error
echo.
echo [PERHATIAN] Server frontend berhenti karena error.
pause

:end
