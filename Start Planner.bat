@echo off
title Family Success Planner
cd /d "%~dp0"
echo.
echo   Family Success Planner
echo   Keep this window open while you work.
echo   Your browser will open. That window is the planner.
echo   Close this window when you are finished.
echo.

set PYTHONUNBUFFERED=1

where py >nul 2>&1
if %errorlevel%==0 (
  py -3 planner.py ui
  goto :done
)

where python >nul 2>&1
if %errorlevel%==0 (
  python planner.py ui
  goto :done
)

echo   Python is missing, so the planner cannot start.
echo   Ask whoever shared this folder to install Python from python.org
echo   and tick "Add python.exe to PATH", then double-click this file again.
echo.
pause
exit /b 1

:done
if errorlevel 1 (
  echo.
  echo   The planner did not start. Leave this window open and ask for help.
  pause
)
