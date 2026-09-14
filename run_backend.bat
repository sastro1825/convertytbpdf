@echo off
setlocal enabledelayedexpansion
title RidhoFajar Video to PDF - Backend Server (Port 8000)

cd /d "%~dp0backend"

echo ================================================================
echo        RIDHOFAJAR VIDEO TO PDF - FASTAPI BACKEND
echo ================================================================
echo.

REM 1. Periksa ketersediaan Python
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python belum terinstal di sistem.
    echo Unduh Python dari https://www.python.org/downloads/
    goto :on_error
)

REM 2. Tentukan virtual environment (gunakan .venv utama atau backend)
set "VENV_PYTHON=..\.venv\Scripts\python.exe"
if not exist "!VENV_PYTHON!" (
    set "VENV_PYTHON=.venv\Scripts\python.exe"
)

if not exist "!VENV_PYTHON!" (
    echo [INFO] Menyiapkan virtual environment Python...
    python -m venv .venv
    .venv\Scripts\pip install -r requirements.txt
    set "VENV_PYTHON=.venv\Scripts\python.exe"
)

REM 3. Jalankan server FastAPI Uvicorn pada port 8000
echo [INFO] Menjalankan server backend di http://localhost:8000 ...
echo [INFO] Dokumentasi Swagger API: http://localhost:8000/docs
echo.
"!VENV_PYTHON!" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
if errorlevel 1 (
    echo.
    echo [ERROR] Terjadi kesalahan pada server backend.
    goto :on_error
)
goto :end

:on_error
echo.
echo [PERHATIAN] Server backend berhenti karena error.
pause

:end
