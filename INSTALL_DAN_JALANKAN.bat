@echo off
title Rekap Keuangan - Setup
color 0A
echo ============================================
echo   REKAP KEUANGAN - Install dan Jalankan
echo ============================================
echo.
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan!
    echo Install dari: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python ditemukan.
echo [*] Menginstall Flask...
pip install flask --quiet
echo [OK] Flask siap.
echo.
cd /d "%~dp0"
echo [*] Membuka browser...
start "" http://localhost:5000
echo [*] Menjalankan aplikasi...
echo    Akses: http://localhost:5000
echo    Tekan Ctrl+C untuk berhenti
echo.
python app.py
pause