@echo off
REM ============================================================
REM DevTools - Batch wrapper để chạy từ bất kỳ đâu
REM ============================================================

REM Set console to UTF-8 to support Vietnamese and emoji
chcp 65001 >nul 2>&1
REM 
REM Mục đích: 
REM   Cho phép chạy DevTools từ bất kỳ thư mục nào
REM   mà không cần cài đặt bằng pip
REM
REM Cách sử dụng:
REM   1. (Khuyến nghị) Đặt file này trong thư mục dự án: scripts/devtools.bat
REM      Chạy: scripts\devtools.bat
REM   2. (Tùy chọn) Copy vào PATH để chạy từ bất kỳ đâu:
REM      - Set biến môi trường DEVTOOLS_DIR
REM      - Hoặc để script tự động tìm trong các thư mục phổ biến
REM
REM Lưu ý:
REM   - Script tự động phát hiện đường dẫn, không cần cấu hình
REM   - Đảm bảo Python đã được thêm vào PATH
REM ============================================================

REM ==================== TỰ ĐỘNG PHÁT HIỆN ĐƯỜNG DẪN ====================
REM Ưu tiên 1: Kiểm tra biến môi trường DEVTOOLS_DIR
if defined DEVTOOLS_DIR (
    if exist "%DEVTOOLS_DIR%\__main__.py" (
        set "TOOL_DIR=%DEVTOOLS_DIR%"
        goto :found
    )
)

REM Ưu tiên 2: Nếu file .bat nằm trong project (scripts/devtools.bat)
REM Lấy đường dẫn thư mục chứa file .bat hiện tại
set "SCRIPT_DIR=%~dp0"
REM Đi lên 1 cấp từ scripts/ lên project root
set "PROJECT_ROOT=%SCRIPT_DIR%.."
REM Chuyển đường dẫn tương đối thành tuyệt đối
for %%I in ("%PROJECT_ROOT%") do set "PROJECT_ROOT=%%~fI"
if exist "%PROJECT_ROOT%\__main__.py" (
    set "TOOL_DIR=%PROJECT_ROOT%"
    goto :found
)

REM Ưu tiên 3: Tìm trong thư mục hiện tại và các thư mục cha
set "CURRENT_DIR=%CD%"
:search_up
if exist "%CURRENT_DIR%\__main__.py" (
    set "TOOL_DIR=%CURRENT_DIR%"
    goto :found
)
REM Đi lên 1 cấp
for %%I in ("%CURRENT_DIR%\..") do set "PARENT_DIR=%%~fI"
if "%PARENT_DIR%"=="%CURRENT_DIR%" goto :not_found
set "CURRENT_DIR=%PARENT_DIR%"
goto :search_up

REM Ưu tiên 4: Thử tìm trong thư mục scripts (nếu file .bat được copy vào PATH)
REM Lấy đường dẫn tuyệt đối của file .bat
for %%I in ("%~f0") do set "BAT_DIR=%%~dpI"
REM Nếu file .bat nằm trong thư mục scripts của project
set "TEST_DIR=%BAT_DIR%.."
for %%I in ("%TEST_DIR%") do set "TEST_DIR=%%~fI"
if exist "%TEST_DIR%\__main__.py" (
    set "TOOL_DIR=%TEST_DIR%"
    goto :found
)

REM Không tìm thấy
:not_found
echo.
echo ===============================================
echo   ERROR: Khong tim thay thu muc DevTools
echo ===============================================
echo.
echo Giai phap:
echo.
echo   Cach 1: Set bien moi truong (khuyen nghi)
echo   ============================================
echo   setx DEVTOOLS_DIR "C:\duong\dan\toi\devtools"
echo   REM Sau do mo cmd moi va chay lai: devtools
echo.
echo   Cach 2: Chay truc tiep tu thu muc project
echo   ============================================
echo   cd C:\duong\dan\toi\devtools
echo   python .
echo.
echo   Cach 3: Cai dat bang pip (khuyen nghi nhat)
echo   ============================================
echo   cd C:\duong\dan\toi\devtools
echo   pip install -e .
echo   REM Sau do chay: devtools (tu bat ky dau)
echo.
echo   Cach 4: Dat file .bat trong thu muc scripts
echo   ============================================
echo   Copy devtools.bat vao: scripts\devtools.bat
echo   Chay: scripts\devtools.bat
echo.
pause
exit /b 1

:found
REM ==================== KIỂM TRA TOOL_DIR ====================
if not exist "%TOOL_DIR%\__main__.py" (
    echo.
    echo ===============================================
    echo   ERROR: Thu muc khong hop le
    echo ===============================================
    echo.
    echo Duong dan: %TOOL_DIR%
    echo Khong tim thay file: __main__.py
    echo.
    pause
    exit /b 1
)

REM Tùy chọn: Chỉ định Python executable cụ thể
REM Bỏ comment và chỉnh sửa nếu cần
REM set "PYTHON_EXE=C:\Python310\python.exe"
REM ===================================================

REM Chạy tool với encoding UTF-8
if defined PYTHON_EXE (
    "%PYTHON_EXE%" -X utf8 "%TOOL_DIR%\__main__.py" %*
) else (
    python -X utf8 "%TOOL_DIR%\__main__.py" %*
)

REM Lưu exit code
set EXIT_CODE=%ERRORLEVEL%

REM Nếu có lỗi, hiển thị thông báo
if %EXIT_CODE% neq 0 (
    echo.
    echo ===============================================
    echo   Co loi xay ra khi chay DevTools
    echo ===============================================
    echo.
    if %EXIT_CODE%==9009 (
        echo Loi: Khong tim thay Python
        echo.
        echo Giai phap:
        echo   1. Kiem tra Python da duoc cai dat chua: python --version
        echo   2. Them Python vao PATH
        echo   3. Hoac chi dinh duong dan Python cu the trong PYTHON_EXE
        echo.
    )
    pause
)

exit /b %EXIT_CODE%

