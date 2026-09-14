@echo off
title RidhoFajar Video to PDF - Web Starter

cd /d "%~dp0"

echo ================================================================
echo        RIDHOFAJAR VIDEO TO PDF - LOCAL WEB STARTER
echo ================================================================
echo.
echo [1/3] Menjalankan Backend FastAPI di jendela terpisah (Port 8000)...
start "RidhoFajar Backend (Port 8000)" cmd /k "cd /d ""%~dp0"" && run_backend.bat"

timeout /t 2 /nobreak >nul

echo [2/3] Menjalankan Frontend Next.js di jendela terpisah (Port 3000)...
start "RidhoFajar Frontend (Port 3000)" cmd /k "cd /d ""%~dp0"" && run_frontend.bat"

echo [3/3] Menunggu server siap dan membuka browser...
timeout /t 4 /nobreak >nul

start http://localhost:3000

echo.
echo ================================================================
echo  Aplikasi web lokal sedang berjalan:
echo  - Frontend : http://localhost:3000
echo  - Backend  : http://localhost:8000
echo  - API Docs : http://localhost:8000/docs
echo ================================================================
echo.
echo Jendela ini dapat Anda tutup. Untuk menghentikan aplikasi,
echo tutup jendela terminal Backend dan Frontend yang sedang berjalan.
pause
