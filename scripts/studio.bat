@echo off
REM Cine Studio launcher — double-click or run from cmd.
REM Opens the interactive terminal UI for the cinematography skill.
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py studio.py
) else (
  python studio.py
)
echo.
pause
