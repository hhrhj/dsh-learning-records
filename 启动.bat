@echo off
title DSH Learning Records
cd /d "%~dp0"

echo ============================================
echo   DSH Learning Records
echo ============================================
echo.

set "PYEXE="

rem --- 1) try "python" on PATH ---
where python >nul 2>nul
if not errorlevel 1 (
  for /f "delims=" %%i in ('where python') do (
    set "PYEXE=%%i"
    goto :found
  )
)

rem --- 2) try "py" launcher ---
where py >nul 2>nul
if not errorlevel 1 (
  set "PYEXE=py"
  goto :found
)

rem --- 3) common install locations ---
for %%p in (
  "D:\Python\python.exe"
  "C:\Python312\python.exe"
  "C:\Python311\python.exe"
  "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
  "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
  "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
  "%ProgramFiles%\Python312\python.exe"
) do (
  if exist %%p (
    set "PYEXE=%%~p"
    goto :found
  )
)

echo [ERROR] Python not found on this computer.
echo.
echo Please install Python 3 from https://www.python.org/downloads/
echo During install, check "Add Python to PATH".
echo.
pause
exit /b 1

:found
echo   Using Python: %PYEXE%
echo.
echo   Server starting, keep this window OPEN.
echo.
echo   Open in browser:  http://127.0.0.1:8765/
echo.
echo ============================================
echo.

%PYEXE% server.py

echo.
echo Server stopped. Press any key to close.
pause
