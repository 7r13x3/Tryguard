@echo off
echo =========================================
echo Building TryGuard Executable...
echo =========================================

:: Install PyInstaller if not already installed
pip install pyinstaller

:: Build the EXE
pyinstaller --noconsole --onefile --name="TryGuard" tryguard.py

echo.
echo =========================================
echo Build Complete! 
echo Check the "dist" folder for TryGuard.exe
echo =========================================
pause
