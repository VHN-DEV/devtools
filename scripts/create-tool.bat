@echo off
REM ============================================================
REM Script tạo tool mới - Windows Batch
REM ============================================================

REM Set console to UTF-8
chcp 65001 >nul 2>&1

REM Lấy đường dẫn script hiện tại
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

REM Chạy Python script
python "%SCRIPT_DIR%create-tool.py"

REM Giữ cửa sổ mở nếu có lỗi
if errorlevel 1 (
    echo.
    echo ===============================================
    echo   Co loi xay ra khi tao tool
    echo ===============================================
    pause
)

exit /b %ERRORLEVEL%

